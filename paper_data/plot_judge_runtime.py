"""Summarize and plot blind-judge wall-clock runtime in the frozen evaluations."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
LOGS = HERE.parent / "logs/by_dataset"
BOOTSTRAP_SAMPLES = 50_000
SEED = 20260925

JUDGE_PROMPT_PREFIXES = (
    "Review this mathematical proof and report every concrete",
    # Blind-judge prompt used by the earlier GPT-5.6-sol OpenAI-TCS run.
    "You are reviewing a mathematical reasoning",
)
COMPLETED_STATUSES = {"completed", "TurnStatus.completed"}

DATASETS = ("Olympiad", "GraduateCourses", "OpenAI-TCS", "ArXivMath")
MODELS = ("GPT-5.6-sol", "Claude Opus 5")

GRADUATE_CLAUDE_SOURCE = (
    LOGS / "graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_10x3_20260923"
)
GRADUATE_CLAUDE_AMENDED = (
    LOGS / "graduate_course/"
    "graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended"
)

# Canonical result files; judge calls are kept only for sessions whose mutated proof
# matches a valid candidate in these results.
RESULTS = {
    ("Olympiad", "GPT-5.6-sol"): LOGS / "olympiad/olympiad_20_frozen_eval_gpt56sol_medium_5x3_20260924",
    ("Olympiad", "Claude Opus 5"): LOGS / "olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922",
    ("GraduateCourses", "GPT-5.6-sol"): LOGS / "graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923",
    ("GraduateCourses", "Claude Opus 5"): GRADUATE_CLAUDE_AMENDED,
    ("OpenAI-TCS", "GPT-5.6-sol"): LOGS / "tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502",
    ("OpenAI-TCS", "Claude Opus 5"): LOGS / "tcs_open_problems/opus5_snapshot120_frozen_eval_5x3_20260925",
    ("ArXivMath", "GPT-5.6-sol"): LOGS / "recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923",
    ("ArXivMath", "Claude Opus 5"): LOGS / "recent_math/runs/recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924",
}

# Each evaluation cell lists the run directories whose blind-judge calls produced
# the canonical reviews. The Claude GraduateCourses evaluation imports 65
# candidates from an earlier run, and the GPT-5.6-sol ArXivMath evaluation combines
# base, extension, and supplemental third-review runs.
RUNS = {
    ("Olympiad", "GPT-5.6-sol"): [
        LOGS / "olympiad/olympiad_20_frozen_eval_gpt56sol_medium_5x3_20260924",
    ],
    ("Olympiad", "Claude Opus 5"): [
        LOGS / "olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922",
    ],
    ("GraduateCourses", "GPT-5.6-sol"): [
        LOGS / "graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923",
    ],
    ("GraduateCourses", "Claude Opus 5"): [
        GRADUATE_CLAUDE_AMENDED,
        GRADUATE_CLAUDE_SOURCE,
    ],
    ("OpenAI-TCS", "GPT-5.6-sol"): [
        LOGS / "tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502",
    ],
    ("OpenAI-TCS", "Claude Opus 5"): [
        LOGS / "tcs_open_problems/opus5_snapshot120_frozen_eval_5x3_20260925",
    ],
    ("ArXivMath", "GPT-5.6-sol"): [
        LOGS / "recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2",
        LOGS / "recent_math/runs/"
        "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_extension_20260923",
        LOGS / "recent_math/runs/"
        "recent_math_clean_all5_v1_gpt56sol_medium_existing_third_reviews_20260923",
    ],
    ("ArXivMath", "Claude Opus 5"): [
        LOGS / "recent_math/runs/recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924",
    ],
}


def valid_mutation_hashes(results_dir: Path) -> set[str]:
    rows = json.loads((results_dir / "results.json").read_text())
    return {str(row["mutation_sha256"]) for row in rows if row.get("valid")}


def session_matches(session: Path, hashes: set[str]) -> bool:
    """Keep sessions without attempt folders; otherwise require a canonical mutation."""
    proofs = list(session.glob("attempts/*/mutated_proof.md"))
    if not proofs:
        return True
    return any(hashlib.sha256(proof.read_bytes()).hexdigest() in hashes for proof in proofs)


def trace_seconds(trace: Path) -> float:
    """Wall-clock seconds between the first and last recorded trace events."""
    stamps = [
        datetime.fromisoformat(json.loads(line)["recorded_at"])
        for line in trace.read_text().splitlines()
        if '"recorded_at"' in line
    ]
    return (stamps[-1] - stamps[0]).total_seconds()


def judge_calls(run: Path, hashes: set[str]) -> list[dict[str, object]]:
    calls = []
    session_cache: dict[Path, bool] = {}
    for metadata_path in sorted(run.glob("**/workspaces/*/metadata.json")):
        workspace = metadata_path.parent
        relative = workspace.relative_to(run)
        if relative.parts[0] == "sessions":
            session = run / "sessions" / relative.parts[1]
            if session not in session_cache:
                session_cache[session] = session_matches(session, hashes)
            if not session_cache[session]:
                continue
        prompt = workspace / "prompt.txt"
        if not prompt.exists() or not prompt.read_text()[:80].startswith(
            JUDGE_PROMPT_PREFIXES
        ):
            continue
        metadata = json.loads(metadata_path.read_text())
        seconds = metadata.get("elapsed_seconds")
        if seconds is None and metadata.get("status") in COMPLETED_STATUSES:
            trace_dir = Path(str(workspace).replace("workspaces", "codex_traces"))
            seconds = trace_seconds(trace_dir / "events.jsonl")
        calls.append(
            {
                "run": run.name,
                "call": str(relative),
                "status": metadata.get("status"),
                "seconds": seconds,
            }
        )
    return calls


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    draws = rng.choice(values, size=(BOOTSTRAP_SAMPLES, len(values)), replace=True)
    return tuple(np.percentile(draws.mean(axis=1), (2.5, 97.5)))


def summarize() -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    rng = np.random.default_rng(SEED)
    summary: dict[str, dict[str, object]] = {}
    rows: list[dict[str, object]] = []
    for dataset in DATASETS:
        for model in MODELS:
            hashes = valid_mutation_hashes(RESULTS[(dataset, model)])
            calls = []
            for run in RUNS[(dataset, model)]:
                calls.extend(judge_calls(run, hashes))
            completed = [
                call for call in calls if call["status"] in COMPLETED_STATUSES
            ]
            minutes = np.array([float(call["seconds"]) / 60 for call in completed])
            low, high = bootstrap_ci(minutes, rng)
            summary[f"{dataset} / {model}"] = {
                "dataset": dataset,
                "model": model,
                "valid_mutations": len(hashes),
                "completed_calls": len(completed),
                "excluded_failed_or_unfinished_calls": len(calls) - len(completed),
                "mean_minutes": float(minutes.mean()),
                "bootstrap_95_ci_minutes": [float(low), float(high)],
                "median_minutes": float(np.median(minutes)),
                "max_minutes": float(minutes.max()),
                "runs": [str(run.relative_to(HERE.parent)) for run in RUNS[(dataset, model)]],
            }
            rows.extend({"dataset": dataset, "model": model, **call} for call in calls)
    return summary, rows


def plot(summary: dict[str, dict[str, object]]) -> None:
    plt.rcParams.update(
        {
            "font.size": 34,
            "axes.labelsize": 38,
            "xtick.labelsize": 32,
            "ytick.labelsize": 34,
            "legend.fontsize": 29,
        }
    )
    colors = {"GPT-5.6-sol": "#2A78D6", "Claude Opus 5": "#EB6834"}
    x = np.arange(len(DATASETS))
    width = 0.34

    fig, ax = plt.subplots(figsize=(18, 12), layout="constrained")
    for offset, model in zip((-width / 2, width / 2), MODELS):
        cells = [summary[f"{dataset} / {model}"] for dataset in DATASETS]
        means = np.array([cell["mean_minutes"] for cell in cells])
        intervals = np.array([cell["bootstrap_95_ci_minutes"] for cell in cells])
        errors = np.vstack((means - intervals[:, 0], intervals[:, 1] - means))
        ax.bar(
            x + offset,
            means,
            width,
            yerr=errors,
            capsize=8,
            label=model,
            color=colors[model],
            edgecolor="white",
            linewidth=2,
            error_kw={"elinewidth": 2.2, "capthick": 2.2},
        )
        for position, mean, upper in zip(x + offset, means, intervals[:, 1]):
            label = f"{mean:.1f}" if mean >= 1 else f"{mean:.2f}"
            ax.text(position, upper + 0.4, label, ha="center", va="bottom", fontsize=26)

    ax.set_ylabel("Mean judge runtime (minutes)")
    ax.set_xticks(x, DATASETS)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))

    output = HERE / "figures" / "judge_eval_runtime.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def main() -> None:
    summary, rows = summarize()
    (HERE / "judge_runtime_summary.json").write_text(
        json.dumps(
            {
                "definition": (
                    "wall-clock seconds per completed blind-judge call in the canonical "
                    "frozen evaluations, pooled over arms; failed and unfinished calls "
                    "are excluded"
                ),
                "bootstrap_samples": BOOTSTRAP_SAMPLES,
                "seed": SEED,
                "cells": summary,
            },
            indent=2,
        )
        + "\n"
    )
    with (HERE / "judge_runtime_calls.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["dataset", "model", "run", "call", "status", "seconds"]
        )
        writer.writeheader()
        writer.writerows(rows)
    plot(summary)
    for key, cell in summary.items():
        print(
            f"{key:34s} n={cell['completed_calls']:4d} "
            f"excluded={cell['excluded_failed_or_unfinished_calls']:3d} "
            f"mean={cell['mean_minutes']:6.2f} "
            f"ci=({cell['bootstrap_95_ci_minutes'][0]:.2f}, "
            f"{cell['bootstrap_95_ci_minutes'][1]:.2f}) "
            f"median={cell['median_minutes']:6.2f} max={cell['max_minutes']:6.1f}"
        )


if __name__ == "__main__":
    main()
