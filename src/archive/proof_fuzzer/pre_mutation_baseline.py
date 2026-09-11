"""Replay blind judging on original proofs from successful fuzzing attempts."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
from typing import Protocol

from .evolution import BlindProofCorrectnessJudge, parse_judge_result, truncate_text_head_tail
from src.proof_fuzzer.gemini_client import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    GeminiChatResult,
    GeminiProofFuzzerClient,
)
from .judge_prompt_robustness import select_successful_false_proof_attempts


class _ReasoningLLM(Protocol):
    def complete_with_reasoning(self, prompt: str) -> GeminiChatResult:
        ...


@dataclass(frozen=True)
class PreMutationBaselineJudgeConfig:
    """Configuration for replaying successful attacks on their original proofs."""

    source_run_dir: str | Path
    output_dir: str | Path | None = None
    max_workers: int = 4
    model: str = DEFAULT_GEMINI_MODEL
    thinking_level: str = DEFAULT_GEMINI_THINKING_LEVEL
    temperature: float = 0.0
    max_tokens: int = 32_000
    max_problem_chars: int = 4_000
    max_proof_chars: int = 24_000
    limit: int | None = None


@dataclass(frozen=True)
class PreMutationBaselineJudgeResult:
    """Summary for a pre-mutation baseline replay."""

    output_dir: Path
    source_run_dir: Path
    attempts_available: int
    attempts_selected: int
    result_rows: int

    def summary(self) -> str:
        return (
            f"Pre-mutation baseline judged {self.result_rows}/{self.attempts_selected} "
            f"successful false-proof attacks; output={self.output_dir}"
        )


class GeminiThreadLocalLLM:
    """Thread-local Gemini client wrapper for concurrent baseline replay jobs."""

    def __init__(
        self,
        *,
        model: str,
        thinking_level: str,
        temperature: float,
        max_tokens: int,
    ):
        self.model = model
        self.thinking_level = thinking_level
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._local = threading.local()

    def complete_with_reasoning(self, prompt: str) -> GeminiChatResult:
        return self._client().complete_with_reasoning(prompt)

    def _client(self) -> GeminiProofFuzzerClient:
        client = getattr(self._local, "client", None)
        if client is None:
            client = GeminiProofFuzzerClient(
                model=self.model,
                thinking_level=self.thinking_level,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            self._local.client = client
        return client


def run_pre_mutation_baseline_judge(
    config: PreMutationBaselineJudgeConfig,
    *,
    judge_llm: _ReasoningLLM | None = None,
) -> PreMutationBaselineJudgeResult:
    """Run the blind judge on original proofs from successful false-proof attacks."""

    source_run_dir = Path(config.source_run_dir)
    output_dir = (
        Path(config.output_dir)
        if config.output_dir is not None
        else source_run_dir / "pre_mutation_baseline_judge"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = output_dir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)
    _write_config(output_dir, config)

    attempts = _load_jsonl(source_run_dir / "attempts.jsonl")
    selected_attempts = select_successful_false_proof_attempts(attempts, limit=config.limit)
    llm = judge_llm or GeminiThreadLocalLLM(
        model=config.model,
        thinking_level=config.thinking_level,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    results_path = output_dir / "pre_mutation_baseline_judge_results.jsonl"
    completed = _load_completed_attempt_ids(results_path)
    tasks = [
        (index, attempt)
        for index, attempt in enumerate(selected_attempts, start=1)
        if str(attempt.get("attempt_id", "")) not in completed
    ]
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {
            executor.submit(
                _run_one_baseline_check,
                attempt,
                row_index=index,
                config=config,
                judge_llm=llm,
                trace_root=trace_dir,
            ): attempt
            for index, attempt in tasks
        }
        for future in as_completed(futures):
            row = future.result()
            with lock:
                with results_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")

    rows = _load_jsonl(results_path)
    write_pre_mutation_baseline_summary(
        output_dir=output_dir,
        source_run_dir=source_run_dir,
        attempts=selected_attempts,
        rows=rows,
        attempts_available=len(attempts),
    )
    return PreMutationBaselineJudgeResult(
        output_dir=output_dir,
        source_run_dir=source_run_dir,
        attempts_available=len(attempts),
        attempts_selected=len(selected_attempts),
        result_rows=len(rows),
    )


def pre_mutation_blind_judge_prompt(
    attempt: dict[str, object],
    *,
    max_problem_chars: int,
    max_proof_chars: int,
) -> str:
    """Build the blind judge prompt for the original unmutated proof."""

    metadata = _metadata(attempt)
    problem = truncate_text_head_tail(str(metadata.get("problem", "")), max_problem_chars)
    proof = truncate_text_head_tail(str(attempt.get("original_proof_text", "")), max_proof_chars)
    return BlindProofCorrectnessJudge(_NoopLLM()).judge_prompt(
        problem_text=problem,
        proof_text=proof,
        fuzzer_kind=str(attempt.get("fuzzer_kind", "natural_language")),
    )


def write_pre_mutation_baseline_summary(
    *,
    output_dir: Path,
    source_run_dir: Path,
    attempts: list[dict[str, object]],
    rows: list[dict[str, object]],
    attempts_available: int,
) -> None:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_run_dir": str(source_run_dir),
        "attempts_available": attempts_available,
        "attempts_selected": len(attempts),
        "rows": len(rows),
        "summary": _summarize_rows(rows),
    }
    (output_dir / "pre_mutation_baseline_judge_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "pre_mutation_baseline_judge_summary.md").write_text(
        _summary_markdown(payload),
        encoding="utf-8",
    )


def _run_one_baseline_check(
    attempt: dict[str, object],
    *,
    row_index: int,
    config: PreMutationBaselineJudgeConfig,
    judge_llm: _ReasoningLLM,
    trace_root: Path,
) -> dict[str, object]:
    prompt = pre_mutation_blind_judge_prompt(
        attempt,
        max_problem_chars=config.max_problem_chars,
        max_proof_chars=config.max_proof_chars,
    )
    completion = judge_llm.complete_with_reasoning(prompt)
    parsed = parse_judge_result(completion.content)
    row = {
        "row_index": row_index,
        "attempt_id": str(attempt.get("attempt_id", "")),
        "source_trace_dir": _metadata(attempt).get("trace_dir", ""),
        "metadata": _result_metadata(attempt),
        "pre_mutation_baseline_judge": parsed.to_dict(),
        "baseline_judged_original_correct": parsed.verdict == "correct",
        "original_run_pre_mutation_judge": attempt.get("pre_mutation_judge_result"),
    }
    _write_trace(
        trace_root=trace_root,
        attempt=attempt,
        row=row,
        prompt=prompt,
        completion=completion,
    )
    return row


def _write_trace(
    *,
    trace_root: Path,
    attempt: dict[str, object],
    row: dict[str, object],
    prompt: str,
    completion: GeminiChatResult,
) -> None:
    trace_dir = trace_root / _trace_name(attempt, row)
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "01_pre_mutation_blind_judge_prompt.txt").write_text(prompt, encoding="utf-8")
    (trace_dir / "02_pre_mutation_blind_judge_response.txt").write_text(
        completion.content,
        encoding="utf-8",
    )
    (trace_dir / "02_pre_mutation_blind_judge_reasoning.txt").write_text(
        completion.reasoning,
        encoding="utf-8",
    )
    (trace_dir / "original_proof.txt").write_text(
        str(attempt.get("original_proof_text", "")),
        encoding="utf-8",
    )
    (trace_dir / "row.json").write_text(json.dumps(row, indent=2, sort_keys=True), encoding="utf-8")


def _summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    topics = sorted({str(row.get("metadata", {}).get("math_topic", "")) for row in rows})
    return {
        "overall": _row_counts(rows),
        "by_topic": {
            topic or "unknown": _row_counts(
                [row for row in rows if str(row.get("metadata", {}).get("math_topic", "")) == topic]
            )
            for topic in topics
        },
        "by_guidance": {
            bucket: _row_counts([row for row in rows if _guidance_bucket(row) == bucket])
            for bucket in ("guided", "unguided")
        },
        "by_strategy_source": _summarize_by_strategy_source(rows),
    }


def _row_counts(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("pre_mutation_baseline_judge", {}).get("verdict") == "correct")
    verdicts: dict[str, int] = {}
    for row in rows:
        verdict = str(row.get("pre_mutation_baseline_judge", {}).get("verdict", ""))
        if verdict:
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
    return {
        "total": total,
        "original_judged_correct": correct,
        "original_judged_correct_rate": correct / total if total else 0.0,
        "verdicts": verdicts,
    }


def _summarize_by_strategy_source(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    buckets = {}
    for source in sorted({source for row in rows for source in row.get("metadata", {}).get("strategy_sources", [])}):
        buckets[source] = _row_counts(
            [row for row in rows if source in row.get("metadata", {}).get("strategy_sources", [])]
        )
    buckets["no_strategy"] = _row_counts(
        [row for row in rows if not row.get("metadata", {}).get("strategy_ids")]
    )
    return buckets


def _summary_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = [
        "# Pre-Mutation Baseline Judge",
        "",
        f"Generated: {payload['created_at']}",
        f"Source run: `{payload['source_run_dir']}`",
        f"Attempts available: **{payload['attempts_available']}**",
        f"Successful false-proof attacks selected: **{payload['attempts_selected']}**",
        f"Result rows: **{payload['rows']}**",
        "",
        "This replays the same blind correctness judge prompt on each successful attack's original proof.",
        "",
        "## Overall",
        "",
        "| Total | Original judged correct | Verdicts |",
        "|---:|---:|---|",
        _counts_row(summary["overall"]),
        "",
        "## By Topic",
        "",
        "| Topic | Total | Original judged correct | Verdicts |",
        "|---|---:|---:|---|",
    ]
    for topic, counts in summary["by_topic"].items():
        lines.append(_counts_row(counts, label=topic))
    lines.extend([
        "",
        "## By Guidance",
        "",
        "| Bucket | Total | Original judged correct | Verdicts |",
        "|---|---:|---:|---|",
    ])
    for bucket, counts in summary["by_guidance"].items():
        lines.append(_counts_row(counts, label=bucket))
    lines.extend([
        "",
        "## By Strategy Source",
        "",
        "| Source | Total | Original judged correct | Verdicts |",
        "|---|---:|---:|---|",
    ])
    for source, counts in summary["by_strategy_source"].items():
        lines.append(_counts_row(counts, label=source))
    lines.append("")
    return "\n".join(lines)


def _counts_row(counts: dict[str, object], *, label: str | None = None) -> str:
    total = int(counts.get("total", 0))
    correct = int(counts.get("original_judged_correct", 0))
    correct_cell = f"{correct}/{total} ({float(counts.get('original_judged_correct_rate', 0.0)):.1%})"
    verdicts = _format_counts(counts.get("verdicts", {}))
    if label is None:
        return f"| {total} | {correct_cell} | {verdicts} |"
    return f"| {label} | {total} | {correct_cell} | {verdicts} |"


def _result_metadata(attempt: dict[str, object]) -> dict[str, object]:
    metadata = _metadata(attempt)
    selection = metadata.get("strategy_selection", {})
    sources = selection.get("selected_strategy_sources", []) if isinstance(selection, dict) else []
    math_topic = metadata.get("math_topic") or metadata.get("llm_category") or metadata.get("topic") or ""
    return {
        "example_id": metadata.get("example_id", ""),
        "sample_index": metadata.get("sample_index", ""),
        "trace_dir_name": metadata.get("trace_dir_name", ""),
        "llm_category": metadata.get("llm_category", ""),
        "math_topic": math_topic,
        "strategy_ids": list(attempt.get("strategy_ids", [])),
        "strategy_sources": list(sources) if isinstance(sources, list) else [],
    }


def _guidance_bucket(row: dict[str, object]) -> str:
    return "guided" if row.get("metadata", {}).get("strategy_ids") else "unguided"


def _trace_name(attempt: dict[str, object], row: dict[str, object]) -> str:
    metadata = _metadata(attempt)
    trace_dir_name = str(metadata.get("trace_dir_name", "")).strip()
    return trace_dir_name or str(row.get("row_index", "")) or str(attempt.get("attempt_id", ""))


def _metadata(attempt: dict[str, object]) -> dict[str, object]:
    metadata = attempt.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _format_counts(counts: object) -> str:
    if not isinstance(counts, dict) or not counts:
        return ""
    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_completed_attempt_ids(path: Path) -> set[str]:
    return {str(row.get("attempt_id", "")) for row in _load_jsonl(path)}


def _write_config(output_dir: Path, config: PreMutationBaselineJudgeConfig) -> None:
    data = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in asdict(config).items()
    }
    (output_dir / "pre_mutation_baseline_judge_config.json").write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )


class _NoopLLM:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError(prompt)
