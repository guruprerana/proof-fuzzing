"""Measure character edits and compare successful with unsuccessful mutations."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
GRADUATE_ROOT = (
    HERE.parent
    / "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923"
)
TCS_ROOT = (
    HERE.parent
    / "logs/by_dataset/tcs_open_problems/"
    "ten_matched_50_gpt-5.6-sol_medium_20260909_202502"
)
RECENT_ROOT = (
    HERE.parent
    / "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923"
)
SEED = 20260924
BOOTSTRAP_SAMPLES = 50_000
PERMUTATION_SAMPLES = 200_000


def _levenshtein(left: str, right: str) -> int:
    """Return unit-cost character Levenshtein distance."""
    if left == right:
        return 0
    prefix = 0
    limit = min(len(left), len(right))
    while prefix < limit and left[prefix] == right[prefix]:
        prefix += 1
    left = left[prefix:]
    right = right[prefix:]
    suffix = 0
    limit = min(len(left), len(right))
    while suffix < limit and left[-suffix - 1] == right[-suffix - 1]:
        suffix += 1
    if suffix:
        left = left[:-suffix]
        right = right[:-suffix]
    if len(left) < len(right):
        left, right = right, left
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_character in enumerate(left, 1):
        current = [i]
        for j, right_character in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (left_character != right_character),
                )
            )
        previous = current
    return previous[-1]


def _changed_blocks(diff: str) -> list[tuple[str, str]]:
    """Extract adjacent removed/added text blocks from a unified diff."""
    blocks: list[tuple[str, str]] = []
    removed: list[str] = []
    added: list[str] = []
    in_hunk = False

    def flush() -> None:
        if removed or added:
            blocks.append(
                (
                    "".join(f"{line}\n" for line in removed),
                    "".join(f"{line}\n" for line in added),
                )
            )
            removed.clear()
            added.clear()

    # Split only at actual newline characters. Python's splitlines() would also
    # split at form feeds embedded in the PDF-derived TCS text.
    for raw_line in diff.split("\n"):
        line = raw_line.removesuffix("\r")
        if line.startswith("@@"):
            flush()
            in_hunk = True
        elif not in_hunk:
            continue
        elif line.startswith("-"):
            removed.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("\\ No newline at end of file"):
            continue
        else:
            flush()
    flush()
    return blocks


def _character_distance(diff: str) -> tuple[int, int]:
    distances = [_levenshtein(removed, added) for removed, added in _changed_blocks(diff)]
    return sum(distances), sum(distance > 0 for distance in distances)


def _load_rows() -> list[dict]:
    rows: list[dict] = []
    sources = (
        ("graduate_course", GRADUATE_ROOT / "results.json"),
        ("tcs", TCS_ROOT / "results.json"),
        ("recent_math", RECENT_ROOT / "results.json"),
    )
    for dataset, results_path in sources:
        results = json.loads(results_path.read_text())
        for candidate_index, result in enumerate(results, 1):
            if result.get("valid") is not True:
                continue
            if dataset == "tcs":
                diff = (
                    TCS_ROOT
                    / "attempts"
                    / f"{int(result['attempt']):03d}"
                    / "mutation.diff"
                ).read_text()
            else:
                diff = result["mutation_diff"]
            characters, changed_blocks = _character_distance(diff)
            misses = sum(
                review.get("detection") == "missed" for review in result["reviews"]
            )
            if characters < 1:
                raise ValueError(f"candidate has no character edits: {dataset} {candidate_index}")
            rows.append(
                {
                    "dataset": dataset,
                    "candidate_index": candidate_index,
                    "proof_id": result["proof_id"],
                    "arm": result["arm"],
                    "successful": misses > 0,
                    "missed_reviews": misses,
                    "characters_mutated": characters,
                    "changed_blocks": changed_blocks,
                    "mutation_sha256": result["mutation_sha256"],
                }
            )
    if len(rows) != 192:
        raise ValueError(f"expected 192 valid mutations, found {len(rows)}")
    return rows


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
                [r["characters_mutated"] for r in subset if r["successful"] is successful],
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
            [r["characters_mutated"] for r in subset if r["successful"]], dtype=float
        )
        failure = np.array(
            [r["characters_mutated"] for r in subset if not r["successful"]], dtype=float
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
        "metric": "character-level Levenshtein distance over changed diff blocks",
        "substitution_cost": 1,
        "insertion_cost": 1,
        "deletion_cost": 1,
        "newline_cost": 1,
        "permutation_samples": PERMUTATION_SAMPLES,
        "bootstrap_samples_per_group": BOOTSTRAP_SAMPLES,
        "random_seed": SEED,
    }
    return summary


def _write_data(rows: list[dict], summary: dict) -> None:
    (HERE / "mutated_character_counts.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    )
    with (HERE / "mutated_character_counts.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "mutated_character_summary.json").write_text(
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
        ("Successful", "successful", "#E34948"),
        ("Unsuccessful", "unsuccessful", "#2A78D6"),
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
    ax.set_ylabel("Mean character edit distance")
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
    output = HERE / "figures" / "gpt56sol_mutated_characters.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def main() -> None:
    rows = _load_rows()
    summary = _summary(rows)
    _write_data(rows, summary)
    _plot(summary)


if __name__ == "__main__":
    main()
