#!/usr/bin/env python3
"""Build the manually audited evaluation-mutation uniqueness annotations.

Two valid candidates are placed in the same cluster only when they introduce the
same false assertion or inference in the same source proof.  Different wording,
counterexamples, dependent edits, or proof hashes do not create a new logical
error.  Similar mechanisms in different proofs, and materially different false
claims in the same proof, remain separate.
"""

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
        "path": ROOT / "logs/by_dataset/olympiad/olympiad_20_frozen_eval_gpt56sol_medium_5x3_20260924/results.json",
        "repeat_groups": [
            [56, 102], [152, 198], [55, 57, 88],
            [63, 85], [74, 105, 111, 129, 136],
            [81, 108, 145, 170], [92, 93, 122],
            [6, 155], [75, 103, 127, 193],
            [23, 38, 112, 132], [37, 87], [141, 150],
            [110, 168], [65, 182], [76, 131], [95, 114, 161, 192],
            [2, 36], [3, 109, 194], [99, 104, 137],
            [73, 140, 179, 186], [12, 30, 49], [54, 86, 107, 162],
            [1, 52, 117, 118, 121, 125, 133, 139, 160, 171],
            [5, 16, 151, 172], [80, 147],
            [101, 119, 149, 158, 167], [40, 97],
            [120, 148, 156, 185], [11, 169],
            [19, 44, 100, 164, 188],
        ],
    },
    "graduate_course": {
        "label": "Graduate course dossiers",
        "path": ROOT / "logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/results.json",
        "repeat_groups": [
            [32, 81, 100], [76, 97], [29, 57],
            [36, 69, 79, 88], [53, 77], [5, 48],
            [41, 46, 65], [67, 99], [39, 52, 68],
            [66, 83], [9, 13, 14], [21, 74], [37, 93],
            [19, 82], [28, 34, 44], [45, 70, 87, 91],
            [11, 58, 61], [64, 78],
        ],
    },
    "tcs_open_problems": {
        "label": "TCS open problems",
        "path": ROOT / "logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/results.json",
        "repeat_groups": [
            [4, 50], [1, 18, 29], [2, 26], [21, 43],
            [9, 12, 23, 47],
        ],
    },
    "recent_math": {
        "label": "Recent mathematical research",
        "path": ROOT / "logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/results.json",
        "repeat_groups": [
            [1, 3, 5, 10], [2, 7, 9], [13, 19],
            [25, 27, 30], [22, 24], [32, 38],
            [33, 35, 39, 40], [34, 36], [42, 49],
            [43, 46, 50], [47, 48],
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
            cluster_id = f"{dataset}:L{cluster_number:03d}"
            for member in members:
                cluster_for[member] = cluster_id

        sizes = Counter(cluster_for.values())
        assert len(cluster_for) == len(valid)
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
        "scope": "Candidates with valid == true in the four frozen GPT-5.6-sol evaluations.",
        "summary": summaries,
        "annotations": annotations,
    }
    (OUT_DIR / "mutation_uniqueness_annotations.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )

    with (OUT_DIR / "mutation_uniqueness_annotations.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(annotations[0]))
        writer.writeheader()
        writer.writerows(annotations)

    for row in summaries:
        print(
            row["dataset_label"], row["valid_mutations"],
            row["distinct_logical_errors"], row["singleton_mutations"]
        )


if __name__ == "__main__":
    main()
