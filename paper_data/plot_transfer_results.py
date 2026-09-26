"""Generate the GPT-5.6-sol judge-miss-rate figure for the paper."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

from plotting_stats import wilson_interval


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
            "legend.fontsize": 30,
        }
    )
    series = (
        ("Discovery", DISCOVERY_COUNTS, "#2A78D6"),
        ("Strategy-guided", GUIDED_COUNTS, "#1BAF7A"),
        ("Unguided", UNGUIDED_COUNTS, "#EB6834"),
    )
    x = np.arange(len(DATASETS))
    width = 0.24
    offset_width = width

    fig, ax = plt.subplots(figsize=(18, 10.8), layout="constrained")
    for offset, (label, counts, color) in zip(
        (-offset_width, 0, offset_width), series
    ):
        values = percentages(counts)
        errors = error_bars(counts)
        bars = ax.bar(
            x + offset,
            values,
            width,
            yerr=errors,
            capsize=6,
            label=label,
            color=color,
            error_kw={"elinewidth": 2.0, "capthick": 2.0},
        )
        for bar, value, upper_error in zip(bars, values, errors[1]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + upper_error + 0.8,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=22,
            )

    ax.set_ylabel("Judge Miss Rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, DATASETS)
    ax.set_ylim(0, 52)
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
