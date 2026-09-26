"""Plot higher-reasoning judge miss rates on selected prior medium-effort misses."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


GROUPS = (
    "OpenAI-TCS",
    "ArXivMath",
    "Overall",
)

# (misses, adjudicated judges). GPT-5.6-sol counts come from the two ultra-effort
# batches; Claude Opus 5 counts come from the 128k-token max-effort runs, where two
# OpenAI-TCS token-limit hits count as misses and one timed-out call is excluded.
GPT_ULTRA = ((4, 6), (3, 6), (7, 12))
CLAUDE_MAX = ((5, 5), (6, 6), (11, 11))


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
        ("GPT-5.6-sol / ultra", GPT_ULTRA, "#2A78D6"),
        ("Claude Opus 5 / max", CLAUDE_MAX, "#EB6834"),
    )
    x = np.arange(len(GROUPS))
    width = 0.32

    fig, ax = plt.subplots(figsize=(15, 12), layout="constrained")
    for offset, (label, counts, color) in zip((-width / 2, width / 2), series):
        values = percentages(counts)
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=label,
            color=color,
            edgecolor="white",
            linewidth=2,
        )
        for bar, value, (misses, total) in zip(bars, values, counts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 1.5,
                f"{value:.0f}%\n({misses}/{total})",
                ha="center",
                va="bottom",
                fontsize=24,
            )

    ax.set_ylabel("Judge Miss Rate")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks(x, GROUPS)
    ax.set_ylim(0, 115)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        frameon=False, ncols=2, loc="lower center", bbox_to_anchor=(0.5, 1.0)
    )

    output = Path(__file__).parent / "figures" / "higher_reasoning_judge_miss_rates.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
