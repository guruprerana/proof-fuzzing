#!/usr/bin/env python3
"""Harvest and source-screen recent, reusable mathematical research papers."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time
from typing import Iterable
from urllib.parse import urlencode
import xml.etree.ElementTree as ET


OAI = "https://oaipmh.arxiv.org/oai"
EPRINT = "https://export.arxiv.org/e-print/{arxiv_id}"
USER_AGENT = "proof-fuzzing-research-corpus/1.0 (noncommercial research)"
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "ax": "http://arxiv.org/OAI/arXiv/",
}

AREAS = {
    "algebra_and_number_theory": ("math:math:AG", "math:math:NT", "math:math:RA"),
    "geometry_and_topology": ("math:math:AT", "math:math:GT", "math:math:DG"),
    "analysis_and_pde": ("math:math:AP", "math:math:FA", "math:math:CA"),
    "probability_and_combinatorics": ("math:math:PR", "math:math:CO"),
    "logic_and_dynamics": ("math:math:LO", "math:math:DS"),
}

ALLOWED_LICENSES = {
    "http://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
    "http://creativecommons.org/licenses/by-sa/4.0/": "CC BY-SA 4.0",
    "https://creativecommons.org/licenses/by-sa/4.0/": "CC BY-SA 4.0",
    "http://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
}

POSITIVE = re.compile(
    r"\b(we prove|we show|we establish|main theorem|as an application|conjecture|"
    r"classification|rigidity|inequality|existence|uniqueness)\b", re.I
)
NEGATIVE = re.compile(
    r"\b(survey|expository|numerical|simulation|machine learning|dataset|benchmark|"
    r"computer-assisted|formalized|formalisation)\b", re.I
)
MANUAL_EXCLUSIONS = {
    "Application of Operator Theory for the Collatz Conjecture":
        "famous-open-problem bait; unsuitable until independently validated",
    "Existence of Multilateral Nash equilibria for families of games":
        "cross-listing does not fit the intended geometry/topology stratum",
    "The cycle double cover conjecture from the perspective of percolation theory on iterated line graphs":
        "claims proximity to a major open conjecture and needs specialist validation before candidacy",
    "Goldbach Conjecture: Violation Probability and Generalization to Prime-like Distributions":
        "famous-open-problem bait; unsuitable until independently validated",
    "On a Conjecture Concerning the Complementary Second Zagreb Index":
        "too short and narrow for the target research-proof dossier",
}
THEOREM_ENV = re.compile(
    r"\\begin\s*\{(?:theorem|lemma|proposition|corollary|claim|mainthm|thm|prop|lem)\*?\}",
    re.I,
)
PROOF_ENV = re.compile(r"\\begin\s*\{proof\*?\}|\\proof\b", re.I)
SECTION = re.compile(r"\\(?:sub)*section\*?\s*\{", re.I)
CITATION = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^]]*\]\s*)?\{", re.I)


def request_bytes(url: str, params: dict[str, str] | None = None) -> bytes:
    if params:
        url = f"{url}?{urlencode(params)}"
    completed = subprocess.run(
        [
            "curl", "-L", "--fail", "--silent", "--show-error",
            "--retry", "4", "--retry-all-errors", "--retry-delay", "5",
            "--user-agent", USER_AGENT, url,
        ],
        check=True,
        stdout=subprocess.PIPE,
        timeout=180,
    )
    return completed.stdout


def text(node: ET.Element, name: str) -> str:
    child = node.find(f"ax:{name}", NS)
    return "" if child is None or child.text is None else " ".join(child.text.split())


def parse_record(record: ET.Element) -> dict[str, object] | None:
    metadata = record.find("oai:metadata/ax:arXiv", NS)
    if metadata is None:
        return None
    authors = []
    for author in metadata.findall("ax:authors/ax:author", NS):
        forenames = text(author, "forenames")
        keyname = text(author, "keyname")
        authors.append(" ".join(part for part in (forenames, keyname) if part))
    license_url = text(metadata, "license")
    created = text(metadata, "created")
    return {
        "arxiv_id": text(metadata, "id"),
        "created": created,
        "updated": text(metadata, "updated") or created,
        "title": text(metadata, "title"),
        "authors": authors,
        "categories": text(metadata, "categories").split(),
        "comments": text(metadata, "comments"),
        "journal_reference": text(metadata, "journal-ref"),
        "doi": text(metadata, "doi"),
        "license_url": license_url,
        "license": ALLOWED_LICENSES.get(license_url),
        "abstract": text(metadata, "abstract"),
    }


def harvest_set(set_spec: str, start: str, end: str, max_pages: int) -> list[dict[str, object]]:
    params = {
        "verb": "ListRecords",
        "from": start,
        "until": end,
        "set": set_spec,
        "metadataPrefix": "arXiv",
    }
    records: list[dict[str, object]] = []
    for page in range(max_pages):
        root = ET.fromstring(request_bytes(OAI, params))
        error = root.find("oai:error", NS)
        if error is not None:
            raise RuntimeError(f"OAI error for {set_spec}: {error.get('code')} {error.text}")
        listing = root.find("oai:ListRecords", NS)
        if listing is None:
            break
        for raw in listing.findall("oai:record", NS):
            parsed = parse_record(raw)
            if parsed:
                records.append(parsed)
        token = listing.find("oai:resumptionToken", NS)
        if token is None or not (token.text or "").strip():
            break
        params = {"verb": "ListRecords", "resumptionToken": token.text.strip()}
        if page + 1 < max_pages:
            time.sleep(3)
    return records


def metadata_score(row: dict[str, object]) -> float:
    if row["title"] in MANUAL_EXCLUSIONS:
        row["automatic_exclusion"] = MANUAL_EXCLUSIONS[str(row["title"])]
        return -100.0
    combined = f"{row['title']} {row['abstract']} {row['comments']}"
    score = 2.0 * len(POSITIVE.findall(combined)) - 4.0 * len(NEGATIVE.findall(combined))
    if row.get("doi"):
        score += 2
    if row.get("journal_reference"):
        score += 2
    page_match = re.search(r"\b(\d{1,3})\s*pages?\b", str(row.get("comments", "")), re.I)
    if page_match:
        pages = int(page_match.group(1))
        row["reported_pages"] = pages
        if 12 <= pages <= 45:
            score += 4
        elif pages > 70 or pages < 7:
            score -= 3
    return score


def safe_member_text(archive: tarfile.TarFile, member: tarfile.TarInfo) -> str:
    if not member.isfile() or member.size > 8_000_000:
        return ""
    extracted = archive.extractfile(member)
    if extracted is None:
        return ""
    return extracted.read().decode("utf-8", errors="replace")


def analyze_source(path: Path) -> dict[str, object]:
    tex_parts = []
    try:
        with tarfile.open(path, "r:*") as archive:
            members = archive.getmembers()
            for member in members:
                if member.name.lower().endswith((".tex", ".ltx")):
                    content = safe_member_text(archive, member)
                    if content:
                        tex_parts.append((member.name, content))
    except tarfile.ReadError:
        return {"source_readable": False, "source_error": "not_a_readable_source_archive"}
    joined = "\n".join(content for _, content in tex_parts)
    if not joined:
        return {"source_readable": False, "source_error": "no_tex_files"}
    without_comments = re.sub(r"(?m)(?<!\\)%.*$", "", joined)
    prose = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^]]*\])?", " ", without_comments)
    prose = re.sub(r"[{}$^_\\]", " ", prose)
    words = re.findall(r"[A-Za-zÀ-ž][A-Za-zÀ-ž'-]*", prose)
    return {
        "source_readable": True,
        "tex_files": [name for name, _ in tex_parts],
        "tex_file_count": len(tex_parts),
        "approximate_source_words": len(words),
        "theorem_like_environments": len(THEOREM_ENV.findall(without_comments)),
        "proof_environments": len(PROOF_ENV.findall(without_comments)),
        "section_commands": len(SECTION.findall(without_comments)),
        "citation_commands": len(CITATION.findall(without_comments)),
    }


def source_score(row: dict[str, object]) -> float:
    if not row.get("source_readable"):
        return -100
    words = int(row["approximate_source_words"])
    theorems = int(row["theorem_like_environments"])
    proofs = int(row["proof_environments"])
    sections = int(row["section_commands"])
    score = float(row["metadata_score"])
    score += min(theorems, 20) * 0.35 + min(proofs, 15) * 0.55 + min(sections, 10) * 0.2
    if 8_000 <= words <= 40_000:
        score += 5
    elif words < 4_000 or words > 80_000:
        score -= 5
    if proofs < 3 or theorems < 5:
        score -= 8
    return round(score, 3)


def download_sources(rows: Iterable[dict[str, object]], source_dir: Path, delay: float) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows):
        arxiv_id = str(row["arxiv_id"])
        target = source_dir / f"{arxiv_id.replace('/', '_')}.tar"
        if not target.exists():
            try:
                target.write_bytes(request_bytes(EPRINT.format(arxiv_id=arxiv_id)))
                row["source_download_status"] = "downloaded"
            except Exception as error:  # Preserve candidate and failure evidence.
                row["source_download_status"] = "failed"
                row["source_download_error"] = repr(error)
                continue
            if index + 1:
                time.sleep(delay)
        else:
            row["source_download_status"] = "cached"
        row["source_archive"] = str(target)
        row["source_archive_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        row.update(analyze_source(target))


def markdown_report(selected: list[dict[str, object]], rejected: list[dict[str, object]]) -> str:
    lines = [
        "# Recent mathematical research candidate manifest",
        "",
        "Thirty source-screened candidates for a research-proof fuzzing corpus. All selected",
        "records carry CC BY 4.0, CC BY-SA 4.0, or CC0; source archives and exact hashes are",
        "retained locally. Selection is provisional pending unchanged-proof mathematical audits.",
        "",
        "Thank you to arXiv for use of its open access interoperability.",
        "",
        "| Area | arXiv | Year | Paper | License | Words | Theorems | Proofs | Score |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in selected:
        title = str(row["title"]).replace("|", "\\|")
        lines.append(
            f"| {row['area'].replace('_', ' ')} | [{row['arxiv_id']}]"
            f"(https://arxiv.org/abs/{row['arxiv_id']}) | {str(row['created'])[:4]} | "
            f"{title} | {row['license']} | {row.get('approximate_source_words', '')} | "
            f"{row.get('theorem_like_environments', '')} | {row.get('proof_environments', '')} | "
            f"{row['source_score']} |"
        )
    lines += [
        "",
        "## Screening limitations",
        "",
        "- Counts are structural signals from TeX, not correctness judgments.",
        "- Word counts include some front matter and bibliography text.",
        "- Journal publication is recorded but is not treated as proof of correctness.",
        "- Papers must still pass two unchanged-source audits and theorem-dossier extraction.",
        "- Cross-area duplicates are assigned to only one area.",
        "",
        f"The source-screened reserve contains {len(rejected)} additional candidates.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-date", default="2025-01-01")
    parser.add_argument("--until-date", default=date.today().isoformat())
    parser.add_argument("--max-oai-pages", type=int, default=2)
    parser.add_argument("--source-candidates-per-area", type=int, default=12)
    parser.add_argument("--selected-per-area", type=int, default=6)
    parser.add_argument("--request-delay", type=float, default=3.0)
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("local_datasets/recent_math_candidates_v1"),
    )
    args = parser.parse_args()
    if args.selected_per_area > args.source_candidates_per_area:
        parser.error("selected-per-area cannot exceed source-candidates-per-area")

    harvested: dict[str, dict[str, object]] = {}
    memberships: dict[str, set[str]] = defaultdict(set)
    for area, set_specs in AREAS.items():
        for set_spec in set_specs:
            print(f"Harvesting {set_spec}", flush=True)
            for row in harvest_set(set_spec, args.from_date, args.until_date, args.max_oai_pages):
                arxiv_id = str(row["arxiv_id"])
                if row.get("license") and str(row.get("created", "")) >= args.from_date:
                    harvested.setdefault(arxiv_id, row)
                    memberships[arxiv_id].add(area)
            time.sleep(args.request_delay)

    by_area: dict[str, list[dict[str, object]]] = defaultdict(list)
    assigned: set[str] = set()
    for area in AREAS:
        choices = []
        for arxiv_id, row in harvested.items():
            if area not in memberships[arxiv_id]:
                continue
            candidate = dict(row)
            candidate["area"] = area
            candidate["metadata_score"] = metadata_score(candidate)
            choices.append(candidate)
        choices.sort(key=lambda row: (float(row["metadata_score"]), row["updated"]), reverse=True)
        for row in choices:
            if row["arxiv_id"] not in assigned:
                by_area[area].append(row)
                assigned.add(str(row["arxiv_id"]))
            if len(by_area[area]) >= args.source_candidates_per_area:
                break

    screened = [row for area in AREAS for row in by_area[area]]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    download_sources(screened, args.output_dir / "sources", args.request_delay)
    for row in screened:
        row["source_score"] = source_score(row)

    selected = []
    rejected = []
    for area in AREAS:
        rows = sorted(by_area[area], key=lambda row: float(row["source_score"]), reverse=True)
        selected.extend(rows[: args.selected_per_area])
        rejected.extend(rows[args.selected_per_area :])

    payload = {
        "dataset": "recent_math_candidates_v1",
        "generated_at": date.today().isoformat(),
        "selection_status": "provisional_pending_baseline_audit",
        "selection_policy": {
            "date_range": [args.from_date, args.until_date],
            "allowed_licenses": sorted(set(ALLOWED_LICENSES.values())),
            "areas": AREAS,
            "selected_per_area": args.selected_per_area,
            "source_candidates_per_area": args.source_candidates_per_area,
            "proof_text_policy": "verbatim source only; no authored bridging proofs",
        },
        "acknowledgement": "Thank you to arXiv for use of its open access interoperability.",
        "selected": selected,
        "reserve": rejected,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )
    (args.output_dir / "README.md").write_text(markdown_report(selected, rejected))
    print(f"Selected {len(selected)} candidates; reserve {len(rejected)}", flush=True)


if __name__ == "__main__":
    main()
