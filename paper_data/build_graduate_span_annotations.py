"""Build the manually reviewed graduate-course span annotations."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESULTS = (
    ROOT
    / "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/results.json"
)
DATASET = ROOT / "local_datasets/graduate_course_dossiers_v1.json"
OUTPUT = ROOT / "paper_data/span_of_influence_annotations/graduate_course.json"

# Values are physical line numbers in the original dossier. Each endpoint was
# reviewed against the mutation explanation and surrounding proof. The builder
# maps these anchors into the mutated proof before counting the span.
END_ORIGINAL_BY_SHA_PREFIX = {
    # analysis_convergence_lp
    "c254f8b7": 1154,
    "d581da4d": 1052,
    "ad474e66": 704,
    "d0e899f3": 704,
    "d10aae2e": 704,
    "2c6b41aa": 1052,
    "affc4dce": 1052,
    # analysis_differential_operators_wavefront_spectral
    "d487c105": 831,
    "dd21b3c2": 200,
    "79b39033": 464,
    "9cdac481": 1376,
    "88fba4cf": 966,
    "6f1ca17c": 1294,
    "e309497e": 941,
    "c3da7426": 1138,
    "48215c3a": 1325,
    "ab1e40ef": 200,
    # analysis_measures_integration_hilbert
    "064325f0": 1252,
    "cb95496f": 1257,
    "9ca6f7f6": 1142,
    "63cf52bd": 721,
    "78152f42": 288,
    "3d8e9b6d": 767,
    "b4571d4f": 767,
    "5b5af2ac": 655,
    "e6bff154": 767,
    "7a8e6865": 767,
    # geometry_fredholm_smale_transversality
    "464ca6b4": 504,
    "214e2985": 112,
    "f5c57109": 1041,
    "b7af46c1": 304,
    "66456246": 504,
    "7d58f7ea": 504,
    "0623f90c": 369,
    # nt_dedekind_domains_etale_algebras
    "05cee308": 321,
    "06ce67f2": 841,
    "612f3ab7": 418,
    "aba9f2c7": 321,
    "e6885db8": 220,
    "ec10d1f8": 793,
    "4d689d9f": 130,
    "ff90fa46": 868,
    "a0ef2df9": 301,
    # nt_global_fields_geometry_numbers
    "1e55327e": 320,
    "b0f07542": 351,
    "9b6d9c26": 333,
    "820283e0": 540,
    "5a97f108": 540,
    "4c57ff6f": 320,
    "d653966c": 540,
    "24ec8cad": 505,
    "fa0a23f9": 885,
    # nt_ideal_norms_dedekind_kummer
    "33f62b39": 494,
    "4c39076f": 644,
    "8945b595": 249,
    "3d3a3672": 729,
    "bbd9124e": 221,
    "99cbb237": 254,
    "17ad801f": 360,
    "8d9f5e37": 726,
    "eb57fde6": 245,
    "da994b53": 726,
    # nt_local_fields_hensel_complete_dvrs
    "0accdf8f": 758,
    "b30cf7d8": 360,
    "7d4fec86": 758,
    "23f14808": 331,
    "7ac4ca99": 293,
    "d299cb07": 580,
    "f9cadc71": 293,
    "7a3171bf": 293,
    # topology_homological_algebra_kunneth
    "333fcb36": 529,
    "41bb54c0": 205,
    "4c178cbf": 614,
    "b995d18b": 614,
    "514c1462": 551,
    "de557d53": 205,
    "e19dab6b": 551,
    # topology_relative_homology_excision
    "f6791aa9": 59,
    "bada1f67": 75,
    "dad00100": 75,
    "7485c2fb": 622,
    "f4bf4125": 16,
    "fe77aff5": 249,
    "2595b2a2": 249,
}

MEDIUM_CONFIDENCE = {
    "9ca6f7f6",  # a changed standing definition is reused across the dossier
    "464ca6b4",  # compact-operator definition is reused through the section
    "820283e0",  # fundamental-domain definition and dependent propositions
    "5a97f108",
    "d653966c",
}

HUNK = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def apply_diff(original: str, diff: str) -> tuple[list[str], dict[int, int], list[int]]:
    old_lines = original.split("\n")
    new_lines: list[str] = []
    old_to_new: dict[int, int] = {}
    changed_new_lines: list[int] = []
    old_cursor = 1
    lines = diff.split("\n")
    index = 0
    while index < len(lines):
        match = HUNK.match(lines[index])
        if not match:
            index += 1
            continue
        hunk_old = int(match.group(1))
        while old_cursor < hunk_old:
            new_lines.append(old_lines[old_cursor - 1])
            old_to_new[old_cursor] = len(new_lines)
            old_cursor += 1
        index += 1
        while index < len(lines) and not lines[index].startswith("@@"):
            line = lines[index]
            if line.startswith(" "):
                new_lines.append(line[1:])
                old_to_new[old_cursor] = len(new_lines)
                old_cursor += 1
            elif line.startswith("-"):
                old_cursor += 1
            elif line.startswith("+"):
                new_lines.append(line[1:])
                changed_new_lines.append(len(new_lines))
            elif line.startswith("\\ No newline at end of file"):
                pass
            elif line == "":
                break
            index += 1
    while old_cursor <= len(old_lines):
        new_lines.append(old_lines[old_cursor - 1])
        old_to_new[old_cursor] = len(new_lines)
        old_cursor += 1
    return new_lines, old_to_new, changed_new_lines


def is_countable(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("%"):
        return False
    return not re.fullmatch(
        r"\\(?:begin|end)\{[^}]+\}|\\label\{[^}]+\}|\\\[|\\\]", stripped
    )


def compact_first_paragraph(text: str) -> str:
    paragraph = text.strip().split("\n\n", 1)[0]
    return " ".join(paragraph.split())


def main() -> None:
    results = json.loads(RESULTS.read_text())
    dataset = json.loads(DATASET.read_text())
    proofs = {row["example_id"]: row["proof"] for row in dataset["heldout"]}
    annotations = []
    used_prefixes: set[str] = set()
    for candidate_index, result in enumerate(results, 1):
        if result.get("valid") is not True:
            continue
        prefix = result["mutation_sha256"][:8]
        if prefix not in END_ORIGINAL_BY_SHA_PREFIX:
            raise ValueError(f"missing endpoint for candidate {candidate_index}: {prefix}")
        used_prefixes.add(prefix)
        mutated, old_to_new, changed = apply_diff(
            proofs[result["proof_id"]], result["mutation_diff"]
        )
        start = min(changed)
        original_end = END_ORIGINAL_BY_SHA_PREFIX[prefix]
        # When the selected endpoint itself belongs to a replaced block, its
        # mutated counterpart is the final added line in that block.
        mapped_end = old_to_new.get(original_end, max(changed))
        end = max(max(changed), mapped_end)
        span = sum(is_countable(line) for line in mutated[start - 1 : end])
        misses = sum(
            review.get("detection") == "missed" for review in result["reviews"]
        )
        if end == max(changed):
            rationale = (
                "The changed assertion has no later direct consumer before it is packaged; "
                "the final changed line is therefore the endpoint."
            )
        else:
            rationale = (
                f"The changed object remains a direct input to the enclosing argument through "
                f"line {end}; later text treats the resulting claim as an opaque subresult."
            )
        annotations.append(
            {
                "dataset": "graduate_course",
                "candidate_index": candidate_index,
                "proof_id": result["proof_id"],
                "arm": result["arm"],
                "successful": misses > 0,
                "missed_reviews": misses,
                "mutation_start_line": start,
                "influence_end_line": end,
                "span_lines": span,
                "span_lower": span,
                "span_upper": span,
                "confidence": "medium" if prefix in MEDIUM_CONFIDENCE else "high",
                "mutated_object": compact_first_paragraph(result["introduced_error"]),
                "endpoint_rationale": rationale,
                "endpoint_excerpt": mutated[end - 1].strip(),
                "annotator": "codex-graduate-course",
            }
        )
    unused = END_ORIGINAL_BY_SHA_PREFIX.keys() - used_prefixes
    if unused:
        raise ValueError(f"unused endpoint mappings: {sorted(unused)}")
    if len(annotations) != 98:
        raise ValueError(f"expected 98 annotations, found {len(annotations)}")
    OUTPUT.write_text(json.dumps(annotations, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
