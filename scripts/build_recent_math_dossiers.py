#!/usr/bin/env python3
"""Build source-faithful proof dossiers from the accepted recent-math corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile


# One paper from each area is reserved for discovery and the other for held-out
# evaluation.  The order is fixed before any fuzzing feedback is observed.
DISCOVERY_IDS = (
    "2507.04819",
    "2312.00701",
    "2605.10535",
    "2309.06944",
    "2412.13499",
)
HELDOUT_IDS = (
    "2501.05622",
    "2405.19197",
    "2406.16806",
    "2505.05324",
    "2507.21862",
)

# The initial learning run uses the first three preregistered discovery papers.
PILOT_DISCOVERY_IDS = DISCOVERY_IDS[:3]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_primary_tex(root: Path, paper: dict[str, object]) -> tuple[str, str]:
    archive = root / str(paper["source_archive"])
    archive_bytes = archive.read_bytes()
    actual_archive_hash = sha256_bytes(archive_bytes)
    expected_archive_hash = str(paper["source_archive_sha256"])
    if actual_archive_hash != expected_archive_hash:
        raise ValueError(f"Archive checksum mismatch for {paper['arxiv_id']}")

    tex_files = paper["tex_files"]
    if not isinstance(tex_files, list) or len(tex_files) != 1:
        raise ValueError(f"Expected one primary TeX file for {paper['arxiv_id']}")
    member_name = str(tex_files[0])
    with tarfile.open(archive) as bundle:
        member = bundle.getmember(member_name)
        handle = bundle.extractfile(member)
        if handle is None:
            raise ValueError(f"Could not read {member_name} from {archive}")
        source = handle.read()
    return source.decode("utf-8", errors="strict"), actual_archive_hash


def make_record(root: Path, paper: dict[str, object]) -> dict[str, object]:
    proof, archive_hash = read_primary_tex(root, paper)
    paper_id = str(paper["arxiv_id"])
    abstract = str(paper["abstract"]).strip()
    problem = (
        f"Title: {paper['title']}\n\n"
        "Claims and scope (verbatim source abstract):\n"
        f"{abstract}\n"
    )
    metadata = {
        "dataset": "recent_math_research_dossiers_v1",
        "arxiv_id": paper_id,
        "area": paper["area"],
        "title": paper["title"],
        "authors": paper["authors"],
        "created": paper["created"],
        "updated": paper["updated"],
        "level": "research",
        "correctness": True,
        "cohesive": True,
        "internet_sourced": True,
        "exposition": "verbatim_arxiv_tex_source",
        "source_url": f"https://arxiv.org/abs/{paper_id}",
        "source_archive": paper["source_archive"],
        "source_archive_sha256": archive_hash,
        "primary_tex_file": paper["tex_files"][0],
        "source_text_sha256": sha256_bytes(proof.encode("utf-8")),
        "actual_word_count": len(proof.split()),
        "theorem_like_environments": paper["theorem_like_environments"],
        "proof_environments": paper["proof_environments"],
        "license": paper["license"],
        "license_url": paper["license_url"],
        "attribution": f"{paper['title']}, by {', '.join(paper['authors'])}, arXiv:{paper_id}.",
        "transformation": (
            "Primary TeX member copied byte-for-text from the verified arXiv source "
            "archive; no proof prose added, deleted, reordered, or macro-expanded."
        ),
        "baseline_audit": paper["baseline_audit"],
    }
    return {
        "example_id": f"arxiv_{paper_id.replace('.', '_')}",
        "problem": problem,
        "proof": proof,
        "metadata": metadata,
    }


def build(root: Path, corpus_path: Path) -> dict[str, object]:
    corpus = json.loads(corpus_path.read_text())
    by_id = {paper["arxiv_id"]: paper for paper in corpus["papers"]}
    expected = set(DISCOVERY_IDS) | set(HELDOUT_IDS)
    if set(by_id) != expected:
        raise ValueError("Accepted corpus does not match the frozen ten-paper split")

    return {
        "dataset": "recent_math_research_dossiers_v1",
        "description": (
            "Ten recent research-paper dossiers copied verbatim from verified, openly "
            "licensed arXiv TeX sources; one paper per area is assigned to discovery "
            "and its paired paper to held-out evaluation."
        ),
        "split_policy": (
            "Five area-matched, paper-disjoint pairs fixed before mutation feedback; "
            "the first member of each pair is discovery."
        ),
        "acknowledgement": corpus["acknowledgement"],
        "discovery": [make_record(root, by_id[paper_id]) for paper_id in DISCOVERY_IDS],
        "heldout": [make_record(root, by_id[paper_id]) for paper_id in HELDOUT_IDS],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("local_datasets/recent_math_candidates_v1/accepted_corpus.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_v1.json"),
    )
    parser.add_argument(
        "--pilot-output",
        type=Path,
        default=Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_pilot3_v1.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    corpus_path = args.corpus if args.corpus.is_absolute() else root / args.corpus
    output = args.output if args.output.is_absolute() else root / args.output
    pilot_output = args.pilot_output if args.pilot_output.is_absolute() else root / args.pilot_output

    payload = build(root, corpus_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    pilot_ids = {f"arxiv_{paper_id.replace('.', '_')}" for paper_id in PILOT_DISCOVERY_IDS}
    pilot = {
        "dataset": "recent_math_research_dossiers_pilot3_v1",
        "description": "Initial three-paper discovery-only subset of the frozen full split.",
        "parent_dataset": str(output.relative_to(root)),
        "discovery": [row for row in payload["discovery"] if row["example_id"] in pilot_ids],
        "heldout": [],
    }
    pilot_output.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n")

    for split in ("discovery", "heldout"):
        for row in payload[split]:
            print(split, row["metadata"]["arxiv_id"], row["metadata"]["actual_word_count"])
    print("pilot", ",".join(row["metadata"]["arxiv_id"] for row in pilot["discovery"]))


if __name__ == "__main__":
    main()
