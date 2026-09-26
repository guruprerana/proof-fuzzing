#!/usr/bin/env python3
"""Plot Opus 5 judge misses by mathematical area in frozen evaluation."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

from plotting_stats import wilson_interval


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "paper_data"

EVALUATIONS = {
    "olympiad": ROOT / (
        "logs/by_dataset/olympiad/"
        "olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922"
    ),
    "graduate_course": ROOT / (
        "logs/by_dataset/graduate_course/"
        "graduate_course_10_frozen_eval_claude_opus5_medium_5x3_"
        "20260923_amended"
    ),
    "tcs_open_problems": ROOT / (
        "logs/by_dataset/tcs_open_problems/"
        "opus5_snapshot120_frozen_eval_5x3_20260925"
    ),
    "recent_math": ROOT / (
        "logs/by_dataset/recent_math/runs/"
        "recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924"
    ),
}

DATASET_LABELS = {
    "olympiad": "Olympiad",
    "graduate_course": "GraduateCourses",
    "tcs_open_problems": "OpenAI-TCS",
    "recent_math": "ArXivMath",
}

RECENT_AREA_LABELS = {
    "algebra_and_number_theory": "Algebra and number theory",
    "geometry_and_topology": "Geometry and topology",
    "analysis_and_pde": "Analysis and PDE",
    "probability_and_combinatorics": "Probability and combinatorics",
    "logic_and_dynamics": "Logic and dynamics",
}

GRADUATE_AREA_LABELS = {
    "algebra and number theory": "Algebra and number theory",
    "analysis": "Analysis",
    "geometry and topology": "Geometry and topology",
}

TCS_TOPICS = {
    "01_high_dimensional_sphere_packing": "Discrete geometry (sphere packing)",
    "02_binary_and_spherical_codes": "Coding theory",
    "06_quantum_parallel_repetition": "Quantum information",
    "07_closest_vector_problem": "Lattice complexity",
    "09_multicolor_ramsey_numbers": "Combinatorics (Ramsey theory)",
}


def _proof_topics() -> dict[str, dict[str, str]]:
    olympiad_manifest = json.loads(
        (EVALUATIONS["olympiad"] / "manifest.json").read_text()
    )
    graduate_manifest = json.loads(
        (EVALUATIONS["graduate_course"] / "manifest.json").read_text()
    )
    recent_dataset = json.loads(
        (ROOT / "local_datasets/recent_math_research_dossiers_clean_v1.json").read_text()
    )
    return {
        "olympiad": {
            row["example_id"]: row["topic"]
            for row in olympiad_manifest["heldout"]
        },
        "graduate_course": {
            row["example_id"]: GRADUATE_AREA_LABELS[row["broad_area"]]
            for row in graduate_manifest["heldout"]
        },
        "tcs_open_problems": TCS_TOPICS,
        "recent_math": {
            row["example_id"]: RECENT_AREA_LABELS[row["metadata"]["area"]]
            for row in recent_dataset["heldout"]
        },
    }


def _summarize() -> list[dict]:
    topics = _proof_topics()
    output: list[dict] = []
    for dataset, directory in EVALUATIONS.items():
        results = json.loads((directory / "results.json").read_text())
        observed_proofs = {row["proof_id"] for row in results}
        if observed_proofs != topics[dataset].keys():
            raise ValueError(f"topic map mismatch for {dataset}")

        ordered_topics = list(dict.fromkeys(topics[dataset].values()))
        for topic in ordered_topics:
            subset = [
                row
                for row in results
                if row.get("valid") is True
                and topics[dataset][row["proof_id"]] == topic
            ]
            reviews = [review for row in subset for review in row["reviews"]]
            if any(
                review.get("detection") not in {"caught", "missed", "ambiguous"}
                for review in reviews
            ):
                raise ValueError(f"unexpected review outcome in {dataset}: {topic}")
            misses = sum(review["detection"] == "missed" for review in reviews)
            low, high = wilson_interval(misses, len(reviews))
            output.append(
                {
                    "dataset": dataset,
                    "dataset_label": DATASET_LABELS[dataset],
                    "subtopic": topic,
                    "valid_mutations": len(subset),
                    "review_slots": len(reviews),
                    "judge_misses": misses,
                    "judge_miss_rate": misses / len(reviews),
                    "wilson_95_ci_lower": low,
                    "wilson_95_ci_upper": high,
                    "ambiguous_reviews": sum(
                        review["detection"] == "ambiguous" for review in reviews
                    ),
                }
            )
    return output


def _write_data(rows: list[dict]) -> None:
    payload = {
        "scope": "Frozen Claude Opus 5 evaluation only; discovery excluded.",
        "unit": "Individual blind-judge review",
        "miss_definition": (
            "review.detection == 'missed'; ambiguous reviews are not misses"
        ),
        "confidence_interval": "95% Wilson score interval over review slots",
        "rows": rows,
    }
    (HERE / "opus5_eval_judge_misses_by_subtopic.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )
    with (HERE / "opus5_eval_judge_misses_by_subtopic.csv").open(
        "w", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _plot(rows: list[dict]) -> None:
    dataset_order = tuple(EVALUATIONS)
    plt.rcParams.update(
        {
            "font.size": 30,
            "axes.titlesize": 34,
            "axes.labelsize": 34,
            "xtick.labelsize": 28,
            "ytick.labelsize": 30,
            "legend.fontsize": 30,
        }
    )
    fig, axes = plt.subplots(
        4,
        1,
        figsize=(19, 19),
        gridspec_kw={"height_ratios": [4, 3, 5, 5]},
        layout="constrained",
    )
    for ax, dataset in zip(axes, dataset_order):
        subset = [row for row in rows if row["dataset"] == dataset]
        y = np.arange(len(subset))
        rates = np.array([row["judge_miss_rate"] for row in subset]) * 100
        intervals = np.array(
            [
                [row["wilson_95_ci_lower"], row["wilson_95_ci_upper"]]
                for row in subset
            ]
        ) * 100
        errors = np.vstack((rates - intervals[:, 0], intervals[:, 1] - rates))
        ax.barh(
            y,
            rates,
            xerr=errors,
            color="#2A78D6",
            capsize=6,
            error_kw={"elinewidth": 2.0, "capthick": 2.0},
        )
        ax.set_yticks(y, [row["subtopic"] for row in subset])
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        ax.set_title(DATASET_LABELS[dataset], loc="left", fontweight="bold")
        ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        for index, (rate, upper, row) in enumerate(
            zip(rates, intervals[:, 1], subset)
        ):
            ax.text(
                min(max(upper + 1.5, rate + 1.5), 96),
                index,
                f"{row['judge_misses']} / {row['review_slots']}",
                va="center",
                ha="left",
                fontsize=27,
                color="#333333",
            )

    axes[-1].set_xlabel("Judge Miss Rate")
    output = HERE / "figures" / "opus5_eval_judge_misses_by_subtopic.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def main() -> None:
    rows = _summarize()
    _write_data(rows)
    _plot(rows)
    for row in rows:
        print(
            row["dataset"],
            row["subtopic"],
            f"{row['judge_misses']}/{row['review_slots']}",
        )


if __name__ == "__main__":
    main()
