"""Parser for semi-formalized proof artifacts.

The generated artifacts are intentionally text-first: they are readable proof
outlines with a small amount of structure. This parser keeps that spirit. It
does not try to interpret mathematics; it extracts global context, lemma
modules, claims, and normalized ``allowed_references`` blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import json
import re
from pathlib import Path
from typing import Iterable, Sequence


CLAIM_RE = re.compile(r"^\s*claim\s+([A-Za-z0-9_.-]+):\s*$")
LEMMA_RE = re.compile(r"^lemma\s+([A-Za-z0-9_.-]+):\s*$")
TOP_LEVEL_RE = re.compile(
    r"^(global context|main proof claims):?\s*$|^lemma\s+[A-Za-z0-9_.-]+:\s*$|^claim\s+[A-Za-z0-9_.-]+:\s*$"
)
LEGACY_CLAIM_RE = re.compile(r"^CLAIM\s+([0-9]+):\s*$")
FIELD_NAMES = {
    "check_type",
    "variables",
    "hypotheses",
    "allowed_references",
    "conclusion",
}


class ParseError(ValueError):
    """Raised when a proof artifact cannot be parsed."""


@dataclass(frozen=True)
class Reference:
    """A dependency entry from an ``allowed_references`` block."""

    ref: str
    instantiation: str = ""
    raw_lines: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "ref": self.ref,
            "instantiation": self.instantiation,
            "raw_lines": list(self.raw_lines),
        }


@dataclass(frozen=True)
class Claim:
    """A verifier-oriented claim."""

    claim_id: str
    check_type: str = ""
    variables: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    allowed_references: tuple[Reference, ...] = ()
    conclusion: tuple[str, ...] = ()
    raw_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "check_type": self.check_type,
            "variables": list(self.variables),
            "hypotheses": list(self.hypotheses),
            "allowed_references": [ref.to_dict() for ref in self.allowed_references],
            "conclusion": list(self.conclusion),
            "raw_text": self.raw_text,
        }


@dataclass(frozen=True)
class LemmaModule:
    """A lemma module with internal proof claims and exported statements."""

    lemma_id: str
    statement: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    proof_claims: tuple[Claim, ...] = ()
    exports: tuple[str, ...] = ()
    raw_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "lemma_id": self.lemma_id,
            "statement": list(self.statement),
            "dependencies": list(self.dependencies),
            "proof_claims": [claim.to_dict() for claim in self.proof_claims],
            "exports": list(self.exports),
            "raw_text": self.raw_text,
        }


@dataclass(frozen=True)
class ParseIssue:
    """A non-fatal structural issue found after parsing."""

    message: str
    location: str = ""
    severity: str = "warning"

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "location": self.location,
            "message": self.message,
        }


@dataclass(frozen=True)
class SemiFormalProof:
    """Parsed semi-formal proof artifact."""

    global_context: tuple[str, ...] = ()
    lemmas: tuple[LemmaModule, ...] = ()
    claims: tuple[Claim, ...] = ()
    raw_text: str = ""
    parse_warnings: tuple[ParseIssue, ...] = ()

    def all_claims(self) -> tuple[Claim, ...]:
        lemma_claims: list[Claim] = []
        for lemma in self.lemmas:
            lemma_claims.extend(lemma.proof_claims)
        return tuple(lemma_claims + list(self.claims))

    def claim_map(self) -> dict[str, Claim]:
        return {claim.claim_id: claim for claim in self.all_claims()}

    def lemma_map(self) -> dict[str, LemmaModule]:
        return {lemma.lemma_id: lemma for lemma in self.lemmas}

    def get_claim(self, claim_id: str) -> Claim | None:
        return self.claim_map().get(claim_id)

    def get_lemma(self, lemma_id: str) -> LemmaModule | None:
        return self.lemma_map().get(lemma_id)

    def to_dict(self, include_raw: bool = False) -> dict[str, object]:
        data: dict[str, object] = {
            "global_context": list(self.global_context),
            "lemmas": [lemma.to_dict() for lemma in self.lemmas],
            "claims": [claim.to_dict() for claim in self.claims],
            "parse_warnings": [issue.to_dict() for issue in self.parse_warnings],
        }
        if include_raw:
            data["raw_text"] = self.raw_text
        else:
            for lemma in data["lemmas"]:  # type: ignore[union-attr]
                lemma.pop("raw_text", None)
                for claim in lemma["proof_claims"]:
                    claim.pop("raw_text", None)
            for claim in data["claims"]:  # type: ignore[union-attr]
                claim.pop("raw_text", None)
        return data


def parse_file(path: str | Path) -> SemiFormalProof:
    """Parse a semi-formalized proof artifact from disk."""

    return parse_text(Path(path).read_text())


def parse_text(text: str) -> SemiFormalProof:
    """Parse a semi-formalized proof artifact."""

    lines = text.splitlines()
    global_context: tuple[str, ...] = ()
    lemmas: list[LemmaModule] = []
    claims: list[Claim] = []
    warnings: list[ParseIssue] = []

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        if stripped in {"global context:", "global context"}:
            end = _next_top_level(lines, i + 1)
            global_context = tuple(_clean_content(lines[i + 1 : end]))
            i = end
            continue

        lemma_match = LEMMA_RE.match(stripped)
        if lemma_match:
            end = _next_top_level(lines, i + 1)
            lemmas.append(_parse_lemma(lines[i:end], warnings))
            i = end
            continue

        if stripped in {"main proof claims:", "main proof claims"}:
            i += 1
            continue

        claim_match = CLAIM_RE.match(lines[i])
        if claim_match:
            end = _next_claim_or_top_level(lines, i + 1)
            claims.append(_parse_claim(lines[i:end], warnings))
            i = end
            continue

        warnings.append(
            ParseIssue(
                location=f"line {i + 1}",
                message=f"Unrecognized top-level line: {stripped}",
            )
        )
        i += 1

    if not global_context and not lemmas and not claims and any(LEGACY_CLAIM_RE.match(line.strip()) for line in lines):
        return _parse_legacy_claim_artifact(text)

    if not global_context and not lemmas and not claims:
        raise ParseError("No semi-formal proof sections were found.")

    return SemiFormalProof(
        global_context=global_context,
        lemmas=tuple(lemmas),
        claims=tuple(claims),
        raw_text=text,
        parse_warnings=tuple(warnings),
    )


def validate_references(proof: SemiFormalProof) -> list[ParseIssue]:
    """Return non-fatal issues for references that cannot be resolved.

    This checks syntactic/dependency integrity only. It does not check whether
    the referenced mathematics proves the conclusion.
    """

    issues: list[ParseIssue] = list(proof.parse_warnings)
    known_claims = proof.claim_map()
    known_exports = _exported_statement_ids(proof)

    for lemma in proof.lemmas:
        internal_ids = {claim.claim_id for claim in lemma.proof_claims}
        for claim in lemma.proof_claims:
            for ref in claim.allowed_references:
                if ref.ref in known_claims or ref.ref in known_exports:
                    continue
                if ref.ref.endswith(".statement") and ref.ref in known_exports:
                    continue
                issues.append(
                    ParseIssue(
                        location=claim.claim_id,
                        message=f"Unknown reference {ref.ref!r}.",
                    )
                )

            if claim.claim_id not in internal_ids:
                issues.append(
                    ParseIssue(
                        location=claim.claim_id,
                        message="Internal parser consistency error: claim missing from its lemma.",
                        severity="error",
                    )
                )

    for claim in proof.claims:
        for ref in claim.allowed_references:
            if ref.ref in known_claims or ref.ref in known_exports:
                continue
            issues.append(
                ParseIssue(
                    location=claim.claim_id,
                    message=f"Unknown reference {ref.ref!r}.",
                )
            )

    return issues


def _exported_statement_ids(proof: SemiFormalProof) -> set[str]:
    ids: set[str] = set()
    for lemma in proof.lemmas:
        ids.add(f"{lemma.lemma_id}.statement")
        for export in lemma.exports:
            normalized = export.rstrip(".")
            if normalized:
                ids.add(normalized)
    return ids


def _next_top_level(lines: Sequence[str], start: int) -> int:
    for i in range(start, len(lines)):
        if _indent(lines[i]) == 0 and TOP_LEVEL_RE.match(lines[i].strip()):
            return i
    return len(lines)


def _next_claim_or_top_level(lines: Sequence[str], start: int) -> int:
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if CLAIM_RE.match(lines[i]) or LEMMA_RE.match(stripped) or stripped in {"main proof claims:", "main proof claims"}:
            return i
    return len(lines)


def _parse_legacy_claim_artifact(text: str) -> SemiFormalProof:
    """Best-effort parser for older CLAIM/Statement/Proof artifacts.

    A few early artifacts predate the modular format. They are still useful to
    ingest, but they do not contain parseable dependency blocks. We represent
    each numbered claim as a ``Claim`` with proof text stored as hypotheses and
    emit a warning so callers know the artifact is not normalized.
    """

    lines = text.splitlines()
    global_context: list[str] = []
    claims: list[Claim] = []
    warnings = [
        ParseIssue(
            location="artifact",
            message="Parsed legacy CLAIM/Statement/Proof format; allowed references are unavailable.",
        )
    ]

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        legacy_match = LEGACY_CLAIM_RE.match(stripped)
        if not legacy_match:
            if stripped:
                global_context.append(stripped)
            i += 1
            continue

        claim_number = legacy_match.group(1)
        end = i + 1
        while end < len(lines) and not LEGACY_CLAIM_RE.match(lines[end].strip()):
            end += 1

        block = lines[i + 1 : end]
        statement, proof_lines = _split_legacy_statement_proof(block)
        claims.append(
            Claim(
                claim_id=f"C{claim_number}",
                check_type="other",
                hypotheses=tuple(proof_lines),
                allowed_references=(),
                conclusion=tuple(statement),
                raw_text="\n".join(lines[i:end]),
            )
        )
        i = end

    return SemiFormalProof(
        global_context=tuple(global_context),
        claims=tuple(claims),
        raw_text=text,
        parse_warnings=tuple(warnings),
    )


def _split_legacy_statement_proof(lines: Sequence[str]) -> tuple[list[str], list[str]]:
    statement: list[str] = []
    proof: list[str] = []
    target = statement
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "Statement:":
            target = statement
            continue
        if stripped == "Proof:":
            target = proof
            continue
        if stripped.startswith("Statement:"):
            target = statement
            rest = stripped[len("Statement:") :].strip()
            if rest:
                target.append(rest)
            continue
        if stripped.startswith("Proof:"):
            target = proof
            rest = stripped[len("Proof:") :].strip()
            if rest:
                target.append(rest)
            continue
        target.append(stripped)
    return statement, proof


def _parse_lemma(lines: Sequence[str], warnings: list[ParseIssue]) -> LemmaModule:
    if not lines:
        raise ParseError("Cannot parse empty lemma block.")

    header = lines[0].strip()
    lemma_match = LEMMA_RE.match(header)
    if not lemma_match:
        raise ParseError(f"Invalid lemma header: {header}")
    lemma_id = lemma_match.group(1)

    statement: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    proof_claims: tuple[Claim, ...] = ()
    exports: tuple[str, ...] = ()

    sections = _split_named_sections(lines[1:], {"statement", "dependencies", "proof_claims", "exports"})

    if "statement" in sections:
        statement = tuple(_clean_content(sections["statement"]))
    else:
        warnings.append(ParseIssue(location=lemma_id, message="Lemma has no statement section."))

    if "dependencies" in sections:
        dependencies = tuple(_clean_content(sections["dependencies"]))

    if "proof_claims" in sections:
        proof_claims = tuple(_parse_claim_blocks(sections["proof_claims"], warnings))
    else:
        warnings.append(ParseIssue(location=lemma_id, message="Lemma has no proof_claims section."))

    if "exports" in sections:
        exports = tuple(_clean_content(sections["exports"]))

    return LemmaModule(
        lemma_id=lemma_id,
        statement=statement,
        dependencies=dependencies,
        proof_claims=proof_claims,
        exports=exports,
        raw_text="\n".join(lines),
    )


def _parse_claim_blocks(lines: Sequence[str], warnings: list[ParseIssue]) -> list[Claim]:
    claims: list[Claim] = []
    i = 0
    while i < len(lines):
        if not CLAIM_RE.match(lines[i]):
            i += 1
            continue
        end = i + 1
        while end < len(lines) and not CLAIM_RE.match(lines[end]):
            end += 1
        claims.append(_parse_claim(lines[i:end], warnings))
        i = end
    return claims


def _parse_claim(lines: Sequence[str], warnings: list[ParseIssue]) -> Claim:
    if not lines:
        raise ParseError("Cannot parse empty claim block.")

    claim_match = CLAIM_RE.match(lines[0])
    if not claim_match:
        raise ParseError(f"Invalid claim header: {lines[0]}")
    claim_id = claim_match.group(1)

    sections = _split_named_sections(lines[1:], FIELD_NAMES)
    if "allowed_references" not in sections:
        warnings.append(ParseIssue(location=claim_id, message="Claim has no allowed_references section."))
    if "conclusion" not in sections:
        warnings.append(ParseIssue(location=claim_id, message="Claim has no conclusion section."))

    return Claim(
        claim_id=claim_id,
        check_type=_single_line(sections.get("check_type", ())),
        variables=tuple(_clean_content(sections.get("variables", ()))),
        hypotheses=tuple(_clean_content(sections.get("hypotheses", ()))),
        allowed_references=tuple(
            _parse_allowed_references(sections.get("allowed_references", ()), claim_id, warnings)
        ),
        conclusion=tuple(_clean_content(sections.get("conclusion", ()))),
        raw_text="\n".join(lines),
    )


def _split_named_sections(lines: Sequence[str], names: Iterable[str]) -> dict[str, list[str]]:
    name_set = set(names)
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in lines:
        stripped = line.strip()
        for candidate in name_set:
            prefix = f"{candidate}:"
            if stripped == prefix or stripped.startswith(f"{prefix} "):
                current = candidate
                sections.setdefault(current, [])
                trailing = stripped[len(prefix) :].strip()
                if trailing:
                    sections[current].append(trailing)
                break
        else:
            if current is not None:
                sections[current].append(line)
            continue
        if current is not None:
            continue

    return sections


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_allowed_references(
    lines: Sequence[str],
    claim_id: str,
    warnings: list[ParseIssue],
) -> list[Reference]:
    content = _clean_content(lines)
    if not content:
        return []
    if len(content) == 1 and content[0] == "none":
        return []

    refs: list[Reference] = []
    current_ref: str | None = None
    current_instantiation: list[str] = []
    current_raw: list[str] = []

    def flush() -> None:
        nonlocal current_ref, current_instantiation, current_raw
        if current_ref is None:
            return
        refs.append(
            Reference(
                ref=current_ref,
                instantiation=" ".join(current_instantiation).strip(),
                raw_lines=tuple(current_raw),
            )
        )
        current_ref = None
        current_instantiation = []
        current_raw = []

    for line in content:
        if line.startswith("- ref:"):
            flush()
            current_ref = line.split(":", 1)[1].strip()
            current_raw = [line]
            continue

        if current_ref is None:
            warnings.append(
                ParseIssue(
                    location=claim_id,
                    message=f"Unparseable allowed_references line: {line}",
                )
            )
            continue

        current_raw.append(line)
        if line.startswith("instantiation:"):
            current_instantiation.append(line.split(":", 1)[1].strip())
        else:
            current_instantiation.append(line)

    flush()
    return refs


def _clean_content(lines: Sequence[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned.append(stripped)
    return cleaned


def _single_line(lines: Sequence[str]) -> str:
    return " ".join(_clean_content(lines)).strip()


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a semi-formalized proof artifact.")
    parser.add_argument("path", type=Path, help="Path to a proof artifact text file.")
    parser.add_argument("--include-raw", action="store_true", help="Include raw text blocks in JSON output.")
    parser.add_argument("--validate", action="store_true", help="Include reference validation issues.")
    args = parser.parse_args(argv)

    proof = parse_file(args.path)
    data = proof.to_dict(include_raw=args.include_raw)
    if args.validate:
        data["reference_issues"] = [issue.to_dict() for issue in validate_references(proof)]
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
