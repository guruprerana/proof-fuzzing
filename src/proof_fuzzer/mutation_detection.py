"""Detect and adjudicate proof mutations from stored fuzzing attempts."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
import time
from typing import Iterable

from src.proof_fuzzer.evolution import truncate_text_head_tail
from src.proof_fuzzer.llm_interface import LLMClient
from src.proof_fuzzer.reporting import write_mutation_detection_examples
from src.proof_fuzzer.vllm_client import (
    DEFAULT_BASE_URL,
    GPT_OSS_120B,
    VLLMProofFuzzerClient,
)


DETECTION_CONDITIONS = {"blind", "mutation_aware"}


@dataclass(frozen=True)
class MutationDetectionExperimentConfig:
    """Configuration for mutation-detection experiments over fuzzing attempts."""

    source_run_dir: str | Path
    output_dir: str | Path | None = None
    target_attempts: int = 1000
    wait_for_target_attempts: bool = True
    poll_interval_seconds: float = 60.0
    max_workers: int = 4
    reasoning_effort: str = "high"
    temperature: float = 0.0
    max_tokens: int = 16_000
    base_url: str = DEFAULT_BASE_URL
    model: str = GPT_OSS_120B
    max_problem_chars: int = 2_000
    max_rubric_chars: int = 3_000
    max_proof_chars: int = 8_000
    include_unsuccessful_completed_mutations: bool = True


@dataclass(frozen=True)
class MutationDetectionExperimentResult:
    """Summary for a mutation-detection experiment."""

    output_dir: Path
    source_run_dir: Path
    attempts_available: int
    attempts_selected: int
    result_rows: int

    def summary(self) -> str:
        return (
            f"Mutation detection experiment wrote {self.result_rows} rows for "
            f"{self.attempts_selected} attempts to {self.output_dir}"
        )


def run_mutation_detection_experiment(
    config: MutationDetectionExperimentConfig,
    *,
    detector_llm: LLMClient | None = None,
    adjudicator_llm: LLMClient | None = None,
) -> MutationDetectionExperimentResult:
    """Run blind and mutation-aware detection over stored fuzzing attempts."""

    source_run_dir = Path(config.source_run_dir)
    output_dir = Path(config.output_dir) if config.output_dir is not None else source_run_dir / "mutation_detection_experiment"
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = output_dir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)
    _write_config(output_dir, config)

    attempts = wait_for_attempts(
        source_run_dir,
        target_attempts=config.target_attempts,
        wait=config.wait_for_target_attempts,
        poll_interval_seconds=config.poll_interval_seconds,
    )
    selected_attempts = select_detection_attempts(
        attempts,
        include_unsuccessful_completed_mutations=config.include_unsuccessful_completed_mutations,
    )

    detector = detector_llm or VLLMProofFuzzerClient(
        base_url=config.base_url,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    adjudicator = adjudicator_llm or detector

    results_path = output_dir / "detection_results.jsonl"
    completed_keys = _load_completed_detection_keys(results_path)
    lock = threading.Lock()
    rows_written = 0

    tasks = [
        (attempt, condition)
        for attempt in selected_attempts
        for condition in sorted(DETECTION_CONDITIONS)
        if (str(attempt.get("attempt_id", "")), condition) not in completed_keys
    ]

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {
            executor.submit(
                _run_one_detection,
                attempt,
                condition=condition,
                config=config,
                detector_llm=detector,
                adjudicator_llm=adjudicator,
                trace_dir=trace_dir,
            ): (attempt, condition)
            for attempt, condition in tasks
        }
        for future in as_completed(futures):
            row = future.result()
            with lock:
                with results_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")
                rows_written += 1

    rows = _load_detection_rows(results_path)
    write_detection_summary(
        output_dir=output_dir,
        source_run_dir=source_run_dir,
        attempts=selected_attempts,
        rows=rows,
        attempts_available=len(attempts),
    )
    write_mutation_detection_examples(source_run_dir)
    return MutationDetectionExperimentResult(
        output_dir=output_dir,
        source_run_dir=source_run_dir,
        attempts_available=len(attempts),
        attempts_selected=len(selected_attempts),
        result_rows=len(rows),
    )


def wait_for_attempts(
    source_run_dir: str | Path,
    *,
    target_attempts: int,
    wait: bool,
    poll_interval_seconds: float,
) -> list[dict[str, object]]:
    """Load attempts, optionally polling until a target count is available."""

    path = Path(source_run_dir) / "attempts.jsonl"
    while True:
        attempts = _load_attempts(path)
        if not wait or len(attempts) >= target_attempts:
            return attempts
        time.sleep(poll_interval_seconds)


def select_detection_attempts(
    attempts: Iterable[dict[str, object]],
    *,
    include_unsuccessful_completed_mutations: bool = True,
) -> list[dict[str, object]]:
    """Select completed attempts with at least one mutation instruction."""

    selected = []
    for attempt in attempts:
        if attempt.get("status") != "success":
            continue
        if not include_unsuccessful_completed_mutations and not attempt.get("success"):
            continue
        instructions = attempt.get("mutation_instructions")
        if not isinstance(instructions, dict) or not instructions.get("mutations"):
            continue
        selected.append(attempt)
    return selected


def blind_detection_prompt(
    attempt: dict[str, object],
    *,
    max_problem_chars: int,
    max_rubric_chars: int,
    max_proof_chars: int,
) -> str:
    """Prompt that does not reveal that a mutation exists."""

    metadata = _metadata(attempt)
    return f"""You are grading a submitted mathematical proof.

Problem:
```text
{truncate_text_head_tail(str(metadata.get("problem", "")), max_problem_chars)}
```

Rubric:
```text
{truncate_text_head_tail(str(metadata.get("rubric", "")), max_rubric_chars)}
```

Submitted proof:
```text
{truncate_text_head_tail(str(attempt.get("mutated_proof_text", "")), max_proof_chars)}
```

Decide whether the proof is mathematically correct. If it is incorrect, identify the most important flaw precisely.
Return exactly one JSON object and no prose outside JSON.
Schema:
```json
{{
  "verdict": "correct | incorrect | uncertain",
  "detected_flaw": "specific flaw, or empty if none",
  "flaw_location": "where in the proof the flaw occurs, if identifiable",
  "confidence": 0.0,
  "rationale": "brief justification"
}}
```
"""


def mutation_aware_detection_prompt(
    attempt: dict[str, object],
    *,
    max_problem_chars: int,
    max_rubric_chars: int,
    max_proof_chars: int,
) -> str:
    """Prompt that explicitly reveals that an introduced mutation/error exists."""

    metadata = _metadata(attempt)
    return f"""You are analyzing a mathematical proof that contains an introduced mutation/error.

Your task is to identify the specific introduced error. Be precise: name the incorrect step, missing condition, invalid inference, or altered dependency.

Problem:
```text
{truncate_text_head_tail(str(metadata.get("problem", "")), max_problem_chars)}
```

Rubric:
```text
{truncate_text_head_tail(str(metadata.get("rubric", "")), max_rubric_chars)}
```

Mutated proof:
```text
{truncate_text_head_tail(str(attempt.get("mutated_proof_text", "")), max_proof_chars)}
```

Return exactly one JSON object and no prose outside JSON.
Schema:
```json
{{
  "verdict": "incorrect | uncertain",
  "detected_flaw": "specific introduced error",
  "flaw_location": "where in the proof the introduced error occurs, if identifiable",
  "confidence": 0.0,
  "rationale": "brief justification"
}}
```
"""


def adjudication_prompt(
    attempt: dict[str, object],
    *,
    condition: str,
    detection_response: str,
) -> str:
    """Prompt comparing a detection response to the known mutation."""

    instructions = attempt.get("mutation_instructions", {})
    known = {
        "rationale": instructions.get("rationale") if isinstance(instructions, dict) else "",
        "mutations": instructions.get("mutations") if isinstance(instructions, dict) else [],
        "mutation_check_detected_flaw": (
            attempt.get("mutation_check_result", {}).get("detected_flaw")
            if isinstance(attempt.get("mutation_check_result"), dict)
            else ""
        ),
    }
    return f"""You are scoring whether a model detected the known introduced proof error.

Detection condition: {condition}

Known introduced mutation:
```json
{json.dumps(known, indent=2, sort_keys=True)}
```

Model detection response:
```text
{detection_response}
```

Judge whether the detection response identifies the same mathematical error as the known mutation. Semantic matches count even if wording differs.
Return exactly one JSON object and no prose outside JSON.
Schema:
```json
{{
  "detected_correct_error": true,
  "match_level": "exact | partial | related | wrong | no_flaw",
  "specificity": 0.0,
  "localization": 0.0,
  "rationale": "brief explanation"
}}
```
"""


def write_detection_summary(
    *,
    output_dir: Path,
    source_run_dir: Path,
    attempts: list[dict[str, object]],
    rows: list[dict[str, object]],
    attempts_available: int,
) -> None:
    """Write JSON and Markdown summaries for detection results."""

    attempt_by_id = {str(attempt.get("attempt_id", "")): attempt for attempt in attempts}
    summary = _summarize_detection_rows(rows, attempt_by_id)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_run_dir": str(source_run_dir),
        "attempts_available": attempts_available,
        "attempts_selected": len(attempts),
        "rows": len(rows),
        "summary": summary,
    }
    (output_dir / "detection_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "detection_summary.md").write_text(
        _summary_markdown(payload),
        encoding="utf-8",
    )


def _run_one_detection(
    attempt: dict[str, object],
    *,
    condition: str,
    config: MutationDetectionExperimentConfig,
    detector_llm: LLMClient,
    adjudicator_llm: LLMClient,
    trace_dir: Path,
) -> dict[str, object]:
    attempt_id = str(attempt.get("attempt_id", ""))
    if condition == "blind":
        prompt = blind_detection_prompt(
            attempt,
            max_problem_chars=config.max_problem_chars,
            max_rubric_chars=config.max_rubric_chars,
            max_proof_chars=config.max_proof_chars,
        )
    elif condition == "mutation_aware":
        prompt = mutation_aware_detection_prompt(
            attempt,
            max_problem_chars=config.max_problem_chars,
            max_rubric_chars=config.max_rubric_chars,
            max_proof_chars=config.max_proof_chars,
        )
    else:
        raise ValueError(f"Unknown detection condition: {condition}")

    detection_response = detector_llm.complete(prompt)
    detection_json, detection_parse_error = _try_load_json_object(detection_response)

    adjudicator = adjudication_prompt(
        attempt,
        condition=condition,
        detection_response=detection_response,
    )
    adjudication_response = adjudicator_llm.complete(adjudicator)
    adjudication_json, adjudication_parse_error = _try_load_json_object(adjudication_response)

    trace_path = trace_dir / f"{attempt_id}_{condition}.json"
    trace = {
        "attempt_id": attempt_id,
        "condition": condition,
        "detection_prompt": prompt,
        "detection_response": detection_response,
        "adjudication_prompt": adjudicator,
        "adjudication_response": adjudication_response,
    }
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "attempt_id": attempt_id,
        "condition": condition,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": _result_metadata(attempt),
        "detection": detection_json,
        "detection_parse_error": detection_parse_error,
        "adjudication": adjudication_json,
        "adjudication_parse_error": adjudication_parse_error,
        "trace_file": str(trace_path.relative_to(trace_dir.parent)),
    }


def _result_metadata(attempt: dict[str, object]) -> dict[str, object]:
    metadata = _metadata(attempt)
    sources = metadata.get("strategy_selection", {}).get("selected_strategy_sources", [])
    math_topic = metadata.get("math_topic") or metadata.get("llm_category") or metadata.get("topic") or ""
    return {
        "example_id": metadata.get("example_id", ""),
        "sample_index": metadata.get("sample_index", ""),
        "llm_category": metadata.get("llm_category", ""),
        "math_topic": math_topic,
        "fuzz_success": bool(attempt.get("success")),
        "strategy_ids": list(attempt.get("strategy_ids", [])),
        "strategy_sources": list(sources) if isinstance(sources, list) else [],
    }


def _summarize_detection_rows(
    rows: list[dict[str, object]],
    attempt_by_id: dict[str, dict[str, object]],
) -> dict[str, object]:
    by_condition = {}
    for condition in sorted(DETECTION_CONDITIONS):
        condition_rows = [row for row in rows if row.get("condition") == condition]
        by_condition[condition] = _row_rate(condition_rows)

    by_topic = {}
    topics = sorted({str(row.get("metadata", {}).get("math_topic", "")) for row in rows})
    for topic in topics:
        by_topic[topic or "unknown"] = {
            condition: _row_rate(
                [
                    row for row in rows
                    if row.get("condition") == condition
                    and str(row.get("metadata", {}).get("math_topic", "")) == topic
                ]
            )
            for condition in sorted(DETECTION_CONDITIONS)
        }

    by_guidance = {}
    for bucket in ("guided", "unguided"):
        by_guidance[bucket] = {
            condition: _row_rate(
                [
                    row for row in rows
                    if row.get("condition") == condition
                    and _guidance_bucket(row) == bucket
                ]
            )
            for condition in sorted(DETECTION_CONDITIONS)
        }

    by_fuzz_success = {}
    for bucket in ("fuzz_success", "fuzz_failure"):
        expected = bucket == "fuzz_success"
        by_fuzz_success[bucket] = {
            condition: _row_rate(
                [
                    row for row in rows
                    if row.get("condition") == condition
                    and bool(row.get("metadata", {}).get("fuzz_success")) == expected
                ]
            )
            for condition in sorted(DETECTION_CONDITIONS)
        }

    return {
        "by_condition": by_condition,
        "by_topic": by_topic,
        "by_guidance": by_guidance,
        "by_fuzz_success": by_fuzz_success,
        "attempt_ids": sorted(attempt_by_id),
    }


def _row_rate(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    correct = sum(
        1 for row in rows
        if bool(row.get("adjudication", {}).get("detected_correct_error"))
    )
    parse_errors = sum(
        1 for row in rows
        if row.get("detection_parse_error") or row.get("adjudication_parse_error")
    )
    match_levels = {}
    for row in rows:
        level = str(row.get("adjudication", {}).get("match_level", ""))
        if level:
            match_levels[level] = match_levels.get(level, 0) + 1
    return {
        "correct": correct,
        "total": total,
        "rate": correct / total if total else 0.0,
        "parse_errors": parse_errors,
        "match_levels": match_levels,
    }


def _summary_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = [
        "# Mutation Detection Experiment Summary",
        "",
        f"Generated: {payload['created_at']}",
        f"Source run: `{payload['source_run_dir']}`",
        f"Attempts available: **{payload['attempts_available']}**",
        f"Attempts selected: **{payload['attempts_selected']}**",
        f"Result rows: **{payload['rows']}**",
        "",
        "## Overall",
        "",
        "| Condition | Correct detections | Rate | Parse errors |",
        "|---|---:|---:|---:|",
    ]
    for condition, row in summary["by_condition"].items():
        lines.append(
            f"| {condition} | {row['correct']}/{row['total']} | {row['rate']:.1%} | {row['parse_errors']} |"
        )
    lines.extend(["", "## By Topic", "", "| Topic | Blind | Mutation-aware |", "|---|---:|---:|"])
    for topic, rows in summary["by_topic"].items():
        blind = rows.get("blind", {})
        aware = rows.get("mutation_aware", {})
        lines.append(
            f"| {topic} | {blind.get('correct', 0)}/{blind.get('total', 0)} ({blind.get('rate', 0):.1%}) | "
            f"{aware.get('correct', 0)}/{aware.get('total', 0)} ({aware.get('rate', 0):.1%}) |"
        )
    lines.extend(["", "## By Guidance", "", "| Bucket | Blind | Mutation-aware |", "|---|---:|---:|"])
    for bucket, rows in summary["by_guidance"].items():
        blind = rows.get("blind", {})
        aware = rows.get("mutation_aware", {})
        lines.append(
            f"| {bucket} | {blind.get('correct', 0)}/{blind.get('total', 0)} ({blind.get('rate', 0):.1%}) | "
            f"{aware.get('correct', 0)}/{aware.get('total', 0)} ({aware.get('rate', 0):.1%}) |"
        )
    lines.extend(["", "## By Fuzz Success", "", "| Bucket | Blind | Mutation-aware |", "|---|---:|---:|"])
    for bucket, rows in summary["by_fuzz_success"].items():
        blind = rows.get("blind", {})
        aware = rows.get("mutation_aware", {})
        lines.append(
            f"| {bucket} | {blind.get('correct', 0)}/{blind.get('total', 0)} ({blind.get('rate', 0):.1%}) | "
            f"{aware.get('correct', 0)}/{aware.get('total', 0)} ({aware.get('rate', 0):.1%}) |"
        )
    lines.append("")
    return "\n".join(lines)


def _guidance_bucket(row: dict[str, object]) -> str:
    return "guided" if row.get("metadata", {}).get("strategy_ids") else "unguided"


def _metadata(attempt: dict[str, object]) -> dict[str, object]:
    metadata = attempt.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _load_attempts(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_detection_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_completed_detection_keys(path: Path) -> set[tuple[str, str]]:
    return {
        (str(row.get("attempt_id", "")), str(row.get("condition", "")))
        for row in _load_detection_rows(path)
    }


def _try_load_json_object(text: str) -> tuple[dict[str, object], str]:
    try:
        candidate = _extract_json_candidate(text)
        data = json.loads(candidate)
        if isinstance(data, dict):
            return data, ""
        return {}, "response JSON was not an object"
    except Exception as exc:
        return {}, repr(exc)


def _extract_json_candidate(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object was found.")
    return text[start:end + 1]


def _write_config(output_dir: Path, config: MutationDetectionExperimentConfig) -> None:
    data = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in asdict(config).items()
    }
    (output_dir / "detection_config.json").write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )
