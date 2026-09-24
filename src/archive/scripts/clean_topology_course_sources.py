#!/usr/bin/env python3
"""Create source-faithful, model-readable excerpts from the 18.905 TeX sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


EXPECTED_COMMIT = "3f5d3189e2082716a69fccc1711d02ed848552d2"

GROUPS = {
    "lectures_01_08": [
        "lec-1-intro.tex", "lec-2-simplices.tex", "lec-3-categories.tex",
        "lec-4-more-on-categories.tex", "lec-5-homotopy.tex",
        "lec-6-homotopy-invariance.tex", "lec-7-eilenberg-zilber.tex",
        "lec-8-relative-homology.tex",
    ],
    "lectures_09_16": [
        "lec-9-lexseq.tex",
        "lec-10-eilenberg-steenrod.tex", "lec-11-locality-principle.tex",
        "lec-12-mayer-vietoris.tex", "lec-13-locality-end-ish.tex",
        "lec-14-ending-locality-and-cw-complexes.tex",
        "lec-15-cw-complexes-cellular-homology.tex",
        "lec-16-homology-cw-complexes.tex",
    ],
    "lectures_17_22": [
        "lec-17-RPn.tex",
        "lec-18-euler-char.tex", "lec-19-eulers-thm.tex",
        "lec-20-tensor-products.tex", "lec-21-tensor-and-tor.tex",
        "lec-22-more-on-tor.tex",
    ],
    "lectures_23_30": [
        "lec-23-direct-limits.tex", "lec-24-uct.tex",
        "lec-25-kunneth-eilenberg-zilber.tex", "lec-26-cohomology.tex",
        "lec-27-ext-cup-product.tex", "lec-28-uct-products-in-cohomology.tex",
        "lec-29-cup-products-contd.tex", "lec-30-surfaces-bilinear-forms.tex",
    ],
}


def strip_comment(line: str) -> str:
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def clean_tex(text: str) -> str:
    text = "\n".join(strip_comment(line).rstrip() for line in text.splitlines())
    text = re.sub(
        r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}",
        "\n[Figure omitted; surrounding mathematical text is unchanged.]\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"\\(?:section|subsection|subsubsection)\*?\{([^{}]+)\}", r"\n## \1\n", text)
    text = re.sub(r"\\label\{[^{}]*\}", "", text)
    text = re.sub(r"\\index\{[^{}]*\}", "", text)
    text = re.sub(r"\\(?:begin|end)\{(?:center|flushleft|flushright)\}", "", text)
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def build(source_repo: Path, output_dir: Path) -> dict[str, object]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source_repo, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if commit != EXPECTED_COMMIT:
        raise ValueError(f"Unexpected algtop-notes commit: {commit}")
    input_dir = source_repo / "old-905"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"source_commit": commit, "groups": {}}
    for group, filenames in GROUPS.items():
        chunks = []
        inputs = []
        for filename in filenames:
            path = input_dir / filename
            raw = path.read_text()
            chunks.append(clean_tex(raw))
            inputs.append({
                "path": f"old-905/{filename}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
        output = "\n".join(chunks).strip() + "\n"
        output_path = output_dir / f"{group}.md"
        output_path.write_text(output)
        manifest["groups"][group] = {
            "inputs": inputs,
            "output": output_path.name,
            "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
            "word_count": len(output.split()),
        }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-repo", type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources/topology/algtop-notes-source"),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources/topology/cleaned_tex"),
    )
    args = parser.parse_args()
    manifest = build(args.source_repo, args.output_dir)
    for name, row in manifest["groups"].items():
        print(name, row["word_count"], row["output_sha256"])


if __name__ == "__main__":
    main()
