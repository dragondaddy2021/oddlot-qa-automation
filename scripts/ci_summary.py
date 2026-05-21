"""Parse the pytest JUnit XML and build the CI email content.

- Writes key=value summary pairs to $GITHUB_OUTPUT (subject line, totals).
- Writes an HTML body (per-test breakdown) to reports/email_body.html, used as
  the email's html_body so the results show inline without opening the attachment.
"""

import datetime
import html
import os
import xml.etree.ElementTree as ET

JUNIT_PATH = os.environ.get("JUNIT_PATH", "reports/junit.xml")
BODY_PATH = os.environ.get("EMAIL_BODY_PATH", "reports/email_body.html")

BADGE = {
    "PASS": ("#1a7f37", "✅ PASS"),
    "FAIL": ("#cf222e", "❌ FAIL"),
    "ERROR": ("#cf222e", "❌ ERROR"),
    "SKIP": ("#8c8c8c", "⏭️ SKIP"),
}


def classify(testcase: ET.Element) -> tuple[str, str]:
    for child in testcase:
        tag = child.tag.lower()
        if tag == "failure":
            return "FAIL", (child.get("message") or child.text or "").strip()
        if tag == "error":
            return "ERROR", (child.get("message") or child.text or "").strip()
        if tag == "skipped":
            return "SKIP", (child.get("message") or child.text or "").strip()
    return "PASS", ""


def collect_cases() -> list[dict]:
    cases: list[dict] = []
    try:
        root = ET.parse(JUNIT_PATH).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
        for suite in suites:
            for tc in suite.findall("testcase"):
                status, detail = classify(tc)
                cases.append(
                    {
                        "name": tc.get("name", ""),
                        "classname": tc.get("classname", ""),
                        "time": float(tc.get("time", 0) or 0),
                        "status": status,
                        "detail": detail,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - report-only helper, never fail the build
        print(f"Could not parse {JUNIT_PATH}: {exc}")
    return cases


def build_html(cases: list[dict], totals: dict, meta: dict) -> str:
    rows = []
    for i, c in enumerate(cases, 1):
        color, label = BADGE.get(c["status"], ("#8c8c8c", c["status"]))
        test = html.escape(f"{c['classname']}::{c['name']}" if c["classname"] else c["name"])
        row = (
            f'<tr>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;color:#666;">{i}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;font-family:monospace;">{test}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;color:{color};font-weight:600;white-space:nowrap;">{label}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #eee;color:#666;text-align:right;">{c["time"]:.2f}s</td>'
            f'</tr>'
        )
        rows.append(row)
        if c["status"] in ("FAIL", "ERROR") and c["detail"]:
            detail = html.escape(c["detail"][:500])
            rows.append(
                f'<tr><td></td><td colspan="3" style="padding:4px 10px 10px;border-bottom:1px solid #eee;">'
                f'<pre style="margin:0;white-space:pre-wrap;color:#cf222e;font-size:12px;">{detail}</pre></td></tr>'
            )

    overall_color, overall_label = BADGE.get(totals["status"], ("#000", totals["status"]))
    return f"""\
<html><body style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1f2328;">
  <h2 style="margin:0 0 4px;">OddLot QA Automation — 每日回歸報告</h2>
  <p style="margin:0 0 16px;color:#666;">
    {meta['date']} ·  觸發：{html.escape(meta['event'])} ·
    <a href="{html.escape(meta['run_url'])}">完整執行紀錄</a>
  </p>
  <p style="font-size:18px;margin:0 0 12px;">
    結果：<b style="color:{overall_color};">{overall_label}</b>
    &nbsp;|&nbsp; 通過 <b style="color:#1a7f37;">{totals['passed']}</b>
    &nbsp;|&nbsp; 失敗 <b style="color:#cf222e;">{totals['failed']}</b>
    &nbsp;|&nbsp; 略過 <b style="color:#8c8c8c;">{totals['skipped']}</b>
    &nbsp;|&nbsp; 共 {totals['total']} 項
  </p>
  <table style="border-collapse:collapse;width:100%;font-size:14px;">
    <thead><tr style="background:#f6f8fa;text-align:left;">
      <th style="padding:8px 10px;">#</th><th style="padding:8px 10px;">測試項目</th>
      <th style="padding:8px 10px;">結果</th><th style="padding:8px 10px;text-align:right;">耗時</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <p style="color:#999;font-size:12px;margin-top:16px;">附件 report.html 為完整的 pytest-html 報告。</p>
</body></html>"""


def main() -> None:
    cases = collect_cases()
    total = len(cases)
    failed = sum(1 for c in cases if c["status"] in ("FAIL", "ERROR"))
    skipped = sum(1 for c in cases if c["status"] == "SKIP")
    passed = total - failed - skipped
    status = "PASS" if failed == 0 and total > 0 else "FAIL"

    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = f"{server}/{repo}/actions/runs/{run_id}" if repo and run_id else server
    tw_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)

    totals = {"status": status, "total": total, "passed": passed, "failed": failed, "skipped": skipped}
    meta = {"run_url": run_url, "event": os.environ.get("GITHUB_EVENT_NAME", "manual"),
            "date": tw_now.strftime("%Y-%m-%d %H:%M TW")}

    print(f"CI summary: {totals}")

    os.makedirs(os.path.dirname(BODY_PATH), exist_ok=True)
    with open(BODY_PATH, "w", encoding="utf-8") as handle:
        handle.write(build_html(cases, totals, meta))

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as handle:
            for key, value in {**totals, "run_url": run_url}.items():
                handle.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
