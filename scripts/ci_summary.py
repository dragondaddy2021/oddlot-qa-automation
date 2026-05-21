"""Parse the pytest JUnit XML and emit a summary for the CI email step.

Writes key=value pairs to $GITHUB_OUTPUT (consumed by later workflow steps) and
prints a human-readable summary to the log.
"""

import os
import xml.etree.ElementTree as ET

JUNIT_PATH = "reports/junit.xml"


def main() -> None:
    total = failed = errors = skipped = 0
    try:
        root = ET.parse(JUNIT_PATH).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
        for suite in suites:
            total += int(suite.get("tests", 0))
            failed += int(suite.get("failures", 0))
            errors += int(suite.get("errors", 0))
            skipped += int(suite.get("skipped", 0))
    except Exception as exc:  # noqa: BLE001 - report-only helper, never fail the build
        print(f"Could not parse {JUNIT_PATH}: {exc}")

    fail_total = failed + errors
    passed = total - fail_total - skipped
    status = "PASS" if fail_total == 0 and total > 0 else "FAIL"

    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = f"{server}/{repo}/actions/runs/{run_id}" if repo and run_id else ""

    outputs = {
        "status": status,
        "total": total,
        "passed": passed,
        "failed": fail_total,
        "skipped": skipped,
        "run_url": run_url,
    }
    print(f"CI summary: {outputs}")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
