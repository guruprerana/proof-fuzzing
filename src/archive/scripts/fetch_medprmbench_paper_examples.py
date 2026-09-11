#!/usr/bin/env python3
"""Download and extract the 14 MedPRMBench appendix trace pairs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer.medprmbench import (
    DEFAULT_MEDPRMBENCH_ROOT,
    MEDPRMBENCH_PAPER_ID,
    MEDPRMBENCH_SOURCE_URL,
    extract_medprmbench_paper_examples,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_MEDPRMBENCH_ROOT / "paper_examples.jsonl",
    )
    parser.add_argument("--source-url", default=MEDPRMBENCH_SOURCE_URL)
    args = parser.parse_args()

    request = Request(args.source_url, headers={"User-Agent": "proof-fuzzing/medprmbench"})
    with urlopen(request, timeout=60) as response:
        archive = response.read()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as bundle:
        tex_members = [member for member in bundle.getmembers() if member.name.endswith(".tex")]
        for member in tex_members:
            handle = bundle.extractfile(member)
            if handle is None:
                continue
            tex = handle.read().decode("utf-8", errors="replace")
            if r"\section{Error Type Examples}" in tex:
                source_name = member.name
                break
        else:
            raise RuntimeError("No MedPRMBench appendix TeX file found in the arXiv source.")

    rows = extract_medprmbench_paper_examples(tex)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    manifest = {
        "paper_id": MEDPRMBENCH_PAPER_ID,
        "source_url": args.source_url,
        "source_member": source_name,
        "source_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "rows": len(rows),
        "note": (
            "Appendix examples only; not a substitute for the authors' full benchmark. "
            "The paper does not state a data license, so verify terms before redistribution."
        ),
    }
    manifest_path = args.output.with_suffix(".source.json")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} traces to {args.output}")
    print(f"Wrote provenance to {manifest_path}")


if __name__ == "__main__":
    main()
