#!/usr/bin/env python3
"""Build a balanced 20-dossier corpus from cleaned graduate course notes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


DATASET = "graduate_course_dossiers_v1"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
OCW_TERMS_URL = "https://ocw.mit.edu/pages/privacy-and-terms-of-use/"

COURSES: dict[str, dict[str, Any]] = {
    "number_theory": {
        "course": "MIT 18.785 Number Theory I",
        "term": "Fall 2025",
        "author": "Andrew V. Sutherland",
        "url": "https://math.mit.edu/classes/18.785/2025/lectures.html",
        "license": "No explicit license located",
        "license_url": None,
        "transformation": "pdftotext -layout; deterministic header, control-glyph, arrow, and line-break cleanup; no authored proof text",
    },
    "measure": {
        "course": "MIT 18.125 Measure and Integration",
        "term": "Fall 2003",
        "author": "Jeff Viaclovsky",
        "url": "https://ocw.mit.edu/courses/18-125-measure-and-integration-fall-2003/pages/lecture-notes/",
        "license": "CC BY-NC-SA 4.0",
        "license_url": LICENSE_URL,
        "transformation": "glyph-name recovery from the source PDFs; deterministic page-furniture and line-break cleanup; no authored proof text",
        "pdfs": [],
    },
    "differential_analysis": {
        "course": "MIT 18.155 Differential Analysis",
        "term": "Fall 2013",
        "author": "Richard B. Melrose",
        "url": "https://math.mit.edu/~rbm/18-155-F13/GradAnal.pdf",
        "license": "No explicit license located",
        "license_url": None,
        "transformation": "pdftotext from the author's later consolidated edition; deterministic page-furniture, ligature, and line-break cleanup; no authored proof text",
        "pdfs": [
            ("analysis/differential_analysis/GradAnal_2013.pdf", "3918ea757dee96ad81392458c7e95612618fcaa8abf2043a5ca19189f8c454bb"),
        ],
    },
    "topology": {
        "course": "MIT 18.905 Algebraic Topology I",
        "term": "Fall 2016",
        "author": "Haynes Miller; notes by Sanath Devalapurkar",
        "url": "https://github.com/sanathdevalapurkar/algtop-notes",
        "license": "MIT",
        "license_url": "https://github.com/sanathdevalapurkar/algtop-notes/blob/3f5d3189e2082716a69fccc1711d02ed848552d2/LICENSE",
        "transformation": "comment and presentation-command removal from commit-pinned LaTeX source; mathematical LaTeX retained; no authored proof text",
    },
    "geometry": {
        "course": "MIT 18.965 Geometry of Manifolds",
        "term": "Fall 2004",
        "author": "Tomasz Mrowka",
        "url": "https://ocw.mit.edu/courses/18-965-geometry-of-manifolds-fall-2004/pages/lecture-notes/",
        "license": "CC BY-NC-SA 4.0",
        "license_url": LICENSE_URL,
        "transformation": "glyph-name recovery from the source PDFs; deterministic page-furniture, ligature, and line-break cleanup; no authored proof text",
        "pdfs": [],
    },
}

MEASURE_PDF_HASHES = {
    1: "42e993c7b1638fc70ccf16c6736ccd1a3c1f386a75f8d2cf8e9832eb3c33225e",
    2: "0197881f9bc551a5c8f2254c63eaedf7347c546ffe73bdae65d084eb4857ae1e",
    3: "fd3720f55af9afdf224602a6d54801647d54bdea6f79b208b1e8a98de27cff76",
    4: "1198a69a45b550a278d3feb58fb11ca6f11cf053137365a5cfda290300dc9934",
    5: "5ccb1f2e10b4c87cc57e67b8e8f0889c8c977f65f120535b8d29432f36300643",
    6: "fe7a85d3d9e59005412d12f5258d207094ebde529841534dbcf5f106e7fd31e0",
    7: "38f5807707e4eaf08f1111b0759238f7fc99ec2c63acf3e45179c2f84e4a8cd6",
    8: "2f24f2e5e463c039a795bcc70c06eddfc42f96c347f6809e192c6b54fc9757b1",
    9: "a50b63583345d27c1520d528272033c51df76a3b04ecb5d49249a24579780fc3",
    10: "dfc95c24e78229a5965e33067d5bc4e5c3f9342775b68de02f21f324a1926446",
    11: "09641c9c77239f08c75b73ce5370943a3306b40bc6759c0c400d7c1404bdf143",
    12: "da96cdf9037ac3acdd3358711b12ad3f7618d00896ced897342a3b9c82ff7402",
    13: "c20bda3ae3359b75ec1ec413edf7a39f9225c1dba5890db2b5ac52020036b124",
    14: "92aea37aecbef3394a183bf66b6c1262c92fa6625e1610bae98ce2884868890d",
    15: "6a82ee1dc4f42d8a673455d5335a50771753a1fbdc128a4d1ec13c82627cff02",
    16: "9c48db64e8ffcad10161fc34ed73089af5d718ff2ca3f2710ffc4e5bf6797b2c",
    17: "01e8c039765f90a6984ac83f26768fd624d5904ba40a9742fdf00fb520c0cfe4",
    18: "5beebc680d19c134506ab19d0c9760b1ced625c030913c3e6d3cb6427db39572",
    19: "652af08df2c6e8ad23dfc8d129355e99b424c6ab592b8677771bd20d165d6464",
    20: "cb3833a5f17ead46b39faf79f7de746c19a99bf6763f3535336e7083432bd2ad",
    21: "83db5161b90cae6f114e5b5180236338fa822b8f61d6df43a5682ea954a61ea1",
    22: "51a03100ef22ba14ad417576fbdcf83fd789f6fd8a719fe50de357a7db5f8d91",
    23: "d506b1c55aa8c01f80f2e703c6a8ae3a0bccfd421af0651b74086cb977fea7fb",
    24: "1f892dab26e453ec43c8ef2dd40d39d62d543dbd835cbfcf5b8407329b76f2c4",
}

GEOMETRY_PDF_HASHES = {
    "1": "5a6433da86a8d5d5c4031b79d5b2ef5ae5f15b7a05bc0b4e3ce1c68761ec5920",
    "2": "894fb86d9ead48f10ad6b80874da32367da672b0b4897ee8cb3cc7b2679f874d",
    "3": "b499e1ab39ce78f0c768be30ea83622d5b8c32d2006ce22984b4a3d157647eda",
    "4": "2561c0859ab342abcbc011b5e74191a79c3bfcdfd04f1b5d3b27375eb6d8d4d8",
    "5": "ca5d98265a571dfafbf41611c61e86700935ed0ff4a85f5b335f84e97c552d43",
    "6": "dafce41314d13e8124c90859a2ce74f06c1ff134e357e843d0a57220948f3cda",
    "7": "4d973d4a5b75e1043c752c1d1ccbab4f6b9db2ac3c05fbed003aacd2892a613a",
    "8": "b2a56327d02a3bfe4cb430e69557e86086eb05f3a2e1795c38e01fcf1f9bc708",
    "9": "5da8b7711b114170236bbd78ab285cb6881a7ede0b7c03239bbb327630d3da25",
    "10_11": "716bf25edcf963865608bb0c53268486c1420e5dab0101ded8df495d317efe03",
    "12": "a94750432e491000a8327af83f2fe168bb67cc84e8d5e00d6e343d048cf38df8",
    "13": "27ca3b3a9cf530dc336806576ebeb7eab4418553c0e85ab91a6a96cb9ef6bfce",
    "14": "3d005d783229b69ae8b22baa746d817ca8652974bc9824b8d3b806a505545382",
    "15": "e5f5560cf0db9cf0b98565ef02727ca4b8b31d7f552fe24b58cbb2fca5daed29",
    "16_17": "d6c5fb742a7678721369c8afd59f123138a84297332e25871e2b9c2972fca2a1",
    "18_19": "7326391d892e0720a4e0baf22286c499ab6a124e7856f4e00e06c237b3e785eb",
    "20": "3fdfad3f2f616616344c974301d781e0f2bf656d56a52d46e8ccc3d2867dec73",
    "21_22": "783a417fe1a45aed09b33fc91cce20987de035585701f656490c69fd48f9c4b7",
}

NT_TITLES = {
    1: "Absolute values and discrete valuations",
    2: "Localization and Dedekind domains",
    3: "Properties of Dedekind domains",
    4: "Étale algebras, norm and trace",
    5: "Dedekind extensions",
    6: "Ideal norms and the Dedekind-Kummer theorem",
    7: "Galois extensions, Frobenius elements, and the Artin map",
    8: "Complete fields and valuation rings",
    9: "Local fields and Hensel’s lemmas",
    10: "Extensions of complete DVRs",
    11: "Totally ramified extensions and Krasner’s lemma",
    12: "The different and the discriminant",
    13: "Global fields and the product formula",
    14: "The geometry of numbers",
    15: "Dirichlet’s unit theorem",
}

TOPOLOGY_TITLES = {
    1: "Introduction: singular simplices and chains",
    8: "Relative homology",
    15: "CW-complexes II",
    22: "The fundamental theorem of homological algebra",
    27: "Ext and UCT",
    33: "A plethora of products",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numbered_heading(text: str, number: int, title: str) -> re.Match[str]:
    pattern = re.compile(rf"(?m)^{number}\s{{3,}}{re.escape(title)}\s*$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"Expected one heading {number} {title!r}; found {len(matches)}")
    return matches[0]


def extract_numbered_range(
    text: str,
    start_number: int,
    start_title: str,
    end_number: int | None,
    end_title: str | None,
) -> str:
    start = numbered_heading(text, start_number, start_title).start()
    if end_number is None:
        bibliography = re.search(r"(?m)^Bibliography\s*$", text[start:])
        end = start + bibliography.start() if bibliography else len(text)
    else:
        assert end_title is not None
        end = numbered_heading(text, end_number, end_title).start()
    return text[start:end].strip() + "\n"


def extract_section_range(text: str, start: str, end: str) -> str:
    start_pattern = re.compile(rf"(?m)^\s*{re.escape(start)}\s*$")
    end_pattern = re.compile(rf"(?m)^\s*{re.escape(end)}\s*$")
    starts = list(start_pattern.finditer(text))
    ends = list(end_pattern.finditer(text))
    if len(starts) != 1 or len(ends) != 1 or ends[0].start() <= starts[0].start():
        raise ValueError(f"Non-unique or reversed section markers: {start!r}, {end!r}")
    return text[starts[0].start():ends[0].start()].strip() + "\n"


def source_files(source_dir: Path, course_key: str, lectures: list[Any] | None = None) -> list[dict[str, str]]:
    if course_key == "measure":
        assert lectures
        expected = [
            (f"analysis/18125_lec{number}.pdf", MEASURE_PDF_HASHES[number])
            for number in lectures
        ]
    elif course_key == "geometry":
        assert lectures
        expected = [
            (f"geometry/lecture{number}.pdf", GEOMETRY_PDF_HASHES[number])
            for number in lectures
        ]
    elif course_key == "number_theory":
        assert lectures
        manifest = json.loads((source_dir / "number_theory_2025/cleaned/manifest.json").read_text())
        expected = [
            (
                f"number_theory_2025/LectureNotes{number}.pdf",
                manifest["lectures"][str(number)]["source_pdf_sha256"],
            )
            for number in lectures
        ]
    elif course_key == "topology":
        assert lectures and len(lectures) == 1
        manifest = json.loads((source_dir / "topology/cleaned_tex/manifest.json").read_text())
        expected = [
            (
                f"topology/algtop-notes-source/{row['path']}",
                row["sha256"],
            )
            for row in manifest["groups"][lectures[0]]["inputs"]
        ]
    else:
        expected = COURSES[course_key]["pdfs"]
    files = []
    for relative, expected_hash in expected:
        path = source_dir / relative
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(f"Unexpected source PDF checksum: {path}")
        files.append({"path": relative, "sha256": actual_hash})
    return files


SPECS = (
    # Discovery: 4 algebra/number theory, 3 analysis, 3 topology.
    dict(split="discovery", example_id="nt_absolute_values_localization", area="algebra and number theory", pair="nt-1", course="number_theory", units=[1, 2], title="Absolute Values, Valuations, and Localization", problem="Develop absolute values and discrete valuations, then construct localization and establish its main ideal-theoretic properties."),
    dict(split="discovery", example_id="nt_dedekind_extensions", area="algebra and number theory", pair="nt-2", course="number_theory", units=[5], title="Dedekind Extensions", problem="Develop extensions of Dedekind domains, including integral closure, prime ideals above a prime, ramification, and residue degrees."),
    dict(split="discovery", example_id="nt_frobenius_complete_fields", area="algebra and number theory", pair="nt-3", course="number_theory", units=[7, 8], title="Frobenius, the Artin Map, and Complete Fields", problem="Develop Frobenius elements and the Artin map in Galois extensions, then construct completions and their valuation rings."),
    dict(split="discovery", example_id="nt_ramification_krasner_different", area="algebra and number theory", pair="nt-4", course="number_theory", units=[11, 12], title="Ramification, Krasner’s Lemma, and the Different", problem="Develop totally ramified extensions and Krasner’s lemma, then establish the theory of the different and discriminant."),
    dict(split="discovery", example_id="analysis_measure_foundations", area="analysis", pair="analysis-1", course="measure", units=list(range(1, 9)), title="Measure-Theoretic Foundations", problem="Develop sigma-algebras, measurable functions, measures, outer measure, and the initial construction and properties of the Lebesgue integral."),
    dict(split="discovery", example_id="analysis_differentiation_product_measures", area="analysis", pair="analysis-2", course="measure", units=list(range(17, 25)), title="Differentiation, Product Measures, and Signed Measures", problem="Develop differentiation of monotone functions and measures, product measures and Fubini-type results, and the decomposition theory of signed measures."),
    dict(split="discovery", example_id="analysis_test_functions_fourier_sobolev", area="analysis", pair="analysis-3", course="differential_analysis", units=[6, 7, 8, 9, 10], title="Test Functions, Distributions, Fourier Inversion, and Sobolev Embedding", problem="Develop test functions and tempered distributions through convolution, Fourier inversion, and Sobolev embedding."),
    dict(split="discovery", example_id="topology_singular_homology_homotopy", area="geometry and topology", pair="topology-1", course="topology", units=["lectures_01_08"], unit_label="Lectures 1–8", title="Singular Homology and Homotopy Invariance", problem="Construct singular homology, introduce the needed categorical language, and prove homotopy invariance and the homology cross product."),
    dict(split="discovery", example_id="topology_cw_homology_tensor", area="geometry and topology", pair="topology-2", course="topology", units=["lectures_17_22"], unit_label="Lectures 17–22", title="CW Homology, Euler Characteristic, Tensor, and Tor", problem="Compute cellular homology and Euler characteristics, then introduce tensor products, Tor, and their homological applications."),
    dict(split="discovery", example_id="geometry_manifolds_bundles_sard", area="geometry and topology", pair="topology-3", course="geometry", units=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10_11", "12", "13", "14"], unit_label="Lectures 1–14", title="Manifolds, Vector Bundles, Sard’s Theorem, and Embeddings", problem="Develop smooth manifolds and maps, vector bundles and connections, embedding constructions, Sard’s theorem, stratified spaces, fiber bundles, and Whitney’s embedding theorem."),
    # Evaluation: the same 4/3/3 area distribution with disjoint source ranges.
    dict(split="heldout", example_id="nt_dedekind_domains_etale_algebras", area="algebra and number theory", pair="nt-1", course="number_theory", units=[3, 4], title="Dedekind Domains and Étale Algebras", problem="Establish the main structure and ideal-factorization properties of Dedekind domains, then develop étale algebras, norm, and trace."),
    dict(split="heldout", example_id="nt_ideal_norms_dedekind_kummer", area="algebra and number theory", pair="nt-2", course="number_theory", units=[6], title="Ideal Norms and the Dedekind–Kummer Theorem", problem="Develop ideal norms and prove the Dedekind–Kummer theorem governing prime factorization in extensions."),
    dict(split="heldout", example_id="nt_local_fields_hensel_complete_dvrs", area="algebra and number theory", pair="nt-3", course="number_theory", units=[9, 10], title="Local Fields, Hensel’s Lemmas, and Complete DVR Extensions", problem="Develop local fields and Hensel’s lemmas, then analyze finite extensions of complete discrete valuation rings."),
    dict(split="heldout", example_id="nt_global_fields_geometry_numbers", area="algebra and number theory", pair="nt-4", course="number_theory", units=[13, 14], title="Global Fields, the Product Formula, and Geometry of Numbers", problem="Establish the product formula for global fields and develop the geometry-of-numbers machinery used in arithmetic applications."),
    dict(split="heldout", example_id="analysis_convergence_lp", area="analysis", pair="analysis-1", course="measure", units=list(range(9, 17)), title="Convergence Theorems and Lp Spaces", problem="Develop convergence theorems for the Lebesgue integral and the principal structural and approximation results for Lp spaces."),
    dict(split="heldout", example_id="analysis_measures_integration_hilbert", area="analysis", pair="analysis-2", course="differential_analysis", units=[1, 2, 3, 4, 5], title="Continuous Functions, Measures, Integration, and Hilbert Space", problem="Develop continuous-function duality, measures and measurable functions, integration, and the foundational geometry of Hilbert space."),
    dict(split="heldout", example_id="analysis_differential_operators_wavefront_spectral", area="analysis", pair="analysis-3", course="differential_analysis", units=[11, 12, 13, 14, 15, 16], title="Differential Operators, Wavefront Methods, and the Spectral Theorem", problem="Develop constant-coefficient differential operators and fundamental solutions, cone support and wavefront methods, homogeneous distributions, kernels, and the spectral theorem."),
    dict(split="heldout", example_id="topology_relative_homology_excision", area="geometry and topology", pair="topology-1", course="topology", units=["lectures_09_16"], unit_label="Lectures 9–16", title="Relative Homology, Excision, Locality, and CW Complexes", problem="Develop the long exact sequence and homology axioms, prove locality and Mayer–Vietoris results, and introduce cellular homology."),
    dict(split="heldout", example_id="topology_homological_algebra_kunneth", area="geometry and topology", pair="topology-2", course="topology", units=["lectures_23_30"], unit_label="Lectures 23–30", title="Universal Coefficients, Künneth, and Cohomology Products", problem="Develop direct limits and universal coefficients, prove Künneth and Eilenberg–Zilber results, and construct products in cohomology."),
    dict(split="heldout", example_id="geometry_fredholm_smale_transversality", area="geometry and topology", pair="topology-3", course="geometry", units=["15", "16_17", "18_19", "20", "21_22"], unit_label="Lectures 15–22", title="Fredholm Operators, Smale–Sard, Transversality, and Whitney Embedding", problem="Develop compact and Fredholm operator theory, prove the Smale–Sard theorem and parametric transversality, and establish the strong Whitney embedding theorem."),
)


def proof_for(spec: dict[str, Any], source_dir: Path) -> str:
    course = spec["course"]
    units = spec["units"]
    if course == "measure":
        chunks = [
            (source_dir / f"analysis/measure_clean/18125_lec{number}.txt").read_text().strip()
            for number in units
        ]
        return "\n\n".join(chunks) + "\n"
    if course == "geometry":
        chunks = [
            (source_dir / f"geometry/lecture{number}.clean.txt").read_text().strip()
            for number in units
        ]
        return "\n\n".join(chunks) + "\n"
    if course == "number_theory":
        chunks = [
            (source_dir / f"number_theory_2025/cleaned/lecture_{number:02d}.txt").read_text().strip()
            for number in units
        ]
        return "\n\n".join(chunks) + "\n"
    if course == "topology":
        return (source_dir / f"topology/cleaned_tex/{units[0]}.md").read_text()
    if course == "differential_analysis":
        cleaned = {
            1: "analysis_measures_integration_hilbert.txt",
            6: "analysis_test_functions_fourier_sobolev.txt",
            11: "analysis_differential_operators_wavefront_spectral.txt",
        }
        return (source_dir / "analysis/differential_analysis/cleaned" / cleaned[units[0]]).read_text()
    raise ValueError(f"Unknown course: {course}")


def build(source_dir: Path) -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = {"discovery": [], "heldout": []}
    for spec in SPECS:
        proof = proof_for(spec, source_dir)
        course = COURSES[spec["course"]]
        files = source_files(
            source_dir,
            spec["course"],
            spec["units"] if spec["course"] in {"measure", "geometry", "number_theory", "topology"} else None,
        )
        unit_label = spec.get("unit_label") or (
            f"Lecture {spec['units'][0]}"
            if len(spec["units"]) == 1
            else f"Lectures/sections {spec['units'][0]}–{spec['units'][-1]}"
        )
        metadata = {
            "dataset": DATASET,
            "broad_area": spec["area"],
            "topic": spec["title"],
            "title": spec["title"],
            "pair": spec["pair"],
            "level": "graduate",
            "correctness": True,
            "correctness_basis": "published graduate course notes from MIT faculty course materials",
            "cohesive": True,
            "internet_sourced": True,
            "exposition": "deterministically_cleaned_source_extraction",
            "actual_word_count": len(proof.split()),
            "theorem_like_marker_count": len(
                re.findall(r"\b(?:Theorem|Proposition|Lemma|Corollary)\b|\\begin\{(?:theorem|proposition|lemma|corollary)\}", proof, re.IGNORECASE)
            ),
            "proof_marker_count": len(re.findall(r"\bProof\.|\\begin\{proof\}", proof, re.IGNORECASE)),
            "source_course": course["course"],
            "source_term": course["term"],
            "source_author": course["author"],
            "source_url": course["url"],
            "source_units": unit_label,
            "source_files": files,
            "source_text_sha256": hashlib.sha256(proof.encode()).hexdigest(),
            "license": course["license"],
            "license_url": course["license_url"],
            "ocw_terms_url": OCW_TERMS_URL,
            "attribution": f"{spec['title']}, from {course['course']} ({course['term']}), by {course['author']}.",
            "transformation": course["transformation"],
        }
        rows[spec["split"]].append({
            "example_id": spec["example_id"],
            "problem": spec["problem"],
            "proof": proof,
            "metadata": metadata,
        })

    return {
        "dataset": DATASET,
        "description": (
            "Twenty graduate proof dossiers extracted from official MIT faculty course materials "
            "lecture notes, with ten discovery and ten held-out examples and matching 4/3/3 "
            "area distributions across algebra and number theory, analysis, and geometry/topology."
        ),
        "license_notice": (
            "Licensing varies by source: MIT OpenCourseWare excerpts are CC BY-NC-SA 4.0, "
            "the topology LaTeX source is MIT-licensed, and two official faculty-hosted note sets "
            "have no explicit license located. See each record before redistributing."
        ),
        "area_counts_per_split": {"algebra and number theory": 4, "analysis": 3, "geometry and topology": 3},
        **rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1_sources"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("local_datasets/graduate_course_dossiers_v1.json"),
    )
    args = parser.parse_args()
    payload = build(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    for split in ("discovery", "heldout"):
        for row in payload[split]:
            print(split, row["example_id"], row["metadata"]["actual_word_count"])


if __name__ == "__main__":
    main()
