"""Prompts and parsers for validating mutations and measuring judge misses."""

import json
import re
from typing import Iterable

from .models import FuzzerMutationInstructions, JudgeResult, LLMClient


def load_json_object(text: str) -> dict[str, object]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else text[text.find("{"):text.rfind("}") + 1]
    if not candidate or not candidate.startswith("{"):
        raise ValueError("No JSON object was found in the LLM response.")
    value = json.loads(candidate)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return value


def _errors(value: object) -> tuple[dict[str, object], ...]:
    return tuple(dict(item) for item in value if isinstance(item, dict)) if isinstance(value, list) else ()


def parse_judge_result(text: str) -> JudgeResult:
    data = load_json_object(text)
    if "errors" in data and "verdict" not in data:
        errors = _errors(data.get("errors"))
        confidence = max((float(e.get("confidence", 0) or 0) for e in errors), default=0.0)
        return JudgeResult("incorrect" if errors else "correct", confidence,
            str(data.get("review_summary", "")), "; ".join(str(e.get("description", "")) for e in errors),
            errors, "error_inventory", text)
    verdict = str(data.get("verdict", "")).strip().lower()
    if verdict not in {"correct", "incorrect", "uncertain"}:
        raise ValueError(f"Unknown judge verdict: {verdict!r}")
    return JudgeResult(verdict, float(data.get("confidence", 0) or 0),
        str(data.get("rationale", "")), str(data.get("detected_flaw", "")), raw_response=text)


def parse_match_result(text: str) -> dict[str, object]:
    data = load_json_object(text)
    reported = bool(data.get("introduced_error_found", data.get("any_judge_reported_correct_error", False)))
    level = str(data.get("match_level", "none")).strip().lower()
    found = reported and level == "exact"
    indices = data.get("matching_report_indices", data.get("matching_judge_indices", []))
    indices = [int(i) for i in indices if str(i).lstrip("-").isdigit()] if isinstance(indices, list) else []
    error_indices = data.get("matching_error_indices", [])
    error_indices = [{"report_index": int(i["report_index"]), "error_index": int(i["error_index"])}
        for i in error_indices if isinstance(i, dict) and str(i.get("report_index", "")).lstrip("-").isdigit()
        and str(i.get("error_index", "")).lstrip("-").isdigit()] if isinstance(error_indices, list) else []
    return {"introduced_error_found": found, "any_judge_reported_correct_error": found,
        "matching_report_indices": indices, "matching_judge_indices": indices,
        "matching_error_indices": error_indices, "match_level": level if level in {"none", "partial", "exact"} else "none",
        "matcher_policy": "exact_only", "reported_introduced_error_found": reported,
        "rationale": str(data.get("rationale", ""))}


def _explanation(instructions: FuzzerMutationInstructions) -> str:
    return instructions.rationale.strip() or "\n".join(m.summary for m in instructions.mutations)


class MutationValidator:
    def __init__(self, llm: LLMClient): self.llm = llm

    def prompt(self, *, original: str, mutated: str, instructions: FuzzerMutationInstructions,
               problem: str) -> str:
        return f'''You are checking a described error introduced into a mathematical proof.
Determine only whether the supplied introduced-error explanation identifies a genuine new logical
or mathematical flaw in the mutated proof. The original may itself be wrong and is supplied only
to distinguish pre-existing defects. A real local error counts even if the theorem remains true or
another argument proves it. Return "correct" if the alleged flaw is valid, absent, or pre-existing;
return "uncertain" if the text is insufficient. Do not audit unrelated parts.

Problem:\n{problem}\n
Original proof:\n{original}\n
Mutated proof:\n{mutated}\n
Introduced-error explanation:\n{_explanation(instructions)}\n
Return exactly one JSON object:
{{"verdict":"correct | incorrect | uncertain","confidence":0.0,
"rationale":"direct assessment of the described error","detected_flaw":"verified flaw or empty"}}'''


class BlindErrorFinder:
    def __init__(self, llm: LLMClient): self.llm = llm

    def prompt(self, *, problem: str, proof: str) -> str:
        return f'''Review this mathematical proof and report every concrete mathematical or logical
error you find, even if local or the conclusion remains true. Check cases, dependencies, false
claims, invalid or circular inferences, hidden assumptions, algebra, indices, signs, quantifiers,
scope, and conclusions stronger than established. Group downstream symptoms of one root cause.
Exclude style concerns, generic requests for detail, and explicitly retracted claims. Do not assume
there is an error. Return exactly one JSON object and no correctness score.

Problem:\n{problem}\n
Proof:\n{proof}\n
Schema:
{{"errors":[{{"location":"precise locator","root_cause":"independent root error",
"description":"specific error","consequence":"local and downstream effect",
"severity":"minor | major | critical","confidence":0.0}}],
"review_summary":"what was checked"}}'''


class IntroducedErrorMatcher:
    def __init__(self, llm: LLMClient): self.llm = llm

    def prompt(self, *, instructions: FuzzerMutationInstructions, reports: Iterable[JudgeResult],
               original: str, mutated: str) -> str:
        payload = [report.to_dict() for report in reports]
        return f'''Determine whether any blind error report explicitly and uniquely identified the
introduced error. The explanation identifies what to match but is not evidence of detection.
A generic downstream complaint, topic overlap, unrelated issue, or pre-existing defect is not a
match. There is no partial credit: true only for an exact or logically equivalent causal diagnosis.

Original proof:\n{original}\n
Mutated proof:\n{mutated}\n
Introduced error:\n{_explanation(instructions)}\n
Blind reports:\n{json.dumps(payload, indent=2)}\n
Return exactly one JSON object:
{{"introduced_error_found":false,"matching_report_indices":[],
"matching_error_indices":[],"match_level":"none | exact","rationale":"brief justification"}}'''


def usage_limit_reached(value: object) -> bool:
    text = repr(value).lower()
    return "usage limit" in text or "purchase more credits" in text
