"""Plot cross-model judge miss rates on selected strategy-guided mutations."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


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
            percentages(GPT_JUDGE_CLAUDE_MUTATIONS),
            "#4C78A8",
        ),
        (
            "Claude Opus 5 judge / GPT-5.6-sol mutations",
            percentages(CLAUDE_JUDGE_GPT_MUTATIONS),
            "#F58518",
        ),
    )
    x = np.arange(len(DATASETS))
    width = 0.32

    fig, ax = plt.subplots(figsize=(18, 10.8), layout="constrained")
    for offset, (label, values, color) in zip((-width / 2, width / 2), series):
        bars = ax.bar(x + offset, values, width, label=label, color=color)
        ax.bar_label(
            bars,
            labels=[f"{value:.0f}%" for value in values],
            padding=4,
            fontsize=28,
        )

    ax.set_ylabel("Judge Miss Rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, DATASETS)
    ax.set_ylim(0, 80)
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
