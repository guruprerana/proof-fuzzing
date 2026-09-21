#!/usr/bin/env python3
"""Consolidate source screening and independent audits into a ten-paper corpus."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path


FINAL_IDS = (
    "2507.04819", "2501.05622",  # algebra and number theory
    "2312.00701", "2405.19197",  # geometry and topology
    "2605.10535", "2406.16806",  # analysis and PDE
    "2309.06944", "2505.05324",  # probability and combinatorics
    "2412.13499", "2507.21862",  # logic and dynamics
)
ACCEPTED_RESERVE_IDS = ("2309.06224", "2407.01806")
AUDIT_ROOTS = (
    "recent_math_shortlist_v1",
    "recent_math_shortlist_v1_round2",
    "recent_math_shortlist_v1_round3",
    "recent_math_shortlist_v1_round4",
    "recent_math_shortlist_v1_round5",
    "recent_math_shortlist_v1_round6_analysis",
)


def disposition(audits: list[dict[str, object]]) -> str:
    recommendations = [str(a["result"].get("dataset_recommendation", "")) for a in audits]
    if len(audits) == 2 and recommendations == ["accept", "accept"]:
        return "accepted"
    if len(audits) == 2 and recommendations == ["reject", "reject"]:
        return "rejected"
    return "specialist_review"


def main() -> None:
    dataset_root = Path("local_datasets/recent_math_candidates_v1")
    audit_base = Path("logs/dataset_audits")
    source_manifest = json.loads((dataset_root / "manifest.json").read_text())
    rows_by_id = {
        row["arxiv_id"]: row
        for row in source_manifest["selected"] + source_manifest["reserve"]
    }

    audits_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    audit_locations: dict[str, list[str]] = defaultdict(list)
    for name in AUDIT_ROOTS:
        root = audit_base / name
        for result in json.loads((root / "results.json").read_text()):
            arxiv_id = str(result["arxiv_id"])
            audits_by_id[arxiv_id].append(result)
            audit_locations[arxiv_id].append(
                str(root / arxiv_id / f"audit_{result['audit_index']}" / "result.json")
            )

    audited = {}
    for arxiv_id, audits in audits_by_id.items():
        audits.sort(key=lambda row: int(row["audit_index"]))
        audited[arxiv_id] = {
            "disposition": disposition(audits),
            "audit_artifacts": audit_locations[arxiv_id],
            "verdicts": [a["result"].get("verdict") for a in audits],
            "recommendations": [a["result"].get("dataset_recommendation") for a in audits],
            "finding_counts": [len(a["result"].get("findings", [])) for a in audits],
            "summaries": [a["result"].get("summary", "") for a in audits],
        }

    for arxiv_id in (*FINAL_IDS, *ACCEPTED_RESERVE_IDS):
        if audited.get(arxiv_id, {}).get("disposition") != "accepted":
            raise ValueError(f"Final or reserve paper is not independently accepted: {arxiv_id}")

    def assembled(arxiv_id: str) -> dict[str, object]:
        return {
            **rows_by_id[arxiv_id],
            "corpus_status": "accepted_for_dossier_extraction",
            "baseline_audit": audited[arxiv_id],
        }

    papers = [assembled(arxiv_id) for arxiv_id in FINAL_IDS]
    reserves = [assembled(arxiv_id) for arxiv_id in ACCEPTED_RESERVE_IDS]
    counts = Counter(paper["area"] for paper in papers)
    if set(counts.values()) != {2} or len(counts) != 5:
        raise ValueError(f"Final corpus is not two-per-area balanced: {counts}")

    audit_dispositions = Counter(item["disposition"] for item in audited.values())
    payload = {
        "corpus": "recent_math_research_corpus_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "accepted_for_dossier_extraction_not_yet_split",
        "paper_count": len(papers),
        "area_distribution": dict(counts),
        "license_distribution": dict(Counter(paper["license"] for paper in papers)),
        "selection_policy": {
            "internet_source": "arXiv OAI metadata and TeX source archives",
            "allowed_licenses": ["CC BY 4.0", "CC BY-SA 4.0", "CC0 1.0"],
            "actual_selected_licenses": dict(Counter(paper["license"] for paper in papers)),
            "proof_text_policy": "verbatim source only; no authored bridging proofs",
            "source_gate": "readable TeX archive with theorem/proof structure and SHA-256",
            "audit_gate": "two independent high-reasoning accept recommendations",
            "balance": "two papers in each of five mathematical areas",
        },
        "audit_campaign": {
            "model": "gpt-5.6-sol",
            "reasoning_effort": "high",
            "unique_papers_audited": len(audited),
            "independent_audits": sum(len(v) for v in audits_by_id.values()),
            "paper_dispositions": dict(audit_dispositions),
            "audit_roots": [str(audit_base / name) for name in AUDIT_ROOTS],
        },
        "acknowledgement": "Thank you to arXiv for use of its open access interoperability.",
        "papers": papers,
        "accepted_reserve": reserves,
        "next_stage": (
            "Extract one cohesive theorem dossier per paper verbatim from TeX, then audit the "
            "extracted packet and create paper-disjoint discovery/held-out splits."
        ),
    }
    (dataset_root / "accepted_corpus.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )

    lines = [
        "# Recent mathematical research corpus v1",
        "",
        "Ten recent, openly licensed mathematical research papers accepted for theorem-dossier extraction.",
        "Every paper has a readable, hashed TeX source archive and two independent high-reasoning",
        "baseline audits recommending acceptance. This is a paper corpus, not yet a mutation dataset:",
        "proof sections still need verbatim extraction and packet-level re-audit.",
        "",
        f"Audit campaign: {len(audited)} unique papers, {sum(len(v) for v in audits_by_id.values())} "
        f"independent audits; dispositions {dict(audit_dispositions)}.",
        "",
        "| Area | arXiv | Paper | Words | Theorems | Proofs | Audit verdicts |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for paper in papers:
        title = str(paper["title"]).replace("|", "\\|")
        verdicts = ", ".join(str(v) for v in paper["baseline_audit"]["verdicts"])
        lines.append(
            f"| {paper['area'].replace('_', ' ')} | [{paper['arxiv_id']}]"
            f"(https://arxiv.org/abs/{paper['arxiv_id']}) | {title} | "
            f"{paper['approximate_source_words']} | {paper['theorem_like_environments']} | "
            f"{paper['proof_environments']} | {verdicts} |"
        )
    lines += [
        "",
        "## Accepted reserves",
        "",
    ]
    for paper in reserves:
        lines.append(f"- [{paper['title']}](https://arxiv.org/abs/{paper['arxiv_id']})")
    lines += [
        "",
        "## Important limitation",
        "",
        "The audits are screening evidence, not peer review or a guarantee of correctness. Findings",
        "in rejected papers may themselves require specialist confirmation. The strict gate is used",
        "to reduce baseline noise before mutation experiments, not to make public correctness claims.",
        "",
        "Thank you to arXiv for use of its open access interoperability.",
    ]
    (dataset_root / "AUDIT_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({
        "papers": len(papers),
        "area_distribution": dict(counts),
        "audit_dispositions": dict(audit_dispositions),
    }, indent=2))


if __name__ == "__main__":
    main()
