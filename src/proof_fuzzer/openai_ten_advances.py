"""Loader for the TCS open-problems proof corpus."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


DEFAULT_OPENAI_TEN_ADVANCES_ROOT = Path(
    "local_datasets/openai_ten_advances_2026/proofs_markdown"
)

# This is the five-proof discovery partition used by the reported GPT-5.6-sol
# experiment. The remaining five proofs form the held-out evaluation partition.
DISCOVERY_IDS = (
    "03_nonsofic_groups",
    "04_connes_rigidity_conjecture",
    "05_arithmetic_circuit_complexity",
    "08_ehrhart_volume_conjecture",
    "10_extremal_number_conjectures",
)


@dataclass(frozen=True)
class OpenAITenAdvancesProof:
    """One full Markdown proof and its extracted problem statement."""

    example_id: str
    path: Path
    title: str
    abstract: str
    proof: str

    @property
    def problem(self) -> str:
        return f"{self.title}\n\nAbstract. {self.abstract}".strip()

    def metadata(self) -> dict[str, object]:
        return {
            "dataset": "openai_ten_advances_2026",
            "example_id": self.example_id,
            "example_path": str(self.path),
            "title": self.title,
        }


def load_openai_ten_advances_proofs(
    root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
) -> tuple[OpenAITenAdvancesProof, ...]:
    """Load all ten Markdown manuscripts in stable filename order."""

    path = Path(root).expanduser()
    if not path.is_dir():
        raise FileNotFoundError(f"TCS proof directory does not exist: {path}")
    files = sorted(path.glob("*.md"))
    if not files:
        raise ValueError(f"TCS proof directory contains no Markdown files: {path}")
    return tuple(_load_proof(file_path) for file_path in files)


def load_openai_ten_advances_split(
    root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
) -> tuple[tuple[OpenAITenAdvancesProof, ...], tuple[OpenAITenAdvancesProof, ...]]:
    """Return the reported five-proof discovery and five-proof held-out split."""

    proofs = load_openai_ten_advances_proofs(root)
    by_id = {proof.example_id: proof for proof in proofs}
    missing = sorted(set(DISCOVERY_IDS) - set(by_id))
    if missing:
        raise ValueError(f"TCS corpus is missing discovery proofs: {missing}")
    discovery = tuple(by_id[example_id] for example_id in DISCOVERY_IDS)
    heldout = tuple(proof for proof in proofs if proof.example_id not in DISCOVERY_IDS)
    if len(proofs) != 10 or len(heldout) != 5:
        raise ValueError(
            f"Expected the canonical 10-proof TCS corpus with a 5/5 split; "
            f"found {len(proofs)} proofs and {len(heldout)} held-out proofs"
        )
    return discovery, heldout


def _load_proof(path: Path) -> OpenAITenAdvancesProof:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if title_match is None:
        raise ValueError(f"Proof Markdown has no level-one title: {path}")
    abstract_match = re.search(
        r"\bAbstract\.\s*(.*?)(?=\n\s*Contents\s*$)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if abstract_match is None:
        raise ValueError(f"Proof Markdown has no extractable abstract: {path}")
    return OpenAITenAdvancesProof(
        example_id=path.stem,
        path=path,
        title=title_match.group(1).strip(),
        abstract=abstract_match.group(1).strip(),
        proof=text,
    )
