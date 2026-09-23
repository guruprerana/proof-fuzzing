#!/usr/bin/env python3
"""Clean the 2025 MIT 18.785 PDF text without rewriting its mathematics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


LECTURES = range(1, 15)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(text: str) -> str:
    # Poppler exposes large TeX delimiters as C0 codes in these PDFs. The
    # paired codes below are delimiter glyphs, not prose characters.
    text = text.translate({
        0x01: None,
        0x10: "(",
        0x11: ")",
        0x12: "[",
        0x13: "]",
        0x14: "(",
        0x15: ")",
        0xAD: "-",
    })
    # The PDF's mapsto/right-arrow constructions are emitted as a literal 7
    # (the TeX mapsto hook) followed by an arrow, and minus-plus-arrow for a
    # long right arrow. These replacements recover the encoded symbols.
    text = text.replace("7−→", "↦").replace("7→", "↦").replace("−→", "→")
    text = re.sub(r"(?m)^18\.785 Number theory I\s+Fall 2025\s*$", "", text)
    text = re.sub(r"(?m)^Lecture #\d+\s+\d+/\d+/2025\s*$", "", text)
    text = re.sub(r"(?m)^\s*Lecture by Andrew V\. Sutherland\s*$", "", text)
    text = re.sub(r"(?m)^\s*18\.785 Fall 2025, Lecture #\d+, Page \d+\s*$", "", text)
    # Join explicit end-of-line word hyphenation while retaining mathematical
    # minus signs and hyphens that are not immediately followed by a lowercase word.
    text = re.sub(r"([A-Za-z]{2,})-\n([a-z]{2,})", r"\1\2\n", text)
    text = re.sub(r"\n\s*([.,;:])(?=\s|$)", r"\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    bad = [
        char for char in text
        if unicodedata.category(char) == "Cc" and char not in "\n\t"
    ]
    if bad or "\ufffd" in text:
        codes = sorted({f"U+{ord(char):04X}" for char in bad})
        raise ValueError(f"Unresolved extraction characters: {codes}")
    return text.strip() + "\n"


def build(source_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "course": "MIT 18.785 Number Theory I",
        "term": "Fall 2025",
        "source_url": "https://math.mit.edu/classes/18.785/2025/lectures.html",
        "lectures": {},
    }
    for number in LECTURES:
        pdf = source_dir / f"LectureNotes{number}.pdf"
        extracted = source_dir / f"LectureNotes{number}.txt"
        output = clean(extracted.read_text())
        output_path = output_dir / f"lecture_{number:02d}.txt"
        output_path.write_text(output)
        manifest["lectures"][str(number)] = {
            "source_pdf": pdf.name,
            "source_pdf_sha256": sha256(pdf),
            "raw_extraction_sha256": sha256(extracted),
            "cleaned_text": output_path.name,
            "cleaned_text_sha256": hashlib.sha256(output.encode()).hexdigest(),
            "word_count": len(output.split()),
        }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources/number_theory_2025"),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources/number_theory_2025/cleaned"),
    )
    args = parser.parse_args()
    manifest = build(args.source_dir, args.output_dir)
    for number, row in manifest["lectures"].items():
        print(number, row["word_count"], row["cleaned_text_sha256"])


if __name__ == "__main__":
    main()
