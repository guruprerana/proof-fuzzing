# Canonical datasets

This directory contains the version-controlled data for the four headline
proof-fuzzing datasets. The experiment loaders consume the JSON files and the TCS
Markdown proofs; the PDFs are retained only as original-source provenance.

## Runtime inputs

- `olympiadbench_balanced_40_v1.json`
- `olympiadbench_balanced_40_v1_manifest.json`
- `graduate_course_dossiers_v1.json`
- `recent_math_research_dossiers_clean_v1.json`
- `openai_ten_advances_2026/proofs_markdown/*.md`

## Original PDFs

- `graduate_course_dossiers_v1_sources/**/*.pdf` contains only the 57 source PDFs
  named by `source_files` entries in `graduate_course_dossiers_v1.json`. Their
  contents match the SHA-256 values stored in that JSON.
- `recent_math_research_dossiers_clean_v1_sources/*.pdf` contains the ten arXiv
  papers referenced by `source_url` entries in the recent-research JSON. Filenames
  use the corresponding dossier IDs.
- `openai_ten_advances_2026/source/ten-proofs-oai.pdf` is the 253-page source volume
  from which the ten TCS Markdown proofs were extracted. Its SHA-256 is
  `ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566`.

OlympiadBench is distributed as structured benchmark records rather than a single
source-PDF collection. None of these PDFs are needed by the experiment loaders.

Do not place run outputs, provider sessions, caches, extraction workspaces, or other
machine-local artifacts in this directory.
