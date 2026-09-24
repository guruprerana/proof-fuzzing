#!/usr/bin/env python3
"""Build two discovery dossiers from verbatim text extracted from published PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCES = (
    {
        "example_id": "open_logic_first_order_completeness",
        "filename": "open-logic-complete.txt",
        "pdf_filename": "open-logic-complete.pdf",
        "pdf_sha256": "e17ac6f54723999b727b56b60f864a969f2b7c883be5ce7149f13472a0ee14ae",
        "start": "\fChapter 23\n\nThe Completeness Theorem",
        "end": "\fChapter 24\n\nBeyond First-order Logic",
        "problem": (
            "Establish the first-order completeness theorem and the accompanying "
            "compactness and downward Löwenheim–Skolem consequences developed in "
            "Chapter 23."
        ),
        "title": "The Completeness Theorem (Chapter 23)",
        "topic": "mathematical logic",
        "source_author": "Open Logic Project",
        "source_url": "https://builds.openlogicproject.org/open-logic-complete.pdf",
        "source_revision": "9620cc7 (2026-07-12)",
        "source_pages": "347–365 (PDF pages 368–386)",
        "license": "CC BY 4.0",
        "license_url": "https://openlogicproject.org/olp-license/",
        "attribution": (
            "“The Completeness Theorem,” Chapter 23 of The Open Logic Text, "
            "by the Open Logic Project, licensed under CC BY 4.0."
        ),
    },
    {
        "example_id": "mit_18905_poincare_duality_sequence",
        "filename": "MIT18_905F16_lecture_notes.txt",
        "pdf_filename": "MIT18_905F16_lecture_notes.pdf",
        "pdf_sha256": "5c6899e1299412471513e4dbf8423937f85e8227650c19238cd7a5e3f9f610ea",
        "start": "\n31     Local coefficients and orientations",
        "end": "\fBibliography",
        "problem": (
            "Develop local coefficients and orientations through the local-to-global "
            "argument, cap products, and the fully relative Poincaré duality theorem, "
            "then derive the applications in Lectures 31–38."
        ),
        "title": "Local Coefficients, Orientations, and Poincaré Duality (Lectures 31–38)",
        "topic": "algebraic topology",
        "source_author": "Haynes Miller; notes based in part on Sanath Devalapurkar",
        "source_url": (
            "https://ocw.mit.edu/courses/18-905-algebraic-topology-i-fall-2016/"
            "pages/lecture-notes/"
        ),
        "source_revision": "MIT 18.905, Fall 2016 lecture notes",
        "source_pages": "83–107",
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://ocw.mit.edu/pages/privacy-and-terms-of-use/",
        "attribution": (
            "Lectures 31–38 from 18.905 Algebraic Topology I, Fall 2016, "
            "Haynes Miller, MIT OpenCourseWare."
        ),
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(text: str, start: str, end: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Expected unique extraction markers: {start!r}, {end!r}")
    begin = text.index(start) + (1 if start.startswith("\f") else 1)
    finish = text.index(end, begin)
    return text[begin:finish].strip() + "\n"


def build(source_dir: Path) -> dict[str, object]:
    records = []
    for spec in SOURCES:
        pdf = source_dir / spec["pdf_filename"]
        text_path = source_dir / spec["filename"]
        if sha256(pdf) != spec["pdf_sha256"]:
            raise ValueError(f"Unexpected source PDF checksum: {pdf}")
        proof = extract(text_path.read_text(), spec["start"], spec["end"])
        metadata = {
            "dataset": "internet_sourced_dossiers_v1",
            "topic": spec["topic"],
            "title": spec["title"],
            "level": "graduate",
            "correctness": True,
            "cohesive": True,
            "internet_sourced": True,
            "exposition": "verbatim_pdf_text_extraction",
            "actual_word_count": len(proof.split()),
            "source_author": spec["source_author"],
            "source_url": spec["source_url"],
            "source_revision": spec["source_revision"],
            "source_pages": spec["source_pages"],
            "source_pdf_sha256": spec["pdf_sha256"],
            "source_text_sha256": hashlib.sha256(proof.encode()).hexdigest(),
            "license": spec["license"],
            "license_url": spec["license_url"],
            "attribution": spec["attribution"],
            "transformation": "pdftotext -layout; contiguous excerpt; no authored proof text",
            "extraction_start_marker": spec["start"].lstrip("\f\n"),
            "extraction_end_marker_exclusive": spec["end"].lstrip("\f\n"),
        }
        records.append({
            "example_id": spec["example_id"],
            "problem": spec["problem"],
            "proof": proof,
            "metadata": metadata,
        })
    return {
        "dataset": "internet_sourced_dossiers_v1",
        "description": (
            "Two discovery-only graduate proof dossiers copied as contiguous text "
            "excerpts from openly licensed, internet-published sources."
        ),
        "discovery": records,
        "heldout": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path,
        default=Path("local_datasets/archive/superseded_proof_datasets_2026-09-21/source_materials/internet_sourced_dossiers_v1_sources"),
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("local_datasets/archive/superseded_proof_datasets_2026-09-21/generated_proof_datasets/internet_sourced_dossiers_v1.json"),
    )
    args = parser.parse_args()
    payload = build(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    for row in payload["discovery"]:
        print(row["example_id"], row["metadata"]["actual_word_count"])


if __name__ == "__main__":
    main()
