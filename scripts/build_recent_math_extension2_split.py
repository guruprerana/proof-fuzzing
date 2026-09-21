#!/usr/bin/env python3
"""Create the two unused cleaned discovery dossiers as a discovery-only split."""

import json
from pathlib import Path


SOURCE = Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_clean_v1.json")
OUTPUT = Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_clean_extension2_v1.json")
IDS = {"arxiv_2309_06944", "arxiv_2412_13499"}


def main() -> None:
    source = json.loads(SOURCE.read_text())
    discovery = [row for row in source["discovery"] if row["example_id"] in IDS]
    if {row["example_id"] for row in discovery} != IDS:
        raise ValueError("The requested extension dossiers are missing")
    payload = {
        "dataset": "recent_math_research_dossiers_clean_extension2_v1",
        "description": "Two unused cleaned discovery dossiers; held-out corpus remains untouched.",
        "parent_dataset": str(SOURCE),
        "discovery": discovery,
        "heldout": [],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
