"""MedPRMBench trace loading and prompt-evolution benchmark integration.

The MedPRMBench v1 paper names a ``test_benchmark.jsonl`` artifact but does not
publish a machine-readable schema or download URL.  This module therefore uses
a small canonical schema, accepts common aliases used by process-reward data,
and also supports the 14 representative trace pairs printed in the appendix.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Iterable

from src.proof_fuzzer.reflect_prompt_evolution import (
    ReflectExample,
    ReflectPromptExperimentConfig,
    ReflectPromptExperimentResult,
    run_reflect_prompt_evolution_experiment,
)
from src.archive.proof_fuzzer.llm_interface import LLMClient


DEFAULT_MEDPRMBENCH_ROOT = Path("local_datasets/MedPRMBench")
MEDPRMBENCH_PAPER_ID = "2604.17282"
MEDPRMBENCH_PAPER_URL = f"https://arxiv.org/abs/{MEDPRMBENCH_PAPER_ID}"
MEDPRMBENCH_SOURCE_URL = f"https://arxiv.org/e-print/{MEDPRMBENCH_PAPER_ID}"


@dataclass(frozen=True)
class MedPRMErrorType:
    code: str
    name: str
    category: str
    operation: str
    severity_weight: float


MEDPRM_ERROR_TYPES = (
    MedPRMErrorType("S-1", "Non-Redundancy", "Simplicity", "insert redundant step", 0.2),
    MedPRMErrorType("S-2", "Non-Circular Logic", "Simplicity", "inject circular argument", 0.3),
    MedPRMErrorType("R-1", "Evidence-Based Soundness", "Soundness", "replace medical fact", 0.8),
    MedPRMErrorType("R-2", "Step Consistency", "Soundness", "introduce contradiction", 0.6),
    MedPRMErrorType("R-3", "Contextual Applicability", "Soundness", "ignore patient context", 0.6),
    MedPRMErrorType("R-4", "Confidence Invariance", "Soundness", "insert overconfident claim", 0.7),
    MedPRMErrorType("R-5", "Safety Awareness", "Soundness", "remove safety check", 1.0),
    MedPRMErrorType("R-6", "Information Grounding Compliance", "Soundness", "fabricate entity", 0.7),
    MedPRMErrorType("R-7", "Trajectory Reasoning", "Soundness", "reverse causal/temporal order", 0.6),
    MedPRMErrorType("E-1", "Prerequisite Sensitivity", "Sensitivity", "delete prerequisite step", 0.7),
    MedPRMErrorType("E-2", "Deception Resistance", "Sensitivity", "insert distractor", 0.5),
    MedPRMErrorType("E-3", "Multi-Solution Consistency", "Sensitivity", "dismiss alternatives", 0.4),
    MedPRMErrorType("E-4", "Quantitative Correctness", "Sensitivity", "alter numerical value", 0.5),
    MedPRMErrorType("E-5", "Differential Diagnosis Coverage", "Sensitivity", "narrow differential", 0.7),
)
MEDPRM_ERROR_TYPE_BY_CODE = {value.code: value for value in MEDPRM_ERROR_TYPES}


DEFAULT_MEDPRMBENCH_MUTATION_POLICY = """Goal:
Produce a clinically meaningful error in a correct medical reasoning chain that remains fluent,
internally plausible, and difficult for a blind evaluator to distinguish from the clean chain.

Strategies:
- Implement exactly the requested MedPRMBench error type and preserve the rest of the chain.
- Prefer a locally credible change whose defect becomes clear only after checking patient facts,
  medical knowledge, prerequisites, safety constraints, quantitative details, or dependencies.
- Preserve the answer, structure, terminology, uncertainty level, and step granularity whenever
  the requested failure permits; a correct final answer may conceal an unsafe reasoning step.
- For safety or prerequisite errors, omit or weaken the necessary check without announcing it.
- For factual, contextual, temporal, or quantitative errors, use a plausible near-miss rather than
  an absurd claim; keep downstream statements coherent with the planted error.
- Propagate the altered fact, interpretation, prerequisite, or calculation through dependent
  clinical steps when leaving them unchanged would create an unnatural contradiction. Every
  companion edit must remain a consequence of the same medical reasoning error.

Do not:
- Mention mutation, corruption, error labels, benchmarking, evaluators, or adversarial intent.
- Add disclaimers, malformed steps, conspicuous nonsense, or multiple unrelated clinical errors.
- Change patient facts unless the requested type specifically requires an ungrounded fabrication.
- Treat legitimate clinical uncertainty, an acceptable alternative, or stylistic brevity as error.
- Use propagation to introduce a second diagnosis, treatment, or safety error unrelated to the
  planted root cause.
- Copy the paper's reference corruption; generate a fresh failure from the clean trace only.

Before returning:
1. Identify the first step that becomes medically or logically invalid and why it matters.
2. Confirm the failure matches the requested taxonomy entry and is not merely controversial.
3. Confirm all non-targeted facts and reasoning remain faithful to the clean chain.
4. Propagate the failure through affected downstream steps wherever coherence requires it.
5. Confirm the result reads like authentic clinical reasoning and does not reveal the edit."""


@dataclass(frozen=True)
class MedPRMBenchTrace:
    """One clean/corrupted clinical reasoning pair."""

    variant_id: str
    case_id: str
    question: str
    original_steps: tuple[str, ...]
    modified_steps: tuple[str, ...]
    error_step_indices: tuple[int, ...]
    error_types: tuple[str, ...]
    severities: tuple[str, ...] = ()
    source_dataset: str = ""
    split: str = ""
    rationale: str = ""
    source: str = ""
    metadata: dict[str, object] = field(default_factory=dict, compare=False)

    @property
    def primary_error_type(self) -> str:
        return self.error_types[0]

    @property
    def original_reasoning(self) -> str:
        return format_medical_reasoning_steps(self.original_steps)

    @property
    def modified_reasoning(self) -> str:
        return format_medical_reasoning_steps(self.modified_steps)

    def to_prompt_evolution_example(self) -> ReflectExample:
        taxonomy = MEDPRM_ERROR_TYPE_BY_CODE.get(self.primary_error_type)
        requested = self.primary_error_type
        if taxonomy is not None:
            requested = f"{taxonomy.code} — {taxonomy.name} ({taxonomy.category})"
        return ReflectExample(
            example_id=f"medprmbench:{self.variant_id}",
            dataset="reasoning",
            trace_id=self.case_id,
            perturbation_type=requested,
            query=self.question,
            original_unit=self.original_reasoning,
            original_candidate=self.original_reasoning,
            unit_kind="text",
            source_dataset=f"medprmbench:{self.source_dataset or self.source}",
        )


@dataclass(frozen=True)
class MedPRMBenchPromptExperimentConfig:
    storage_dir: str | Path = "logs/medprmbench_prompt_evolution"
    dataset_root: str | Path = DEFAULT_MEDPRMBENCH_ROOT
    dataset_file: str = ""
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "medium"
    error_types: tuple[str, ...] = tuple(value.code for value in MEDPRM_ERROR_TYPES)
    train_case_fraction: float = 0.5
    train_examples: int = 5
    test_examples: int = 5
    test_attempts_per_example: int = 1
    training_generations: int = 3
    split_seed: int = 20260903
    evaluation_seed: int = 20260904
    max_workers: int = 5
    max_trace_chars: int = 24_000
    max_question_chars: int = 8_000
    max_prompt_chars: int = 6_000
    max_prompt_growth_chars: int = 400
    max_prompt_length_multiplier: float = 2.0
    max_attempt_summary_chars: int = 1_600
    max_evolution_context_chars: int = 48_000
    llm_retries: int = 1
    evolution_retries: int = 3
    initial_prompt: str = DEFAULT_MEDPRMBENCH_MUTATION_POLICY

    def __post_init__(self) -> None:
        normalized = tuple(dict.fromkeys(code.upper() for code in self.error_types))
        unknown = set(normalized) - set(MEDPRM_ERROR_TYPE_BY_CODE)
        if unknown:
            raise ValueError(f"Unknown MedPRMBench error types: {sorted(unknown)}")
        if not normalized:
            raise ValueError("At least one MedPRMBench error type must be selected.")
        object.__setattr__(self, "error_types", normalized)
        if (
            self.train_examples < 1
            or self.test_examples < 1
            or self.test_attempts_per_example < 1
        ):
            raise ValueError(
                "train_examples, test_examples, and test_attempts_per_example "
                "must be at least 1."
            )


@dataclass(frozen=True)
class MedPRMBenchPromptExperimentResult:
    traces_loaded: int
    source_files: tuple[Path, ...]
    experiment: ReflectPromptExperimentResult

    def summary(self) -> str:
        comparison = self.experiment.metrics.get("comparison", {})
        delta = comparison.get("success_rate_delta", 0.0) if isinstance(comparison, dict) else 0.0
        return (
            f"MedPRMBench prompt v{self.experiment.learned_prompt.version}; "
            f"traces={self.traces_loaded}; held-out attempts/arm="
            f"{len(self.experiment.baseline_attempts)}; success-rate delta="
            f"{float(delta):+.3f}; storage={self.experiment.storage_dir}"
        )


def load_medprmbench_traces(
    root_or_file: str | Path = DEFAULT_MEDPRMBENCH_ROOT,
    *,
    split: str | None = None,
) -> tuple[MedPRMBenchTrace, ...]:
    """Load canonical, appendix-derived, or release-style MedPRMBench JSONL."""

    paths = resolve_medprmbench_files(root_or_file)
    traces: list[MedPRMBenchTrace] = []
    for path in paths:
        inferred_split = _infer_split(path.name)
        for line_number, row in _iter_jsonl(path):
            try:
                trace = normalize_medprmbench_row(row, inferred_split=inferred_split)
            except Exception as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if split is None or trace.split.lower() == split.lower():
                traces.append(trace)
    if not traces:
        suffix = f" for split {split!r}" if split else ""
        raise ValueError(f"No MedPRMBench traces found{suffix} in {root_or_file}.")
    variant_ids = [trace.variant_id for trace in traces]
    if len(variant_ids) != len(set(variant_ids)):
        raise ValueError("MedPRMBench variant_id values must be unique across input files.")
    return tuple(traces)


def resolve_medprmbench_files(root_or_file: str | Path) -> tuple[Path, ...]:
    path = Path(root_or_file)
    if path.is_file():
        return (path,)
    if not path.is_dir():
        raise FileNotFoundError(
            f"MedPRMBench path does not exist: {path}. Run "
            "scripts/fetch_medprmbench_paper_examples.py or pass the released JSONL."
        )
    released = [
        value
        for value in (path / "test_benchmark.jsonl", path / "train_benchmark.jsonl")
        if value.is_file()
    ]
    # Do not silently mix the small appendix sample with an official release.
    files = released or [path / "paper_examples.jsonl"]
    files = [value for value in files if value.is_file()]
    if not files:
        files = sorted(path.glob("*.jsonl"))
    if not files:
        raise FileNotFoundError(f"No JSONL files found in MedPRMBench directory: {path}")
    return tuple(files)


def normalize_medprmbench_row(
    row: dict[str, object], *, inferred_split: str = ""
) -> MedPRMBenchTrace:
    """Normalize one row while retaining unknown release metadata."""

    question_value = _first(row, "question", "query", "problem", "prompt")
    question = _question_text(question_value, row)
    original_value = _first(
        row,
        "original_steps",
        "original_process",
        "correct_reasoning",
        "original_reasoning",
        "positive",
        "chosen",
    )
    modified_value = _first(
        row,
        "modified_steps",
        "corrupted_steps",
        "modified_process",
        "corrupted_reasoning",
        "error_reasoning",
        "negative",
        "rejected",
    )
    original_steps = _normalize_steps(original_value)
    modified_steps = _normalize_steps(modified_value)
    if not question:
        raise ValueError("missing question/query/problem text")
    if not original_steps:
        raise ValueError("missing original/correct reasoning steps")
    if not modified_steps:
        raise ValueError("missing modified/corrupted reasoning steps")

    mapping = _first(row, "error_step_code_mapping", "error_mapping", "step_errors")
    error_types = _normalize_error_types(
        _first(row, "error_types", "error_codes", "primary_error_type", "error_type"),
        mapping,
    )
    if not error_types:
        raise ValueError("missing MedPRMBench error type/code")
    unknown = set(error_types) - set(MEDPRM_ERROR_TYPE_BY_CODE)
    if unknown:
        raise ValueError(f"unknown MedPRMBench error type/code: {sorted(unknown)}")

    indices = _normalize_error_indices(row, mapping, original_steps, modified_steps)
    variant_id = str(
        _first(row, "variant_id", "example_id", "id", "uid") or ""
    ).strip()
    case_id = str(
        _first(row, "case_id", "instance_id", "question_id", "source_id") or variant_id
    ).strip()
    if not case_id:
        raise ValueError("missing case_id/instance_id")
    if not variant_id:
        variant_id = f"{case_id}:{'+'.join(error_types)}"
    severities = _string_tuple(
        _first(row, "severities", "severity_labels", "severity", "severity_level")
    )
    split = str(_first(row, "split", "_split") or inferred_split).strip()
    return MedPRMBenchTrace(
        variant_id=variant_id,
        case_id=case_id,
        question=question,
        original_steps=original_steps,
        modified_steps=modified_steps,
        error_step_indices=indices,
        error_types=error_types,
        severities=severities,
        source_dataset=str(_first(row, "source_dataset", "dataset_type", "dataset") or ""),
        split=split,
        rationale=str(_first(row, "rationale", "reason", "error_reason") or ""),
        source=str(_first(row, "source", "provenance") or ""),
        metadata=dict(row),
    )


def run_medprmbench_prompt_evolution_experiment(
    *,
    llm: LLMClient,
    config: MedPRMBenchPromptExperimentConfig | None = None,
    traces: tuple[MedPRMBenchTrace, ...] | None = None,
    progress=None,
) -> MedPRMBenchPromptExperimentResult:
    """Evolve a clinical mutation prompt and compare it on held-out cases."""

    active = config or MedPRMBenchPromptExperimentConfig()
    source_path = Path(active.dataset_file) if active.dataset_file else Path(active.dataset_root)
    loaded = traces or load_medprmbench_traces(source_path)
    selected = tuple(
        trace for trace in loaded if trace.primary_error_type in active.error_types
    )
    if not selected:
        raise ValueError("No loaded traces match the selected MedPRMBench error types.")
    examples = tuple(trace.to_prompt_evolution_example() for trace in selected)
    source_files = resolve_medprmbench_files(source_path)
    manifest_root = source_path.parent if source_path.is_file() else source_path
    manifest_files = tuple(str(path.relative_to(manifest_root)) for path in source_files)
    reflect_config = ReflectPromptExperimentConfig(
        storage_dir=active.storage_dir,
        dataset_root=manifest_root,
        model=active.model,
        reasoning_effort=active.reasoning_effort,
        datasets=("reasoning",),
        train_trace_fraction=active.train_case_fraction,
        train_examples_per_dataset=active.train_examples,
        test_examples_per_dataset=active.test_examples,
        test_attempts_per_example=active.test_attempts_per_example,
        training_generations=active.training_generations,
        split_seed=active.split_seed,
        evaluation_seed=active.evaluation_seed,
        max_workers=active.max_workers,
        max_unit_chars=active.max_trace_chars,
        max_candidate_chars=active.max_trace_chars,
        max_context_chars=active.max_trace_chars,
        max_query_chars=active.max_question_chars,
        max_prompt_chars=active.max_prompt_chars,
        max_prompt_growth_chars=active.max_prompt_growth_chars,
        max_prompt_length_multiplier=active.max_prompt_length_multiplier,
        max_attempt_summary_chars=active.max_attempt_summary_chars,
        max_evolution_context_chars=active.max_evolution_context_chars,
        llm_retries=active.llm_retries,
        evolution_retries=active.evolution_retries,
        initial_prompt=active.initial_prompt,
        task_profile="medical_reasoning",
        dataset_manifest_files=manifest_files,
    )
    result = run_reflect_prompt_evolution_experiment(
        llm=llm,
        config=reflect_config,
        examples=examples,
        progress=progress,
    )
    return MedPRMBenchPromptExperimentResult(
        traces_loaded=len(selected), source_files=source_files, experiment=result
    )


def extract_medprmbench_paper_examples(tex: str) -> tuple[dict[str, object], ...]:
    """Extract the 14 representative trace pairs from the paper's LaTeX source."""

    marker = r"\section{Error Type Examples}"
    if marker not in tex:
        raise ValueError("MedPRMBench Error Type Examples appendix was not found.")
    appendix = tex.split(marker, 1)[1]
    box_pattern = re.compile(
        r"\\begin\{tcolorbox\}\[examplebox,\s*title=\{"
        r"(?P<code>[SRE]-\d):\s*(?P<name>.*?)\s*\\hfill\s*"
        r"\\texttt\{(?P<case_id>[^}]+)\}\}\]"
        r"(?P<body>.*?)\\end\{tcolorbox\}",
        re.DOTALL,
    )
    rows: list[dict[str, object]] = []
    for match in box_pattern.finditer(appendix):
        code = match.group("code")
        body = match.group("body")
        question_raw = _between(body, r"\textbf{Question:}", r"\tcblower")
        original_raw = _between(
            body, r"\textbf{1. Original Process}", r"\textbf{2. Modified Process}"
        )
        modified_raw = _between(
            body, r"\textbf{2. Modified Process}", r"\textbf{3. Reason}"
        )
        reason_raw = body.split(r"\textbf{3. Reason}", 1)[1]
        original_steps, _ = _extract_tex_steps(original_raw)
        modified_steps, error_indices = _extract_tex_steps(
            modified_raw, originals=original_steps
        )
        if not original_steps or not modified_steps:
            raise ValueError(f"Could not extract reasoning steps for {code}.")
        taxonomy = MEDPRM_ERROR_TYPE_BY_CODE[code]
        case_id = match.group("case_id").replace(r"\_", "_")
        rows.append(
            {
                "schema_version": 1,
                "source": "arxiv_appendix",
                "paper_id": MEDPRMBENCH_PAPER_ID,
                "variant_id": f"{case_id}:{code}",
                "case_id": case_id,
                "split": "paper",
                "question": _latex_to_text(question_raw),
                "original_steps": list(original_steps),
                "modified_steps": list(modified_steps),
                "error_step_indices": list(error_indices),
                "index_base": 0,
                "error_types": [code],
                "error_type_name": taxonomy.name,
                "error_category": taxonomy.category,
                "rationale": _latex_to_text(reason_raw),
            }
        )
    expected = set(MEDPRM_ERROR_TYPE_BY_CODE)
    actual = {str(row["error_types"][0]) for row in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError(
            f"Expected one paper example for each of 14 error types; found "
            f"{len(rows)} rows with codes {sorted(actual)}."
        )
    return tuple(rows)


def format_medical_reasoning_steps(steps: Iterable[str]) -> str:
    return "\n\n".join(f"Step {index}: {step.strip()}" for index, step in enumerate(steps, 1))


def _extract_tex_steps(
    text: str, *, originals: tuple[str, ...] = ()
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    step_pattern = re.compile(
        r"\\textbf\{Step\s+(?P<start>\d+)(?:(?:--|-)(?P<end>\d+))?:\}"
        r"(?P<content>.*?)(?=\\textbf\{Step\s+\d+|\Z)",
        re.DOTALL,
    )
    steps: list[str] = []
    errors: list[int] = []
    for match in step_pattern.finditer(text):
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        raw_content = match.group("content")
        content = _latex_to_text(raw_content)
        if end > start and "same as original" in content.lower():
            if len(originals) < end:
                raise ValueError("A paper trace abbreviates unavailable original steps.")
            steps.extend(originals[start - 1 : end])
            continue
        if end != start:
            raise ValueError(f"Unsupported non-copy step range: {start}--{end}")
        # The appendix uses red boxes and an explicit left-arrow marker for
        # erroneous steps.  Check before stripping TeX commands.
        is_error = r"\leftarrow" in raw_content and "error" in raw_content
        steps.append(content)
        if is_error:
            errors.append(len(steps) - 1)
    return tuple(steps), tuple(errors)


def _latex_to_text(value: str) -> str:
    text = value
    text = re.sub(r"\\hfill\s*\$?\\leftarrow\$?\s*\\textit\{error\}", "", text)
    text = re.sub(r"\\(?:colorbox|parbox)\[[^]]*\]\{[^{}]*\}", "", text)
    text = re.sub(r"\\(?:colorbox|parbox)(?:\[[^]]*\])?\{[^{}]*\}", "", text)
    text = re.sub(r"\\(?:textbf|textit|texttt|emph)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", "", text)
    text = re.sub(r"\\(?:smallskip|medskip|bigskip|noindent)\b", " ", text)
    text = text.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    text = text.replace(r"\gamma", "gamma").replace(r"\times", "×")
    text = text.replace(r"\geq", "≥").replace(r"\leq", "≤")
    text = text.replace(r"\^ote", "ôte").replace("$", "")
    text = text.replace("---", "—").replace("--", "–").replace("~", " ")
    text = text.replace("``", '"').replace("''", '"')
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^]]*\])?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _between(value: str, start: str, end: str) -> str:
    if start not in value or end not in value:
        raise ValueError(f"Missing expected paper markers: {start!r}, {end!r}")
    return value.split(start, 1)[1].split(end, 1)[0]


def _normalize_steps(value: object) -> tuple[str, ...]:
    if isinstance(value, dict):
        nested = _first(value, "steps", "reasoning", "process", "text", "content")
        return _normalize_steps(nested)
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                item = _first(item, "text", "content", "reasoning", "step")
            text = str(item or "").strip()
            if text:
                result.append(text)
        return tuple(result)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ()
        matches = list(re.finditer(r"(?im)^\s*(?:\*\*)?Step\s+\d+\s*:\s*", text))
        if matches:
            return tuple(
                text[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()
                for index, match in enumerate(matches)
            )
        paragraphs = tuple(part.strip() for part in re.split(r"\n\s*\n", text) if part.strip())
        return paragraphs or (text,)
    return ()


def _normalize_error_types(value: object, mapping: object) -> tuple[str, ...]:
    candidates = list(_string_tuple(value))
    if isinstance(mapping, dict):
        for mapped in mapping.values():
            candidates.extend(_string_tuple(mapped))
    codes: list[str] = []
    for candidate in candidates:
        match = re.search(r"\b([SRE]-\d)\b", candidate.upper())
        if match and match.group(1) not in codes:
            codes.append(match.group(1))
    return tuple(codes)


def _normalize_error_indices(
    row: dict[str, object],
    mapping: object,
    original_steps: tuple[str, ...],
    modified_steps: tuple[str, ...],
) -> tuple[int, ...]:
    raw_key = next(
        (
            key
            for key in ("error_step_indices", "error_indices", "error_steps")
            if row.get(key) is not None
        ),
        "",
    )
    raw = row.get(raw_key) if raw_key else None
    values: list[int] = []
    if isinstance(raw, (list, tuple)):
        for item in raw:
            if isinstance(item, dict):
                item = _first(item, "index", "step_index", "position")
            if isinstance(item, int) or (isinstance(item, str) and item.strip().isdigit()):
                values.append(int(item))
    values_from_mapping = False
    if not values and isinstance(mapping, dict):
        for key in mapping:
            match = re.search(r"\d+", str(key))
            if match:
                values.append(int(match.group()))
                values_from_mapping = True
    labels = _first(row, "labels", "step_labels", "validity")
    if not values and isinstance(labels, list) and len(labels) == len(modified_steps):
        values = [index for index, label in enumerate(labels) if _is_error_label(label)]
        return tuple(values)
    if values:
        index_base = _first(row, "index_base", "step_index_base")
        if index_base == 1 or str(index_base).lower() in {"one", "1-based", "one_based"}:
            values = [value - 1 for value in values]
        elif index_base is None and (raw_key == "error_steps" or values_from_mapping):
            # Human-facing "Step 1" annotations are normally one-based; fields
            # explicitly named *_indices remain zero-based unless declared.
            values = [value - 1 for value in values]
        elif index_base is None and 0 not in values and max(values) == len(modified_steps):
            values = [value - 1 for value in values]
        normalized = tuple(sorted(set(values)))
        if any(value < 0 or value >= len(modified_steps) for value in normalized):
            raise ValueError("error step index is outside the modified reasoning chain")
        return normalized
    # Deterministic fallback used when a release row omits explicit indices.
    return tuple(
        index
        for index, step in enumerate(modified_steps)
        if index >= len(original_steps) or step != original_steps[index]
    )


def _is_error_label(value: object) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value <= 0
    return str(value).strip().lower() in {"-", "-1", "0", "false", "error", "incorrect"}


def _question_text(value: object, row: dict[str, object]) -> str:
    if isinstance(value, dict):
        value = _first(value, "text", "question", "content")
    question = str(value or "").strip()
    options = _first(row, "options", "choices", "answer_options")
    if isinstance(options, dict):
        option_text = "\n".join(f"{key}. {item}" for key, item in options.items())
        question = f"{question}\n{option_text}".strip()
    elif isinstance(options, list):
        option_text = "\n".join(f"{chr(65 + index)}. {item}" for index, item in enumerate(options))
        question = f"{question}\n{option_text}".strip()
    return question


def _string_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    text = str(value).strip()
    return (text,) if text else ()


def _first(mapping: dict[str, object], *keys: str) -> object:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _infer_split(filename: str) -> str:
    lowered = filename.lower()
    for split in ("train", "test", "validation", "val", "dev", "paper"):
        if split in lowered:
            return split
    return ""


def _iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object.")
            yield line_number, row
