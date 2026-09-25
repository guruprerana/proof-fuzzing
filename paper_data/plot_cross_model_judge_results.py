"""Plot cross-model judge miss rates on selected strategy-guided mutations."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

from plotting_stats import wilson_interval


DATASETS = (
    "Olympiad",
    "GraduateCourses",
    "ArXivMath",
)

# Each cell contains ten valid strategy-guided mutations selected by descending
# original missed-review count. Counts come from the finalized cross-model run.
GPT_JUDGE_CLAUDE_MUTATIONS = ((3, 10), (5, 10), (7, 10))
CLAUDE_JUDGE_GPT_MUTATIONS = ((2, 10), (1, 10), (2, 10))


def percentages(counts: tuple[tuple[int, int], ...]) -> np.ndarray:
    return np.array([misses / total * 100 for misses, total in counts])


def error_bars(counts: tuple[tuple[int, int], ...]) -> np.ndarray:
    values = percentages(counts)
    intervals = np.array(
        [wilson_interval(misses, total) for misses, total in counts]
    ) * 100
    return np.vstack((values - intervals[:, 0], intervals[:, 1] - values))


def main() -> None:
    plt.rcParams.update(
        {
            "font.size": 34,
            "axes.labelsize": 38,
            "xtick.labelsize": 34,
            "ytick.labelsize": 34,
            "legend.fontsize": 29,
        }
    )
    series = (
        (
            "GPT-5.6-sol judge / Claude Opus 5 mutations",
            GPT_JUDGE_CLAUDE_MUTATIONS,
            "#4C78A8",
        ),
        (
            "Claude Opus 5 judge / GPT-5.6-sol mutations",
            CLAUDE_JUDGE_GPT_MUTATIONS,
            "#F58518",
        ),
    )
    x = np.arange(len(DATASETS))
    width = 0.32

    fig, ax = plt.subplots(figsize=(18, 10.8), layout="constrained")
    for offset, (label, counts, color) in zip((-width / 2, width / 2), series):
        values = percentages(counts)
        errors = error_bars(counts)
        bars = ax.bar(
            x + offset,
            values,
            width,
            yerr=errors,
            capsize=8,
            label=label,
            color=color,
            error_kw={"elinewidth": 2.2, "capthick": 2.2},
        )
        for bar, value, upper_error in zip(bars, values, errors[1]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + upper_error + 1.5,
                f"{value:.0f}%",
                ha="center",
                va="bottom",
                fontsize=26,
            )

    ax.set_ylabel("Judge Miss Rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, DATASETS)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=1, loc="upper left")

    output = Path(__file__).parent / "figures" / "cross_model_judge_miss_rates.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
