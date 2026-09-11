"""OlympiadBench adapter for the generic strategy-transfer pipeline."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


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

    @property
    def folder(self) -> str:
        return self.selector.split(":", 1)[0]

    def metadata(self) -> dict[str, object]:
        return {"problem_id": self.example_id, "selector": self.selector, "topic": self.topic,
            "source": str(self.path), "source_sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
            "problem_sha256": _digest(re.sub(r"\s+", "", self.problem).casefold()),
            "proof_sha256": _digest(self.proof), "proof_chars": len(self.proof),
            "artifact": f"original_data.solution[{self.solution_index}]", "problem": self.problem}


def load_split(root: Path, discovery_selectors: list[str], heldout_selectors: list[str]):
    if len(discovery_selectors) != 5 or len(heldout_selectors) != 5:
        raise ValueError("Select exactly five discovery and five held-out proofs")
    examples, ids, questions = [], set(), set()
    for selector in [*discovery_selectors, *heldout_selectors]:
        if not re.fullmatch(r"\d{6}(?::\d+)?", selector):
            raise ValueError(f"Expected folder or folder:solution_index: {selector}")
        folder, _, raw_index = selector.partition(":")
        index = int(raw_index or 0)
        path = root / folder / "metadata.json"
        data = json.loads(path.read_text())["original_data"]
        question = data["question"].strip()
        solutions = data["solution"]
        proof = solutions[index] if isinstance(solutions, list) else solutions if index == 0 else None
        if proof is None:
            raise ValueError(f"No solution index {index}: {folder}")
        problem_id = str(data["id"])
        normalized = re.sub(r"\s+", "", question).casefold()
        if problem_id in ids or normalized in questions:
            raise ValueError(f"Duplicate problem in split: {selector} / {problem_id}")
        if (not proof.strip() or not question or any(data.get(f"image_{i}") for i in range(1, 10))
                or re.search(r"<img|!\[.*?\]\(", proof, flags=re.IGNORECASE)):
            raise ValueError(f"Expected a complete text-only solution: {selector}")
        ids.add(problem_id); questions.add(normalized)
        examples.append(OlympiadProof(problem_id, question, proof, path,
            data.get("subfield", "unspecified"), selector, index))
    return examples[:5], examples[5:]
