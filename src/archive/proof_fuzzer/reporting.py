"""Markdown reports for proof-fuzzer runs."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import re


SELF_LABEL_RE = re.compile(r"\b(incorrectly|incorrect|invalid|false|wrong|flaw|mistake|omitted)\b", re.I)


def write_standard_source_reports(run_dir: str | Path) -> None:
    """Write summary and successful-example markdown files for a fuzzing run."""

    root = Path(run_dir)
    attempts = _load_jsonl(root / "attempts.jsonl")
    if not attempts:
        return
    strategy_titles = _load_strategy_titles(root)
    _write_trace_mapping(root, attempts)
    id_to_simple = _load_simple_attempt_ids(root)
    _write_source_summary(root, attempts)
    _write_successful_examples(root, attempts, strategy_titles, id_to_simple)


def write_mutation_detection_examples(run_dir: str | Path) -> None:
    """Write representative blind-vs-mutation-aware detection examples."""

    root = Path(run_dir)
    detection_dir = root / "mutation_detection_experiment"
    attempts = _load_jsonl(root / "attempts.jsonl")
    rows = _load_jsonl(detection_dir / "detection_results.jsonl")
    if not attempts or not rows:
        return

    by_attempt = {str(attempt.get("attempt_id", "")): attempt for attempt in attempts}
    id_to_simple = _load_simple_attempt_ids(root)
    paired: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        paired[str(row.get("attempt_id", ""))][str(row.get("condition", ""))] = row

    counts = Counter()
    candidates: dict[tuple[bool, bool], list[tuple[tuple[int, int, int], str]]] = defaultdict(list)
    for attempt_id, pair in paired.items():
        if "blind" not in pair or "mutation_aware" not in pair or attempt_id not in by_attempt:
            continue
        blind_detected = _detected(pair["blind"])
        aware_detected = _detected(pair["mutation_aware"])
        counts[(blind_detected, aware_detected)] += 1
        attempt = by_attempt[attempt_id]
        if SELF_LABEL_RE.search(str(attempt.get("mutated_proof_text", ""))):
            continue
        changed = _diff_changed_lines(attempt)
        mutation_count = len(_mutations(attempt))
        rank = (1 if attempt.get("success") else 0, changed + 8 * mutation_count, changed)
        candidates[(blind_detected, aware_detected)].append((rank, attempt_id))

    examples = [
        ("Detected both with and without mutation hint", (True, True)),
        ("Missed without hint, detected with mutation hint", (False, True)),
        ("Missed both with and without mutation hint", (False, False)),
        ("Detected without hint, missed with mutation hint", (True, False)),
    ]

    lines = [
        "# Mutation Detection Examples",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Run directory: `{root}`",
        f"Detection experiment: `{detection_dir}`",
        "",
        "This report compares the same mutated proof under a blind detector prompt and a mutation-aware detector prompt.",
        "",
        "## Outcome Counts",
        "",
        "| Blind prompt | Mutation-aware prompt | Attempts |",
        "|---|---|---:|",
        f"| detected | detected | {counts[(True, True)]} |",
        f"| not detected | detected | {counts[(False, True)]} |",
        f"| not detected | not detected | {counts[(False, False)]} |",
        f"| detected | not detected | {counts[(True, False)]} |",
        "",
        "## Examples",
        "",
    ]
    for title, pattern in examples:
        choices = sorted(candidates.get(pattern, ()), key=lambda item: item[0], reverse=True)
        if not choices:
            continue
        attempt_id = choices[0][1]
        attempt = by_attempt[attempt_id]
        pair = paired[attempt_id]
        lines.extend(_detection_example_lines(
            title=title,
            root=root,
            detection_dir=detection_dir,
            attempt=attempt,
            blind=pair["blind"],
            aware=pair["mutation_aware"],
            simple_id=id_to_simple.get(attempt_id, attempt_id),
        ))
    (root / "mutation_detection_examples.md").write_text("\n".join(lines), encoding="utf-8")


def _write_source_summary(root: Path, attempts: list[dict[str, object]]) -> None:
    completed = [attempt for attempt in attempts if attempt.get("status") == "success"]
    successes = [attempt for attempt in attempts if attempt.get("success")]
    failed = [attempt for attempt in attempts if attempt.get("status") != "success"]
    proof_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for attempt in attempts:
        proof_groups[_proof_key(attempt)].append(attempt)

    lines = [
        "# Source Fuzzing Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Run directory: `{root}`",
        "",
        "## Overall",
        "",
        f"- Attempts written: **{len(attempts)}**",
        f"- Completed attempts: **{len(completed)}**",
        f"- Failed attempts: **{len(failed)}**",
        f"- Successful fuzzes: **{len(successes)}**",
        f"- Success rate over completed attempts: **{_rate(len(successes), len(completed)):.1%}**",
        "",
        "## Proof-Level Coverage",
        "",
        f"- Distinct correct proofs attempted: **{len(proof_groups)}**",
        f"- Distinct correct proofs with at least one successful fuzz: **{sum(1 for rows in proof_groups.values() if any(row.get('success') for row in rows))}**",
        "",
        "## By Topic",
        "",
        "| Topic | Attempts | Completed | Fuzz successes | Completed success rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for topic, rows in sorted(_group_by(attempts, _topic).items()):
        topic_completed = [row for row in rows if row.get("status") == "success"]
        topic_successes = [row for row in rows if row.get("success")]
        lines.append(
            f"| {topic} | {len(rows)} | {len(topic_completed)} | {len(topic_successes)} | "
            f"{_rate(len(topic_successes), len(topic_completed)):.1%} |"
        )
    lines.append("")
    (root / "source_fuzzing_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _write_successful_examples(
    root: Path,
    attempts: list[dict[str, object]],
    strategy_titles: dict[str, str],
    id_to_simple: dict[str, object],
) -> None:
    by_topic = _group_by(
        [
            attempt for attempt in attempts
            if attempt.get("success") and not SELF_LABEL_RE.search(str(attempt.get("mutated_proof_text", "")))
        ],
        _topic,
    )
    lines = [
        "# Successful Fuzzing Examples By Topic",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Run directory: `{root}`",
        "",
        "These examples are selected from successful fuzzing attempts and avoid mutated proofs that explicitly label their own error.",
        "",
    ]
    for topic, rows in sorted(by_topic.items()):
        attempt = max(rows, key=lambda row: (_diff_changed_lines(row) + 8 * len(_mutations(row)), _diff_changed_lines(row)))
        lines.extend(_source_example_lines(root, attempt, id_to_simple.get(str(attempt.get("attempt_id", ""))), strategy_titles))
    (root / "successful_fuzz_examples_by_topic.md").write_text("\n".join(lines), encoding="utf-8")


def _write_trace_mapping(root: Path, attempts: list[dict[str, object]]) -> None:
    trace_root = root / "source_attempt_traces"
    if not trace_root.exists():
        return
    rows = []
    for index, attempt in enumerate(attempts):
        attempt_id = str(attempt.get("attempt_id", ""))
        metadata = _metadata(attempt)
        trace_dir_name = str(metadata.get("trace_dir_name") or index)
        rows.append(
            {
                "simple_attempt_id": trace_dir_name,
                "attempt_id": attempt_id,
                "trace_dir": str(trace_root / trace_dir_name),
            }
        )
    (trace_root / "attempt_id_mapping.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (trace_root / "attempt_id_mapping.tsv").write_text(
        "simple_attempt_id\tattempt_id\ttrace_dir\n"
        + "".join(f"{row['simple_attempt_id']}\t{row['attempt_id']}\t{row['trace_dir']}\n" for row in rows),
        encoding="utf-8",
    )


def _source_example_lines(
    root: Path,
    attempt: dict[str, object],
    simple_id: object,
    strategy_titles: dict[str, str],
) -> list[str]:
    metadata = _metadata(attempt)
    attempt_id = str(attempt.get("attempt_id", ""))
    simple = simple_id if simple_id is not None else attempt_id
    trace_dir = root / "source_attempt_traces" / str(simple)
    lines = [
        f"## {_topic(attempt).replace('_', ' ').title()}",
        "",
        f"- Attempt: `{simple}`",
        f"- Original attempt id: `{attempt_id}`",
        f"- Mutation trace dir: `{trace_dir}`",
    ]
    lines.extend(_strategy_lines(attempt, strategy_titles))
    blind_result = _dict(attempt.get("judge_result"))
    blind_errors = blind_result.get("detected_errors", ())
    blind_error_count = len(blind_errors) if isinstance(blind_errors, list) else 0
    introduced_match = _dict(
        metadata.get("introduced_error_match")
        or metadata.get("judge_error_detection_check")
    )
    introduced_error_found = introduced_match.get(
        "introduced_error_found",
        introduced_match.get("any_judge_reported_correct_error", ""),
    )
    lines.extend([
        f"- Example: `{metadata.get('example_id', '')}`; sample index: `{metadata.get('sample_index', '')}`",
        f"- Problem id: `{metadata.get('problem_id') or metadata.get('grading_id') or ''}`",
        f"- Blind error-finder items: `{blind_error_count}`; introduced error found by matcher: `{introduced_error_found}`; mutation-check verdict: `{_dict(attempt.get('mutation_check_result')).get('verdict', '')}`",
        f"- Full diff size: about **{_diff_changed_lines(attempt)} changed lines** in the sentence/paragraph diff",
        "",
        "**Problem excerpt:**",
        "",
        f"> {_compact(metadata.get('problem', ''), 750)}",
        "",
        "**Mutation description:**",
        "",
    ])
    lines.extend(_mutation_lines(attempt))
    rationale = _dict(attempt.get("mutation_instructions")).get("rationale", "")
    if rationale:
        lines.extend(["", f"Rationale recorded by fuzzer: {_compact(rationale, 800)}"])
    flaw = _dict(attempt.get("mutation_check_result")).get("detected_flaw", "")
    if flaw:
        lines.extend(["", f"Mutation-check detected flaw: {_compact(flaw, 800)}"])
    lines.extend(["", "**Quoted proof diff:**", "", "```diff", _proof_diff(attempt), "```", ""])
    return lines


def _detection_example_lines(
    *,
    title: str,
    root: Path,
    detection_dir: Path,
    attempt: dict[str, object],
    blind: dict[str, object],
    aware: dict[str, object],
    simple_id: object,
) -> list[str]:
    strategy_titles = _load_strategy_titles(root)
    attempt_id = str(attempt.get("attempt_id", ""))
    lines = [
        f"### {title}",
        "",
        f"- Attempt: `{simple_id}`",
        f"- Original attempt id: `{attempt_id}`",
        f"- Source trace dir: `{root / 'source_attempt_traces' / str(simple_id)}`",
    ]
    lines.extend(_strategy_lines(attempt, strategy_titles))
    metadata = _metadata(attempt)
    lines.extend([
        f"- Topic: `{_topic(attempt)}`; example: `{metadata.get('example_id', '')}`; sample index: `{metadata.get('sample_index', '')}`",
        f"- Problem id: `{metadata.get('problem_id') or metadata.get('grading_id') or ''}`",
        f"- Fuzz success: `{attempt.get('success')}`",
        "",
        "**Mutation produced:**",
        "",
    ])
    lines.extend(_mutation_lines(attempt))
    lines.extend([""])
    lines.extend(_detection_block("Blind detector, no mutation hint", detection_dir, blind))
    lines.extend(_detection_block("Mutation-aware detector, mutation hint given", detection_dir, aware))
    lines.extend(["**Quoted proof diff:**", "", "```diff", _proof_diff(attempt), "```", ""])
    return lines


def _detection_block(title: str, detection_dir: Path, row: dict[str, object]) -> list[str]:
    detection = _dict(row.get("detection"))
    adjudication = _dict(row.get("adjudication"))
    return [
        f"**{title}:**",
        "",
        f"- Outcome: **{'detected' if _detected(row) else 'not detected'}**",
        f"- Detector verdict: `{detection.get('verdict', '')}`; confidence: `{detection.get('confidence', '')}`",
        f"- Adjudicator match level: `{adjudication.get('match_level', '')}`",
        f"- Detection trace: `{detection_dir / str(row.get('trace_file', ''))}`",
        f"- Detected flaw: {_compact(detection.get('detected_flaw', ''), 700) or '(empty)'}",
        f"- Adjudicator rationale: {_compact(adjudication.get('rationale', ''), 700) or '(empty)'}",
        "",
    ]


def _strategy_lines(attempt: dict[str, object], strategy_titles: dict[str, str]) -> list[str]:
    ids = [str(item) for item in attempt.get("strategy_ids", ()) if item]
    selection = _dict(_metadata(attempt).get("strategy_selection"))
    sources = [str(item) for item in selection.get("selected_strategy_sources", ()) if item]
    if not ids:
        return ["- Strategy used: `no`", "- Used mined strategy: `no`"]
    return [
        "- Strategy used: `yes`",
        f"- Strategy sources: `{', '.join(sources) if sources else 'unknown'}`",
        f"- Used mined strategy: `{'yes' if 'mined' in sources else 'no'}`",
        "- Strategy ids: " + ", ".join(f"`{strategy_id}`" for strategy_id in ids),
        "- Strategy titles: " + "; ".join(f"{strategy_id}: {strategy_titles.get(strategy_id, strategy_id)}" for strategy_id in ids),
    ]


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_strategy_titles(root: Path) -> dict[str, str]:
    titles = {}
    for path in (root / "strategies_natural_language.jsonl", Path("src/proof_fuzzer/data/mined_strategies.jsonl")):
        for row in _load_jsonl(path):
            strategy_id = str(row.get("strategy_id", ""))
            if strategy_id:
                titles[strategy_id] = str(row.get("title") or strategy_id)
    return titles


def _load_simple_attempt_ids(root: Path) -> dict[str, object]:
    mapping_path = root / "source_attempt_traces" / "attempt_id_mapping.json"
    if mapping_path.exists():
        return {
            str(row.get("attempt_id", "")): row.get("simple_attempt_id")
            for row in json.loads(mapping_path.read_text(encoding="utf-8"))
        }
    result = {}
    for trace_dir in (root / "source_attempt_traces").glob("*"):
        if not trace_dir.is_dir():
            continue
        attempt_path = trace_dir / "attempt.json"
        if attempt_path.exists():
            attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
            result[str(attempt.get("attempt_id", ""))] = trace_dir.name
    return result


def _group_by(rows: list[dict[str, object]], key_fn) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(key_fn(row) or "unknown")].append(row)
    return grouped


def _metadata(attempt: dict[str, object]) -> dict[str, object]:
    return _dict(attempt.get("metadata"))


def _dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _topic(attempt: dict[str, object]) -> str:
    metadata = _metadata(attempt)
    return str(metadata.get("math_topic") or metadata.get("llm_category") or "unknown")


def _proof_key(attempt: dict[str, object]) -> str:
    metadata = _metadata(attempt)
    return str(metadata.get("example_id") or metadata.get("example_path") or metadata.get("problem_id") or "unknown")


def _mutations(attempt: dict[str, object]) -> list[dict[str, object]]:
    return [item for item in _dict(attempt.get("mutation_instructions")).get("mutations", ()) if isinstance(item, dict)]


def _mutation_lines(attempt: dict[str, object]) -> list[str]:
    lines = []
    for index, mutation in enumerate(_mutations(attempt), start=1):
        lines.append(f"{index}. `{mutation.get('kind', '')}` at `{mutation.get('target', '')}`: {mutation.get('summary', '')}")
    return lines or ["- (No structured mutation summary available.)"]


def _detected(row: dict[str, object]) -> bool:
    return bool(_dict(row.get("adjudication")).get("detected_correct_error"))


def _proof_diff(attempt: dict[str, object]) -> str:
    diff = list(difflib.unified_diff(
        _split_units(str(attempt.get("original_proof_text", ""))),
        _split_units(str(attempt.get("mutated_proof_text", ""))),
        fromfile="original proof",
        tofile="mutated proof",
        n=3,
        lineterm="",
    ))
    if len(diff) <= 130:
        return "\n".join(diff)
    return "\n".join(diff[:90] + ["... diff truncated ..."] + diff[-35:])


def _diff_changed_lines(attempt: dict[str, object]) -> int:
    return sum(
        1 for line in _proof_diff(attempt).splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )


def _split_units(text: str) -> list[str]:
    text = re.sub(r"\n{2,}", "\n\n", text.strip())
    out = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        parts = [part.strip() for part in para.splitlines() if part.strip()] if "\n" in para else re.split(r"(?<=[.!?])\s+", para)
        for part in parts:
            if len(part) > 260:
                out.extend(chunk.strip() for chunk in re.findall(r".{1,240}(?:\s+|$)", part) if chunk.strip())
            elif part.strip():
                out.append(part.strip())
        out.append("")
    return out


def _compact(text: object, limit: int) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    return value if len(value) <= limit else value[:limit].rstrip() + " ..."


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
