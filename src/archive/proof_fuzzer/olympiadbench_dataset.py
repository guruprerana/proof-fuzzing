"""OlympiadBench adapter for the generic strategy-transfer pipeline."""

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


OLYMPIAD_TOPICS = ("Algebra", "Combinatorics", "Geometry", "Number Theory")
CORRECT_LABELS = {"true", "correct", "1", "yes"}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class OlympiadProof:
    example_id: str
    problem: str
    proof: str
    path: Path
    topic: str
    selector: str
    solution_index: int
    artifact: str = ""
    correctness: bool | None = None
    correctness_label: str | None = None

    @property
    def folder(self) -> str:
        return self.selector.split(":", 1)[0]

    def metadata(self) -> dict[str, object]:
        return {"problem_id": self.example_id, "selector": self.selector, "topic": self.topic,
            "source": str(self.path), "source_sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
            "problem_sha256": _digest(re.sub(r"\s+", "", self.problem).casefold()),
            "proof_sha256": _digest(self.proof), "proof_chars": len(self.proof),
            "artifact": self.artifact or f"original_data.solution[{self.solution_index}]",
            "correctness": self.correctness, "correctness_label": self.correctness_label,
            "problem": self.problem}


def load_examples(
    root: Path,
    selectors: list[str],
    *,
    proof_artifact: str = "reference_solution",
    require_correct: bool = False,
) -> list[OlympiadProof]:
    """Load a disjoint, text-only collection of selected proof artifacts."""
    if proof_artifact not in {"reference_solution", "model_response"}:
        raise ValueError("proof_artifact must be 'reference_solution' or 'model_response'")
    examples, ids, questions = [], set(), set()
    for selector in selectors:
        if not re.fullmatch(r"\d{6}(?::\d+)?", selector):
            raise ValueError(f"Expected folder or folder:solution_index: {selector}")
        folder, _, raw_index = selector.partition(":")
        index = int(raw_index or 0)
        path = root / folder / "metadata.json"
        metadata = json.loads(path.read_text())
        data = metadata["original_data"]
        question = data["question"].strip()
        correctness_path = path.parent / "correctness.txt"
        correctness = None
        correctness_label = None
        if correctness_path.is_file():
            correctness_label = correctness_path.read_text(encoding="utf-8").strip()
            label = correctness_label.casefold()
            if label not in CORRECT_LABELS | {"false", "incorrect", "0", "no"}:
                raise ValueError(f"Unknown correctness label {label!r}: {folder}")
            correctness = label in CORRECT_LABELS
        if require_correct and correctness is not True:
            raise ValueError(f"OlympiadBench does not mark this response correct: {folder}")
        if proof_artifact == "model_response":
            if raw_index:
                raise ValueError(f"Solution indices do not apply to model responses: {selector}")
            proof = str(metadata.get("full_response") or "").strip()
            artifact = "full_response"
        else:
            solutions = data["solution"]
            proof = solutions[index] if isinstance(solutions, list) else solutions if index == 0 else None
            if proof is None:
                raise ValueError(f"No solution index {index}: {folder}")
            artifact = f"original_data.solution[{index}]"
        problem_id = str(data["id"])
        normalized = re.sub(r"\s+", "", question).casefold()
        if problem_id in ids or normalized in questions:
            raise ValueError(f"Duplicate problem in split: {selector} / {problem_id}")
        if (not proof.strip() or not question or any(data.get(f"image_{i}") for i in range(1, 10))
                or re.search(r"<img|!\[.*?\]\(", proof, flags=re.IGNORECASE)):
            raise ValueError(f"Expected a complete text-only solution: {selector}")
        ids.add(problem_id); questions.add(normalized)
        examples.append(OlympiadProof(problem_id, question, proof, path,
            data.get("subfield", "unspecified"), selector, index, artifact, correctness,
            correctness_label))
    return examples


def load_split(
    root: Path,
    discovery_selectors: list[str],
    heldout_selectors: list[str],
    *,
    per_topic: int = 5,
):
    expected_size = len(OLYMPIAD_TOPICS) * per_topic
    if len(discovery_selectors) != expected_size or len(heldout_selectors) != expected_size:
        raise ValueError(
            f"Select exactly {expected_size} discovery and {expected_size} held-out proofs"
        )
    examples = load_examples(
        root, [*discovery_selectors, *heldout_selectors],
        proof_artifact="model_response", require_correct=True,
    )
    discovery, heldout = examples[:expected_size], examples[expected_size:]
    expected_topics = Counter({topic: per_topic for topic in OLYMPIAD_TOPICS})
    for name, split in (("discovery", discovery), ("held-out", heldout)):
        actual = Counter(example.topic for example in split)
        if actual != expected_topics:
            raise ValueError(
                f"Expected {per_topic} proofs per Olympiad topic in {name}; got {dict(actual)}"
            )
    return discovery, heldout


def load_split_manifest(root: Path, manifest_path: Path):
    """Load and validate a fixed balanced selector manifest."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    per_topic = int(manifest.get("proofs_per_topic_per_split", 0))
    if per_topic < 1:
        raise ValueError("Manifest proofs_per_topic_per_split must be positive")

    def selectors(split: str) -> list[str]:
        groups = manifest.get(split)
        if not isinstance(groups, dict) or set(groups) != set(OLYMPIAD_TOPICS):
            raise ValueError(f"Manifest {split!r} must contain exactly the four Olympiad topics")
        result = []
        for topic in OLYMPIAD_TOPICS:
            values = groups[topic]
            if not isinstance(values, list) or len(values) != per_topic:
                raise ValueError(f"Manifest {split}.{topic} must contain {per_topic} selectors")
            result.extend(str(value) for value in values)
        return result

    if manifest.get("proof_artifact") != "full_response" or manifest.get("correctness_label") != "TRUE":
        raise ValueError("Balanced manifest must select TRUE-labeled full_response proofs")
    return load_split(root, selectors("discovery"), selectors("heldout"), per_topic=per_topic)
