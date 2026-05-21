# CI/CD Design

## Overview

The GitHub Actions workflow runs regression tests when code is pushed to `main`, when a pull request targets `main`, on a daily schedule (03:30 Taiwan time / UTC `30 19 * * *`, after the site's 02:00 data refresh), and on manual dispatch (`workflow_dispatch`).

The tests run against the live, publicly deployed application (GitHub Pages front-end + Supabase REST back-end), so no application server needs to be started in CI.

The workflow is designed to provide quick feedback and produce a portable HTML report for review.

## Workflow Steps

1. Check out the repository.
2. Set up Python.
3. Install dependencies from `requirements.txt`.
4. Install Playwright Chromium browser.
5. Run Pytest regression tests.
6. Generate `reports/report.html` and capture failure screenshots under `reports/screenshots/`.
7. Upload the HTML report and any failure screenshots as GitHub Actions artifacts.

## Environment Variables

Runtime configuration is provided through environment variables:

- `BASE_URL` — front-end (GitHub Pages) base URL
- `SUPABASE_URL` — Supabase REST base URL
- `SUPABASE_ANON_KEY` — Supabase publishable (anon) key
- `AI_RECOMMENDATION_ENDPOINT` — recommendation table path

The Supabase publishable key is a public anon key already embedded in the front-end, so it is safe to commit. The workflow still reads it from `secrets.SUPABASE_ANON_KEY` when present, so it can be rotated without code changes. Any genuinely sensitive credentials must be stored in GitHub Actions secrets and never committed.

## Regression Reports

The workflow generates two reports:

```text
reports/report.html        # self-contained pytest-html report
reports/allure-report/     # generated Allure report (from reports/allure-results)
```

These are uploaded as artifacts named `pytest-html-report`, `allure-report`, and
`allure-results`. Any failure screenshots are uploaded as `failure-screenshots`.

## Quality Gate

The pull request should not be merged unless the regression workflow passes and the HTML report does not show critical failures.

