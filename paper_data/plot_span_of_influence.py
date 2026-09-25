"""Validate span annotations and plot successful versus unsuccessful means."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ANNOTATION_DIR = HERE / "span_of_influence_annotations"
GRADUATE_RESULTS = (
    HERE.parent
    / "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/results.json"
)
TCS_RESULTS = (
    HERE.parent
    / "logs/by_dataset/tcs_open_problems/"
    "ten_matched_50_gpt-5.6-sol_medium_20260909_202502/results.json"
)
RECENT_RESULTS = (
    HERE.parent
    / "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/"
    "results.json"
)
SEED = 20260924
BOOTSTRAP_SAMPLES = 50_000
PERMUTATION_SAMPLES = 200_000


def _expected() -> dict[tuple[str, int], dict]:
    expected: dict[tuple[str, int], dict] = {}
    for dataset, path in (
        ("graduate_course", GRADUATE_RESULTS),
        ("tcs", TCS_RESULTS),
        ("recent_math", RECENT_RESULTS),
    ):
        rows = json.loads(path.read_text())
        for index, row in enumerate(rows, 1):
            if row.get("valid") is True:
                expected[(dataset, index)] = row
    return expected


def _load_and_validate() -> list[dict]:
    paths = sorted(ANNOTATION_DIR.glob("tcs_[0-9]*.json")) + sorted(
        ANNOTATION_DIR.glob("recent_[0-9]*.json")
    ) + [ANNOTATION_DIR / "graduate_course.json"]
    annotations = [row for path in paths for row in json.loads(path.read_text())]
    expected = _expected()
    observed: dict[tuple[str, int], dict] = {}
    required = {
        "dataset",
        "candidate_index",
        "proof_id",
        "arm",
        "successful",
        "missed_reviews",
        "mutation_start_line",
        "influence_end_line",
        "span_lines",
        "span_lower",
        "span_upper",
        "confidence",
        "mutated_object",
        "endpoint_rationale",
        "annotator",
    }
    for row in annotations:
        missing = required - row.keys()
        if missing:
            raise ValueError(f"annotation missing {sorted(missing)}: {row}")
        key = (row["dataset"], row["candidate_index"])
        if key in observed:
            raise ValueError(f"duplicate annotation: {key}")
        if key not in expected:
            raise ValueError(f"unexpected annotation: {key}")
        source = expected[key]
        misses = sum(review.get("detection") == "missed" for review in source["reviews"])
        if row["proof_id"] != source["proof_id"] or row["arm"] != source["arm"]:
            raise ValueError(f"source metadata mismatch: {key}")
        if row["missed_reviews"] != misses or row["successful"] != (misses > 0):
            raise ValueError(f"outcome mismatch: {key}")
        for field in ("span_lines", "span_lower", "span_upper"):
            if not isinstance(row[field], int) or row[field] < 1:
                raise ValueError(f"invalid {field}: {key}")
        if not row["span_lower"] <= row["span_lines"] <= row["span_upper"]:
            raise ValueError(f"span outside uncertainty bounds: {key}")
        observed[key] = row
    missing = expected.keys() - observed.keys()
    if missing:
        raise ValueError(f"missing {len(missing)} valid candidates: {sorted(missing)}")
    return [observed[key] for key in sorted(observed)]


def _mean_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    draws = rng.choice(values, size=(BOOTSTRAP_SAMPLES, len(values)), replace=True)
    return tuple(np.percentile(draws.mean(axis=1), (2.5, 97.5)))


def _summary(rows: list[dict]) -> dict:
    rng = np.random.default_rng(SEED)
    summary: dict[str, dict] = {}
    for dataset in ("all", "graduate_course", "tcs", "recent_math"):
        subset = rows if dataset == "all" else [r for r in rows if r["dataset"] == dataset]
        summary[dataset] = {}
        for outcome, successful in (("successful", True), ("unsuccessful", False)):
            values = np.array(
                [r["span_lines"] for r in subset if r["successful"] is successful],
                dtype=float,
            )
            low, high = _mean_ci(values, rng)
            summary[dataset][outcome] = {
                "n": len(values),
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "standard_deviation": float(values.std(ddof=1)),
                "bootstrap_95_ci": [float(low), float(high)],
            }

    summary["comparisons"] = {}
    for dataset in ("all", "graduate_course", "tcs", "recent_math"):
        subset = rows if dataset == "all" else [r for r in rows if r["dataset"] == dataset]
        success = np.array(
            [r["span_lines"] for r in subset if r["successful"]], dtype=float
        )
        failure = np.array(
            [r["span_lines"] for r in subset if not r["successful"]], dtype=float
        )
        observed = float(success.mean() - failure.mean())
        pooled = np.concatenate((success, failure))
        permutation_differences = np.empty(PERMUTATION_SAMPLES)
        for i in range(PERMUTATION_SAMPLES):
            permuted = rng.permutation(pooled)
            permutation_differences[i] = (
                permuted[: len(success)].mean() - permuted[len(success) :].mean()
            )
        summary["comparisons"][dataset] = {
            "mean_difference_successful_minus_unsuccessful": observed,
            "two_sided_permutation_p": float(
                (np.count_nonzero(np.abs(permutation_differences) >= abs(observed)) + 1)
                / (PERMUTATION_SAMPLES + 1)
            ),
        }
    summary["method"] = {
        "permutation_samples": PERMUTATION_SAMPLES,
        "bootstrap_samples_per_group": BOOTSTRAP_SAMPLES,
        "random_seed": SEED,
    }
    return summary


def _write_data(rows: list[dict], summary: dict) -> None:
    (HERE / "span_of_influence_annotations.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    )
    fieldnames = list(rows[0])
    with (HERE / "span_of_influence_annotations.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "span_of_influence_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )


def _plot(summary: dict) -> None:
    dataset_keys = ("graduate_course", "tcs", "recent_math", "all")
    dataset_labels = (
        "GraduateCourses",
        "OpenAI-TCS",
        "ArXivMath",
        "Pooled",
    )
    outcome_series = (
        ("Successful", "successful", "#E45756"),
        ("Unsuccessful", "unsuccessful", "#4C78A8"),
    )

    plt.rcParams.update(
        {
            "font.size": 34,
            "axes.labelsize": 38,
            "xtick.labelsize": 34,
            "ytick.labelsize": 34,
            "legend.fontsize": 32,
        }
    )
    fig, ax = plt.subplots(figsize=(20, 10.8), layout="constrained")
    x = np.arange(len(dataset_keys))
    width = 0.34
    all_highs: list[float] = []
    for offset, (label, outcome, color) in zip((-width / 2, width / 2), outcome_series):
        means = np.array([summary[key][outcome]["mean"] for key in dataset_keys])
        intervals = np.array(
            [summary[key][outcome]["bootstrap_95_ci"] for key in dataset_keys]
        )
        errors = np.vstack((means - intervals[:, 0], intervals[:, 1] - means))
        counts = [summary[key][outcome]["n"] for key in dataset_keys]
        all_highs.extend(intervals[:, 1])
        bars = ax.bar(
            x + offset,
            means,
            width,
            yerr=errors,
            capsize=8,
            label=label,
            color=color,
            error_kw={"elinewidth": 2.2, "capthick": 2.2},
        )
        ax.bar_label(
            bars,
            labels=[f"{mean:.1f}\n(n={count})" for mean, count in zip(means, counts)],
            padding=8,
            fontsize=26,
        )
    ax.set_ylabel("Mean nonblank proof lines")
    ax.set_xlabel("Evaluation dataset")
    ax.set_xticks(x, dataset_labels)
    ax.set_ylim(0, max(all_highs) * 1.25)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=2, loc="upper right")
    ax.text(
        0.01,
        0.98,
        "Error bars: 95% bootstrap CI",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=26,
        color="#555555",
    )
    output = HERE / "figures" / "gpt56sol_span_of_influence.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def main() -> None:
    rows = _load_and_validate()
    summary = _summary(rows)
    _write_data(rows, summary)
    _plot(summary)


if __name__ == "__main__":
    main()
