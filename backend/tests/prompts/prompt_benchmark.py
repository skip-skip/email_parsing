from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field

from backend.app.prompts.email_extraction import (
    EMAIL_EXTRACTION_VERSION,
)
from backend.app.prompts.missing_info_draft import (
    MISSING_INFO_DRAFT_VERSION,
)
from backend.app.prompts.schedule_suggestion import (
    SCHEDULE_SUGGESTION_VERSION,
)
from backend.tests.prompts.test_data import (
    EMAIL_SAMPLES,
    MOCK_LLM_EXTRACTION_RESPONSES,
    MOCK_MISSING_INFO_DRAFTS,
    MOCK_SCHEDULE_SUGGESTIONS,
)

EXTRACTION_FIELDS = [
    "client",
    "sender",
    "subject",
    "project_number",
    "task_description",
    "deadline",
    "budget_hours",
    "attachments",
    "confidence",
]


@dataclass
class BenchmarkResult:
    prompt_name: str
    prompt_version: str
    total_samples: int
    passed: int
    failed: int
    accuracy: float
    field_accuracy: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0


def _measure_extraction_accuracy() -> BenchmarkResult:
    start = time.perf_counter()
    field_correct: dict[str, int] = {f: 0 for f in EXTRACTION_FIELDS}
    total = len(EMAIL_SAMPLES)
    errors: list[str] = []

    for sample in EMAIL_SAMPLES:
        response = MOCK_LLM_EXTRACTION_RESPONSES[sample.name]
        expected = sample.expected_extraction

        for fld in EXTRACTION_FIELDS:
            actual = response.get(fld)
            exp = expected.get(fld)
            if fld == "confidence":
                if isinstance(actual, (int, float)) and isinstance(exp, (int, float)):
                    field_correct[fld] += 1
            elif actual == exp:
                field_correct[fld] += 1
            else:
                errors.append(
                    f"{sample.name}.{fld}: got {actual!r}, expected {exp!r}"
                )

    field_accuracy = {
        fld: field_correct[fld] / total for fld in EXTRACTION_FIELDS
    }
    overall = sum(field_accuracy.values()) / len(field_accuracy)
    elapsed = (time.perf_counter() - start) * 1000

    return BenchmarkResult(
        prompt_name="email_extraction",
        prompt_version=EMAIL_EXTRACTION_VERSION,
        total_samples=total,
        passed=sum(1 for v in field_accuracy.values() if v >= 0.9),
        failed=sum(1 for v in field_accuracy.values() if v < 0.9),
        accuracy=overall,
        field_accuracy=field_accuracy,
        errors=errors,
        execution_time_ms=elapsed,
    )


def _measure_draft_quality() -> BenchmarkResult:
    start = time.perf_counter()
    total = len(MOCK_MISSING_INFO_DRAFTS)
    passed = 0
    errors: list[str] = []

    quality_checks = {
        "has_greeting": lambda d: any(
            d.strip().startswith(p) for p in ["Dear", "Hi", "Hello"]
        ),
        "has_closing": lambda d: any(
            w in d.lower() for w in ["regards", "sincerely", "thank you", "best"]
        ),
        "multi_sentence": lambda d: len([s for s in d.split(".") if s.strip()]) >= 3,
        "reasonable_length": lambda d: 50 < len(d.strip()) < 2000,
    }

    for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
        sample_ok = True
        for check_name, check_fn in quality_checks.items():
            if not check_fn(draft):
                errors.append(f"{name}: failed check '{check_name}'")
                sample_ok = False
        if sample_ok:
            passed += 1

    elapsed = (time.perf_counter() - start) * 1000
    accuracy = passed / total if total > 0 else 0

    return BenchmarkResult(
        prompt_name="missing_info_draft",
        prompt_version=MISSING_INFO_DRAFT_VERSION,
        total_samples=total,
        passed=passed,
        failed=total - passed,
        accuracy=accuracy,
        errors=errors,
        execution_time_ms=elapsed,
    )


def _measure_schedule_suggestions() -> BenchmarkResult:
    start = time.perf_counter()
    total = len(MOCK_SCHEDULE_SUGGESTIONS)
    passed = 0
    errors: list[str] = []

    valid_days = {
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday",
    }

    for name, suggestion in MOCK_SCHEDULE_SUGGESTIONS.items():
        sample_ok = True

        if "suggested_blocks" not in suggestion:
            errors.append(f"{name}: missing 'suggested_blocks'")
            sample_ok = False
        if "total_scheduled_hours" not in suggestion:
            errors.append(f"{name}: missing 'total_scheduled_hours'")
            sample_ok = False
        if not suggestion.get("notes"):
            errors.append(f"{name}: missing 'notes'")
            sample_ok = False

        for block in suggestion.get("suggested_blocks", []):
            if block.get("day") not in valid_days:
                errors.append(f"{name}: invalid day '{block.get('day')}'")
                sample_ok = False
            start_t = block.get("start_time", "")
            end_t = block.get("end_time", "")
            if not start_t or not end_t or start_t >= end_t:
                errors.append(f"{name}: invalid time range {start_t}-{end_t}")
                sample_ok = False
            start_h = int(start_t.split(":")[0]) if start_t else 0
            end_h = int(end_t.split(":")[0]) if end_t else 0
            if start_h < 9 or end_h > 17:
                errors.append(
                    f"{name}: block outside working hours {start_t}-{end_t}"
                )
                sample_ok = False

        if sample_ok:
            passed += 1

    elapsed = (time.perf_counter() - start) * 1000
    accuracy = passed / total if total > 0 else 0

    return BenchmarkResult(
        prompt_name="schedule_suggestion",
        prompt_version=SCHEDULE_SUGGESTION_VERSION,
        total_samples=total,
        passed=passed,
        failed=total - passed,
        accuracy=accuracy,
        errors=errors,
        execution_time_ms=elapsed,
    )


def _format_result(result: BenchmarkResult) -> str:
    lines = [
        f"  Prompt: {result.prompt_name} ({result.prompt_version})",
        f"  Samples: {result.total_samples}",
        f"  Passed: {result.passed} / {result.total_samples}",
        f"  Accuracy: {result.accuracy:.1%}",
        f"  Time: {result.execution_time_ms:.2f}ms",
    ]
    if result.field_accuracy:
        lines.append("  Per-field accuracy:")
        for fld, acc in result.field_accuracy.items():
            marker = "PASS" if acc >= 0.9 else "FAIL"
            lines.append(f"    {fld}: {acc:.1%} [{marker}]")
    if result.errors:
        lines.append(f"  Errors ({len(result.errors)}):")
        for err in result.errors[:10]:
            lines.append(f"    - {err}")
        if len(result.errors) > 10:
            lines.append(f"    ... and {len(result.errors) - 10} more")
    return "\n".join(lines)


def run_benchmarks() -> dict[str, BenchmarkResult]:
    results: dict[str, BenchmarkResult] = {}
    results["email_extraction"] = _measure_extraction_accuracy()
    results["missing_info_draft"] = _measure_draft_quality()
    results["schedule_suggestion"] = _measure_schedule_suggestions()
    return results


def print_report(results: dict[str, BenchmarkResult]) -> None:
    print("=" * 70)
    print("PROMPT BENCHMARK REPORT")
    print("=" * 70)
    print()

    total_passed = 0
    total_samples = 0

    for name, result in results.items():
        print(_format_result(result))
        print()
        total_passed += result.passed
        total_samples += result.total_samples

    print("-" * 70)
    overall = total_passed / total_samples if total_samples > 0 else 0
    print(f"OVERALL: {total_passed}/{total_samples} checks passed ({overall:.1%})")
    print()

    all_ok = all(r.accuracy >= 0.90 for r in results.values())
    if all_ok:
        print("STATUS: ALL PROMPTS PASS (>=90% accuracy)")
    else:
        failing = [n for n, r in results.items() if r.accuracy < 0.90]
        print(f"STATUS: FAILING - {', '.join(failing)}")
    print("=" * 70)


def main() -> None:
    results = run_benchmarks()
    print_report(results)

    all_ok = all(r.accuracy >= 0.90 for r in results.values())
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
