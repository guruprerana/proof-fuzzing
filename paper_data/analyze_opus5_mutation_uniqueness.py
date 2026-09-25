#!/usr/bin/env python3
"""Build manually audited Claude Opus 5 mutation-uniqueness annotations."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper_data"

DATASETS = {
    "olympiad": {
        "label": "Olympiad",
        "path": ROOT / (
            "logs/by_dataset/olympiad/"
            "olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922/"
            "results.json"
        ),
        "repeat_groups": [
            [1, 52, 117, 118, 121, 125, 133, 139, 160, 171],
            [3, 9, 68, 109, 176],
            [5, 16, 34, 45, 80, 147, 151, 172, 183],
            [6, 146],
            [159, 193],
            [7, 184],
            [42, 47, 61],
            [18, 191],
            [12, 50, 54, 86, 96, 107, 162],
            [11, 188],
            [17, 163],
            [19, 44, 100, 164, 169],
            [14, 85, 111, 136],
            [63, 153],
            [77, 81, 115],
            [92, 122],
            [90, 174],
            [94, 102],
            [21, 101, 119],
            [58, 62, 89, 91, 149, 158, 167],
            [35, 38, 41, 70, 112, 113, 165, 199],
            [24, 55, 57, 200],
            [128, 142, 173],
            [25, 69, 83, 197],
            [60, 110, 123, 168, 189],
            [37, 84],
            [43, 87, 98],
            [78, 130],
            [120, 185],
            [116, 148, 156],
            [65, 76, 114, 131, 134, 154, 161, 182],
        ],
    },
    "graduate_course": {
        "label": "GraduateCourses",
        "path": ROOT / (
            "logs/by_dataset/graduate_course/"
            "graduate_course_10_frozen_eval_claude_opus5_medium_5x3_"
            "20260923_amended/results.json"
        ),
        "repeat_groups": [
            [34, 91],
            [45, 82],
            [22, 31, 75, 92],
            [18, 85],
            [5, 24],
            [98, 99],
            [58, 73],
            [20, 74],
            [21, 93],
            [27, 39, 42],
            [66, 83],
            [33, 36],
            [40, 79],
            [53, 69],
            [30, 54, 76],
            [32, 81],
        ],
    },
    "recent_math": {
        "label": "ArXivMath",
        "path": ROOT / (
            "logs/by_dataset/recent_math/runs/"
            "recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924/"
            "results.json"
        ),
        "repeat_groups": [
            [4, 30],
            [10, 27],
            [18, 31, 42],
            [5, 20, 29, 43],
            [6, 23, 34, 44],
            [8, 36, 38],
            [13, 41],
            [21, 28],
        ],
    },
}


def main() -> None:
    annotations: list[dict] = []
    summaries: list[dict] = []

    for dataset, config in DATASETS.items():
        rows = json.loads(config["path"].read_text())
        valid = {i: row for i, row in enumerate(rows, 1) if row.get("valid") is True}

        grouped: dict[int, tuple[int, ...]] = {}
        for group in config["repeat_groups"]:
            members = tuple(sorted(group))
            assert len(members) >= 2
            assert all(i in valid for i in members), (dataset, members)
            assert len({valid[i]["proof_id"] for i in members}) == 1, (dataset, members)
            for i in members:
                assert i not in grouped, (dataset, i)
                grouped[i] = members

        cluster_for: dict[int, str] = {}
        cluster_number = 0
        for i in sorted(valid):
            if i in cluster_for:
                continue
            cluster_number += 1
            members = grouped.get(i, (i,))
            cluster_id = f"opus5:{dataset}:L{cluster_number:03d}"
            for member in members:
                cluster_for[member] = cluster_id

        sizes = Counter(cluster_for.values())
        distinct = len(sizes)
        singleton = sum(size == 1 for size in sizes.values())
        summaries.append(
            {
                "dataset": dataset,
                "dataset_label": config["label"],
                "generated_candidates": len(rows),
                "valid_mutations": len(valid),
                "distinct_logical_errors": distinct,
                "distinct_error_rate": distinct / len(valid),
                "singleton_mutations": singleton,
                "singleton_rate": singleton / len(valid),
                "duplicate_excess_candidates": len(valid) - distinct,
            }
        )

        for i, row in valid.items():
            cluster_id = cluster_for[i]
            annotations.append(
                {
                    "dataset": dataset,
                    "candidate_index": i,
                    "proof_id": row["proof_id"],
                    "arm": row["arm"],
                    "mutation_sha256": row.get("mutation_sha256"),
                    "logical_error_cluster": cluster_id,
                    "cluster_size": sizes[cluster_id],
                    "is_singleton": sizes[cluster_id] == 1,
                }
            )

    payload = {
        "definition": (
            "A cluster is one false assertion or inference in one source proof. "
            "Wording, counterexample, dependent-edit, and proof-hash differences "
            "do not split a cluster; analogous errors in different proofs do."
        ),
        "scope": (
            "Candidates with valid == true in the three completed frozen Claude "
            "Opus 5 evaluations. OpenAI-TCS is excluded because its Opus 5 frozen "
            "evaluation has not been run."
        ),
        "summary": summaries,
        "annotations": annotations,
    }
    (OUT_DIR / "opus5_mutation_uniqueness_annotations.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )

    with (OUT_DIR / "opus5_mutation_uniqueness_annotations.csv").open(
        "w", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(annotations[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(annotations)

    for row in summaries:
        print(
            row["dataset_label"],
            row["valid_mutations"],
            row["distinct_logical_errors"],
            row["singleton_mutations"],
        )


if __name__ == "__main__":
    main()
