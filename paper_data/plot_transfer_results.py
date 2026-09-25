"""Generate the GPT-5.6-sol judge-miss-rate figure for the paper."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


DATASETS = (
    "Olympiad",
    "GraduateCourses",
    "OpenAI-TCS",
    "ArXivMath",
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
            "font.size": 34,
            "axes.labelsize": 38,
            "xtick.labelsize": 34,
            "ytick.labelsize": 34,
            "legend.fontsize": 30,
        }
    )
    series = (
        ("Discovery", percentages(DISCOVERY_COUNTS), "#4C78A8"),
        ("Strategy-guided", percentages(GUIDED_COUNTS), "#54A24B"),
        ("Unguided", percentages(UNGUIDED_COUNTS), "#F58518"),
    )
    x = np.arange(len(DATASETS))
    width = 0.24
    offset_width = width

    fig, ax = plt.subplots(figsize=(18, 10.8), layout="constrained")
    for series_index, (offset, (label, values, color)) in enumerate(zip(
        (-offset_width, 0, offset_width), series
    )):
        bars = ax.bar(x + offset, values, width, label=label, color=color)
        annotations = ax.bar_label(
            bars,
            labels=[f"{value:.1f}%" for value in values],
            padding=14 if series_index == 1 else 4,
            fontsize=24,
        )
        if series_index == 0:
            annotations[2].set_horizontalalignment("right")
        elif series_index == 1:
            annotations[2].set_horizontalalignment("left")

    ax.set_ylabel("Judge Miss Rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, DATASETS)
    ax.set_ylim(0, 38)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        frameon=False,
        ncols=3,
        loc="upper left",
        bbox_to_anchor=(0, 0.98),
    )

    output = Path(__file__).parent / "figures" / "gpt56sol_transfer_judge_miss_rates.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
