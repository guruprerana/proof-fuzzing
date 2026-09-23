#!/usr/bin/env python3
"""Recover clean text from the MIT 18.125 Fall 2003 lecture PDFs.

The PDFs were produced by an early pdfTeX version.  Their embedded Type 1
fonts preserve TeX glyph names, but several ToUnicode entries are absent or
incorrect.  In particular, ordinary PDF text extraction emits U+FFFD for
integrals, sums, epsilon, large set operators, and proof-ending squares.

This script uses the glyph names already encoded in each PDF as the source of
truth.  It converts the PDF to PostScript, adds corrected GlyphNames2Unicode
entries to each embedded font, converts the result back to a temporary PDF,
and extracts fixed-layout UTF-8 text.  It does not OCR or reconstruct symbols
from mathematical context.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path


LECTURES = range(1, 25)

# These names occur in the Computer Modern/AMS fonts embedded in the source
# PDFs.  Ghostscript's stock glyph list either omits them or assigns the old
# Adobe epsilon1 mapping (U+01EB), which is not the TeX mathematical glyph.
GLYPH_OVERRIDES = {
    "epsilon1": "03F5",             # GREEK LUNATE EPSILON SYMBOL
    "summationtext": "2211",        # N-ARY SUMMATION
    "summationdisplay": "2211",     # N-ARY SUMMATION
    "integraltext": "222B",         # INTEGRAL
    "integraldisplay": "222B",      # INTEGRAL
    "uniondisplay": "22C3",         # N-ARY UNION
    "intersectiondisplay": "22C2",  # N-ARY INTERSECTION
    "negationslash": "0338",        # COMBINING LONG SOLIDUS OVERLAY
    "bardbl": "2016",               # DOUBLE VERTICAL LINE (norm bars)
    "mu": "03BC",                   # GREEK SMALL LETTER MU
    "Omega": "03A9",                # GREEK CAPITAL LETTER OMEGA
    "vextendsingle": "007C",        # vertical delimiter extender
    "vextenddouble": "2016",        # double vertical delimiter extender
    "parenleftBig": "0028",
    "parenrightBig": "0029",
    "parenleftbigg": "0028",
    "parenrightbigg": "0029",
    "parenleftBigg": "0028",
    "parenrightBigg": "0029",
    "braceleftbigg": "007B",
    "bracerightbigg": "007D",
    "braceleftBigg": "007B",
    "bracerightBigg": "007D",
    "bracelefttp": "23A7",
    "braceleftmid": "23A8",
    "braceleftbt": "23A9",
    "braceex": "23AA",
    "bracehtipupleft": "007B",
    "bracehtipupright": "007D",
    "openbullet": "2218",           # RING OPERATOR
    "parenleftbig": "0028",
    "parenrightbig": "0029",
    "square": "25A1",               # WHITE SQUARE (proof terminator)
}


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required extraction tool is not installed: {name}")


def run(*args: str) -> None:
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def unicode_patch() -> str:
    definitions = "\n".join(
        f"/{name} 16#{codepoint} def" for name, codepoint in GLYPH_OVERRIDES.items()
    )
    return f"""/FontInfo 8 dict dup begin
/GlyphNames2Unicode /Unicode /Decoding findresource dup length 32 add dict dup begin exch {{def}} forall
{definitions}
end readonly def
"""


def patch_postscript(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="latin-1")
    pattern = re.compile(r"/FontInfo\s+\d+\s+dict\s+dup\s+begin\n")
    text, count = pattern.subn(unicode_patch(), text)
    if count == 0:
        raise RuntimeError(f"No embedded-font FontInfo dictionaries found in {source}")
    destination.write_text(text, encoding="latin-1")


def clean_extracted_text(text: str) -> str:
    # The glyph-level repair turns TeX's overlaid '=' + negationslash into an
    # equals sign followed by U+0338.  Compose that exact encoded construction.
    text = re.sub(r"=\s*\u0338", "≠", text)
    text = re.sub(r"\u0338\s*=", "≠", text)
    text = re.sub(r"\u0338\s*∈", "∉", text)
    text = re.sub(r"\u0338\s*⊂", "⊄", text)
    text = re.sub(r"\u0338\s*→", "↛", text)

    # Normalize typographic encodings without applying broad NFKC to math.
    replacements = {
        "\u00ad": "",  # soft hyphen used at TeX line breaks
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "\u00a0": " ",
        "\u2212": "−",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("7−→", "↦").replace("7→", "↦").replace("−→", "→")

    # Page furniture is not part of the mathematical exposition.  Preserve
    # page boundaries as blank lines while removing repeated headers/footers.
    text = text.replace("\f", "\n\n")
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(
            r"(?:\d+\s+)?MEASURE AND INTEGRATION: LECTURE \d+(?:\s+\d+)?",
            stripped,
        ):
            continue
        if re.fullmatch(r"Date: [A-Za-z]+ \d{1,2}, 2003\.", stripped):
            continue
        if re.fullmatch(r"[1-9]", stripped):
            # Each PDF numbers its short sequence of pages 1--6. Mathematical
            # displays in these notes do not consist of a bare single digit.
            continue
        kept.append(line.rstrip())
    text = "\n".join(kept)

    # Join only explicit TeX discretionary word breaks.  Do not reflow display
    # equations, because fixed-layout extraction carries their structure.
    text = re.sub(r"(?<=[A-Za-z])-[ \t]*\n[ \t]*(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def validate(text: str, lecture: int) -> None:
    if "\ufffd" in text:
        raise ValueError(f"Lecture {lecture}: replacement character remains")
    controls = sorted(
        {ord(char) for char in text if unicodedata.category(char) == "Cc" and char != "\n"}
    )
    if controls:
        raise ValueError(f"Lecture {lecture}: control characters remain: {controls}")
    if "Proof." not in text:
        raise ValueError(f"Lecture {lecture}: extraction lost all proof markers")
    if len(text.split()) < 500:
        raise ValueError(f"Lecture {lecture}: implausibly short extraction")


def clean_lecture(pdf: Path, output: Path, lecture: int) -> None:
    with tempfile.TemporaryDirectory(prefix=f"measure_lec{lecture}_") as temporary:
        temp = Path(temporary)
        original_ps = temp / "original.ps"
        repaired_ps = temp / "repaired.ps"
        repaired_pdf = temp / "repaired.pdf"
        extracted = temp / "extracted.txt"

        run("pdftops", "-level3", str(pdf), str(original_ps))
        patch_postscript(original_ps, repaired_ps)
        run(
            "gs",
            "-q",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={repaired_pdf}",
            str(repaired_ps),
        )
        run("pdftotext", "-layout", str(repaired_pdf), str(extracted))
        text = clean_extracted_text(extracted.read_text(encoding="utf-8"))
        validate(text, lecture)
        output.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources/analysis"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "local_datasets/graduate_course_dossiers_v1_sources/analysis/measure_clean"
        ),
    )
    args = parser.parse_args()

    for tool in ("pdftops", "gs", "pdftotext"):
        require_tool(tool)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for lecture in LECTURES:
        pdf = args.source_dir / f"18125_lec{lecture}.pdf"
        if not pdf.is_file():
            raise FileNotFoundError(pdf)
        output = args.output_dir / f"18125_lec{lecture}.txt"
        clean_lecture(pdf, output, lecture)
        print(f"lecture {lecture:02d}: {len(output.read_text().split()):5d} words -> {output}")


if __name__ == "__main__":
    main()
