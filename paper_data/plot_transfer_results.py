"""Generate the GPT-5.6-sol judge-miss-rate figure for the paper."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


DATASETS = (
    "Olympiad",
    "Graduate course\ndossiers",
    "TCS open\nproblems",
    "Recent mathematical\nresearch",
)

# Discovery values are verified blind-judge misses divided by independently
# assessed attempts. Evaluation values are missed blind reviews divided by all
# three review slots for every valid mutation. Counts come from
# QUANTITATIVE_RESULTS.md and its indexed run artifacts.
DISCOVERY_COUNTS = ((8, 489), (46, 250), (29, 100), (29, 102))
UNGUIDED_COUNTS = ((2, 300), (16, 147), (7, 63), (19, 75))
GUIDED_COUNTS = ((2, 300), (18, 147), (20, 69), (25, 75))


def percentages(counts: tuple[tuple[int, int], ...]) -> np.ndarray:
    return np.array([misses / total * 100 for misses, total in counts])


def main() -> None:
    plt.rcParams.update(
        {
            "font.size": 25.5,
            "axes.titlesize": 33,
            "axes.labelsize": 28.5,
            "xtick.labelsize": 25.5,
            "ytick.labelsize": 25.5,
            "legend.fontsize": 25.5,
        }
    )
    series = (
        ("Discovery", percentages(DISCOVERY_COUNTS), "#4C78A8"),
        ("Unguided evaluation", percentages(UNGUIDED_COUNTS), "#F58518"),
        ("Strategy-guided evaluation", percentages(GUIDED_COUNTS), "#54A24B"),
    )
    x = np.arange(len(DATASETS))
    width = 0.24
    offset_width = width

    fig, ax = plt.subplots(figsize=(18, 10.8), layout="constrained")
    for offset, (label, values, color) in zip(
        (-offset_width, 0, offset_width), series
    ):
        bars = ax.bar(x + offset, values, width, label=label, color=color)
        ax.bar_label(
            bars,
            labels=[f"{value:.1f}%" for value in values],
            padding=4,
            fontsize=19,
        )

    ax.set_title("GPT-5.6-sol judge miss rates across discovery and evaluation")
    ax.set_ylabel("Blind-judge review miss rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, DATASETS)
    ax.set_ylim(0, 38)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=3, loc="upper left")

    output = Path(__file__).parent / "figures" / "gpt56sol_transfer_judge_miss_rates.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
