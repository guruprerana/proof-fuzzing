#!/usr/bin/env python3
"""Create source-faithful, mutation-ready views of the recent research dossiers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


PILOT_IDS = {"arxiv_2507_04819", "arxiv_2312_00701", "arxiv_2605_10535"}

SEMANTIC_PREAMBLE_COMMANDS = re.compile(
    r"^\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand|"
    r"DeclareMathOperator\*?|DeclarePairedDelimiter\w*|newtheorem|theoremstyle|"
    r"newenvironment|renewenvironment|def|gdef|let)\b"
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def strip_comments(text: str) -> tuple[str, int]:
    """Remove TeX comments while preserving escaped percent signs and newlines."""
    output = []
    removed = 0
    for line in text.split("\n"):
        cut = len(line)
        position = 0
        while True:
            found = line.find("%", position)
            if found < 0:
                break
            backslashes = 0
            cursor = found - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = found
                removed += 1
                break
            position = found + 1
        output.append(line[:cut].rstrip())
    return "\n".join(output), removed


def brace_delta(text: str) -> int:
    delta = 0
    for index, char in enumerate(text):
        if char not in "{}":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            delta += 1 if char == "{" else -1
    return delta


def defined_symbol(block: str) -> tuple[str, str] | None:
    """Return (kind, name) for a retained TeX definition when recognizable."""
    environment = re.match(
        r"\\(?:newtheorem\*?|newenvironment|renewenvironment)\s*\{([^}]+)\}",
        block,
    )
    if environment:
        return "environment", environment.group(1)
    macro = re.match(
        r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand|"
        r"DeclareMathOperator\*?|DeclarePairedDelimiter\w*)\s*"
        r"(?:\{\\([A-Za-z@]+)\}|\\([A-Za-z@]+))",
        block,
    )
    if macro:
        return "macro", macro.group(1) or macro.group(2)
    primitive = re.match(r"\\(?:def|gdef|let)\s*\\([A-Za-z@]+)", block)
    if primitive:
        return "macro", primitive.group(1)
    return None


def symbol_is_used(kind: str, name: str, text: str) -> bool:
    if kind == "environment":
        return bool(re.search(rf"\\begin\{{{re.escape(name)}\}}", text))
    return bool(re.search(rf"\\{re.escape(name)}(?![A-Za-z@])", text))


def semantic_preamble(preamble: str, body: str) -> tuple[str, int, int]:
    lines = preamble.split("\n")
    retained = []
    index = 0
    while index < len(lines):
        stripped = lines[index].lstrip()
        if not SEMANTIC_PREAMBLE_COMMANDS.match(stripped):
            index += 1
            continue
        block = [lines[index].strip()]
        depth = brace_delta(lines[index])
        index += 1
        while index < len(lines) and depth > 0:
            block.append(lines[index].rstrip())
            depth += brace_delta(lines[index])
            index += 1
        retained.append("\n".join(block).strip())
    # Preserve first occurrence only; source preambles occasionally repeat declarations.
    unique = list(dict.fromkeys(item for item in retained if item))

    # Large source bundles often contain drawing helpers and notation from unrelated
    # component files. Retain definitions used by the live manuscript, plus their
    # transitive macro dependencies. Unrecognized semantic declarations are retained
    # conservatively.
    recognized = [(block, defined_symbol(block)) for block in unique]
    selected: set[int] = {
        index
        for index, (block, symbol) in enumerate(recognized)
        if symbol is None or symbol_is_used(symbol[0], symbol[1], body)
    }
    changed = True
    while changed:
        changed = False
        selected_text = "\n".join(recognized[index][0] for index in selected)
        for index, (_, symbol) in enumerate(recognized):
            if index in selected or symbol is None:
                continue
            if symbol_is_used(symbol[0], symbol[1], selected_text):
                selected.add(index)
                changed = True
    filtered = [block for index, (block, _) in enumerate(recognized) if index in selected]
    return "\n".join(filtered).strip(), len(filtered), len(unique) - len(filtered)


def remove_bibliography(body: str) -> tuple[str, int]:
    count = 0
    body, found = re.subn(
        r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
        "\n",
        body,
        flags=re.DOTALL,
    )
    count += found
    body, found = re.subn(
        r"^[ \t]*\\(?:bibliography|bibliographystyle|printbibliography)"
        r"(?:\[[^\]]*\])?\s*(?:\{[^}]*\})?[ \t]*$",
        "",
        body,
        flags=re.MULTILINE,
    )
    count += found
    return body, count


def replace_graphics(body: str) -> tuple[str, int]:
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}")

    def replacement(match: re.Match[str]) -> str:
        filename = match.group(1)
        return f"\\textit{{[Figure source {filename} omitted from the text-only dossier.]}}"

    return pattern.subn(replacement, body)


def braced_argument(text: str, command: str) -> str | None:
    """Extract a possibly nested braced argument to a TeX command."""
    match = re.search(rf"\\{command}(?:\[[^]]*\])?\s*\{{", text)
    if not match:
        return None
    start = match.end()
    depth = 1
    index = start
    while index < len(text) and depth:
        if text[index] in "{}" and (index == 0 or text[index - 1] != "\\"):
            depth += 1 if text[index] == "{" else -1
        index += 1
    return text[start:index - 1].strip() if depth == 0 else None


def replace_inline_tikz_figures(body: str) -> tuple[str, int]:
    """Replace drawing code with its source caption and label."""
    pattern = re.compile(r"\\begin\{figure(\*?)\}(.*?)\\end\{figure\1\}", re.DOTALL)
    replaced = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal replaced
        content = match.group(2)
        if "\\begin{tikzpicture}" not in content:
            return match.group(0)
        replaced += 1
        caption = braced_argument(content, "caption")
        labels = list(dict.fromkeys(re.findall(r"\\label\{([^}]+)\}", content)))
        lines = [
            "\\begin{quote}",
            "\\textit{[Source TikZ figure omitted from the text-only dossier.]}",
        ]
        if caption:
            lines.append(f"\\textbf{{Caption.}} {caption}")
        lines.extend(f"\\label{{{label}}}" for label in labels)
        lines.append("\\end{quote}")
        return "\n".join(lines)

    return pattern.sub(replacement, body), replaced


def remove_pre_abstract_title_blocks(body: str) -> tuple[str, int]:
    abstract = body.find("\\begin{abstract}")
    if abstract < 0:
        return body, 0
    prefix, suffix = body[:abstract], body[abstract:]
    prefix, count = re.subn(
        r"\\begin\{center\}.*?\\end\{center\}", "", prefix, flags=re.DOTALL
    )
    return prefix + suffix, count


def normalize_layout(body: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    body, counts["front_matter_commands_removed"] = re.subn(
        r"^[ \t]*\\(?:maketitle|tableofcontents)[ \t]*$", "", body, flags=re.MULTILINE
    )
    body, counts["standalone_layout_commands_removed"] = re.subn(
        r"^[ \t]*\\(?:newpage|clearpage|pagebreak|small|normalsize|large|Large|"
        r"raggedbottom|allowdisplaybreaks|sloppy)[ \t]*(?:\[[^\]]*\])?[ \t]*$",
        "",
        body,
        flags=re.MULTILINE,
    )
    body, counts["inline_noindent_removed"] = re.subn(r"\\noindent\s*", "", body)
    body = body.replace("\t", "    ")
    body = "\n".join(line.rstrip() for line in body.split("\n"))
    body, counts["blank_line_runs_collapsed"] = re.subn(r"\n{4,}", "\n\n\n", body)
    return body.strip() + "\n", counts


def clean_record(row: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    source = str(row["proof"])
    uncommented, comment_markers = strip_comments(source)
    begin = uncommented.find("\\begin{document}")
    end = uncommented.rfind("\\end{document}")
    if begin < 0 or end <= begin:
        raise ValueError(f"No complete document wrapper in {row['example_id']}")
    preamble = uncommented[:begin]
    body = uncommented[begin + len("\\begin{document}"):end]
    body, bibliography_blocks = remove_bibliography(body)
    macros, macro_count, unused_macro_count = semantic_preamble(preamble, body)
    body, graphics = replace_graphics(body)
    body, tikz_figures = replace_inline_tikz_figures(body)
    body, title_blocks = remove_pre_abstract_title_blocks(body)
    body, layout_counts = normalize_layout(body)

    metadata = dict(row["metadata"])
    title = str(metadata["title"])
    authors = ", ".join(str(author) for author in metadata["authors"])
    arxiv_id = str(metadata["arxiv_id"])
    macro_section = (
        "## Source notation definitions\n\n"
        "The following author-supplied TeX definitions are retained to interpret notation.\n\n"
        "```tex\n"
        f"{macros}\n"
        "```\n\n"
        if macros else ""
    )
    cleaned = (
        f"# {title}\n\n"
        f"> Source: {authors}, arXiv:{arxiv_id}. {metadata['license']}.\n"
        "> Mechanically cleaned from the verified primary TeX source; mathematical "
        "prose and display order are preserved.\n\n"
        f"{macro_section}"
        "## Manuscript\n\n"
        f"{body}"
    )

    clean_metadata = dict(metadata)
    clean_metadata.update({
        "dataset": "recent_math_research_dossiers_clean_v1",
        "exposition": "mechanically_cleaned_verbatim_arxiv_tex_body",
        "parent_dataset": "recent_math_research_dossiers_v1",
        "parent_proof_sha256": digest(source),
        "source_text_sha256": digest(cleaned),
        "actual_word_count": len(cleaned.split()),
        "transformation": (
            "Removed TeX wrapper/package/front-matter/layout commands, comments, and "
            "bibliography listings; retained author-defined notation macros; replaced "
            "image inclusions and inline drawing code with text markers while retaining "
            "captions and labels; no "
            "mathematical proof prose was authored."
        ),
    })
    cleaned_row = {
        "example_id": row["example_id"],
        "problem": row["problem"],
        "proof": cleaned,
        "metadata": clean_metadata,
    }
    audit = {
        "example_id": row["example_id"],
        "arxiv_id": arxiv_id,
        "source_sha256": digest(source),
        "clean_sha256": digest(cleaned),
        "source_chars": len(source),
        "clean_chars": len(cleaned),
        "source_words": len(source.split()),
        "clean_words": len(cleaned.split()),
        "comments_removed": comment_markers,
        "semantic_preamble_definitions_retained": macro_count,
        "unused_preamble_definitions_removed": unused_macro_count,
        "bibliography_blocks_or_commands_removed": bibliography_blocks,
        "figure_inclusions_replaced": graphics,
        "inline_tikz_figures_replaced": tikz_figures,
        "pre_abstract_title_blocks_removed": title_blocks,
        **layout_counts,
        "policy": "mechanical presentation cleanup only; original source retained separately",
    }
    return cleaned_row, audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_clean_v1.json"),
    )
    parser.add_argument(
        "--pilot-output",
        type=Path,
        default=Path("local_datasets/generated_proof_datasets/recent_math_research_dossiers_clean_pilot3_v1.json"),
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=Path("local_datasets/recent_math_cleaned_v1/audits"),
    )
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    cleaned: dict[str, object] = {
        "dataset": "recent_math_research_dossiers_clean_v1",
        "description": "Mechanically cleaned, paper-disjoint views of the accepted recent research corpus.",
        "parent_dataset": str(args.input),
        "split_policy": payload["split_policy"],
        "acknowledgement": payload["acknowledgement"],
    }
    all_audits = []
    for split in ("discovery", "heldout"):
        rows = []
        for row in payload[split]:
            clean_row, audit = clean_record(row)
            rows.append(clean_row)
            all_audits.append(audit)
        cleaned[split] = rows

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_dir.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n")
    pilot_rows = [row for row in cleaned["discovery"] if row["example_id"] in PILOT_IDS]
    pilot = {
        "dataset": "recent_math_research_dossiers_clean_pilot3_v1",
        "description": "Cleaned three-paper discovery-only subset; fresh-run replacement for the raw-source pilot.",
        "parent_dataset": str(args.output),
        "discovery": pilot_rows,
        "heldout": [],
    }
    args.pilot_output.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n")
    for audit in all_audits:
        (args.audit_dir / f"{audit['example_id']}.json").write_text(
            json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
        )
        print(audit["arxiv_id"], audit["source_words"], "->", audit["clean_words"])


if __name__ == "__main__":
    main()
