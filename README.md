# OddLot QA Automation

Automated regression test portfolio for **OddLot** (龍爹地的零股投資學習平台), an AI-powered odd-lot stock recommendation website.

Live application under test: https://dragondaddy2021.github.io/oddlot/

Author: Teemo

## 專案定位 (Why This Project)

這個作品集是我用來展示 **Senior SDET** 能力的專案,不只是寫幾支測試腳本,而是包含**測試架構、API 驗證、E2E 流程、CI/CD 執行、測試報告與失敗截圖**,模擬實際公司導入自動化回歸測試的流程。

This portfolio demonstrates **Senior SDET** capabilities end to end — not just a handful of test scripts, but a complete framework: test architecture, API contract validation, E2E browser flows, CI/CD execution, HTML reporting, and automatic failure screenshots — mirroring how a real engineering team would adopt automated regression testing.

## Project Goal

This project demonstrates Senior QA Automation Engineer / SDET capabilities through a maintainable test automation framework covering API, web UI, AI response validation, test reporting, and CI/CD execution.

The tests run against the **live, publicly deployed application** and focus on stable product quality signals instead of brittle implementation details. AI recommendation tests validate response structure, required fields, error handling, and user-facing behavior rather than fixed AI-generated answers.

## Architecture Under Test

- **Front-end**: a Vite/React single-page app hosted on GitHub Pages (`BASE_URL`).
- **Back-end**: a Supabase REST (PostgREST) endpoint that serves the daily AI stock picks
  (`GET /rest/v1/ai_recommendations`), authenticated with a public publishable key.
- **Data shape**: each row is `{ id, date, stocks[10], reasoning, created_at }`, and each
  stock carries `symbol`, `name`, `reason`, `price`, `industry`, `yield_rate`, `pe_ratio`,
  `fill_rate`, `dividend_cv`, `momentum_3m`, and more.

## Tech Stack

- Python
- Pytest
- Playwright
- Requests
- pytest-html
- Allure (allure-pytest)
- python-dotenv
- GitHub Actions

## Test Scope

- Front-end site reachability (smoke)
- Supabase recommendation API availability
- AI recommendation contract validation (latest row, 10 stocks, required fields)
- Recommendation numeric-field sanity checks
- API authentication error handling (missing apikey → 401)
- Homepage smoke (title, disclaimer, navigation)
- Recommendation cards render with key metrics
- Favoriting is gated behind login
- Login "coming soon" state
- Friendly error message when the data source is unavailable

## How to Run

1. Create a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
playwright install chromium
```

3. (Optional) Create a local environment file. Sensible defaults pointing at the live
   site are baked in, so this is only needed to override a URL, key, or expected text.

```bash
cp .env.example .env
```

4. Run all tests.

```bash
pytest
```

5. Generate an HTML report.

```bash
pytest --html=reports/report.html --self-contained-html
```

> Web tests drive a real browser against the live site, so an internet connection is required.

## How to Run API Tests

```bash
pytest tests/api
```

## How to Run Web Tests

```bash
pytest tests/web
```

To run headed browser tests:

```bash
pytest tests/web --headed
```

## CI/CD

GitHub Actions runs regression tests on every push and pull request targeting `main`,
on a daily schedule, and on manual dispatch (see "CI Triggers & Cost" below).

The workflow:

- Installs Python dependencies
- Installs Playwright Chromium browser
- Runs API and web tests against the live deployment
- Generates `reports/report.html`
- Captures a full-page screenshot for any failed browser test under `reports/screenshots/`
- Uploads the HTML report and failure screenshots as build artifacts

## CI 觸發方式與費用 (中文)

### 觸發方式

回歸測試的 GitHub Actions 會在以下情況自動執行:

- **Push 到 `main`** — 每次推送 commit 即觸發
- **對 `main` 的 Pull Request** — 開啟或更新 PR 時觸發
- **每日定時** — 每天台灣時間約 03:30(UTC `30 19 * * *`),排在網站資料於凌晨 2:00 更新之後,自動驗證當天的線上推薦
- **手動觸發** — 到 GitHub 的 Actions 分頁點「Run workflow」(`workflow_dispatch`)

> 注意:公開 repo 若連續 60 天沒有任何 commit,GitHub 會自動暫停每日排程;推一個 commit 或在 Actions 分頁重新啟用即可恢復。

### 費用

- 本 repo 為 **public**,GitHub 標準 runner **完全免費、不限分鐘數**(含每日定時)
- Artifact 儲存對公開 repo 免費,且預設 90 天自動過期清除
- 被測的 GitHub Pages 與 Supabase 皆使用免費額度,測試每次僅發出少量請求
- **實質零成本**

## CI Triggers & Cost (English)

### Triggers

The regression workflow runs automatically on:

- **Push to `main`** — on every commit pushed
- **Pull request to `main`** — when a PR is opened or updated
- **Daily schedule** — ~03:30 Taiwan time (UTC `30 19 * * *`), right after the site's data refreshes at 02:00, to re-validate the live recommendations
- **Manual dispatch** — via the "Run workflow" button on the Actions tab (`workflow_dispatch`)

> Note: GitHub pauses scheduled runs on a public repo after 60 days without commits; push a commit or re-enable from the Actions tab to resume.

### Cost

- This is a **public** repository, so GitHub-hosted standard runners are **free with unlimited minutes** (including the daily run)
- Artifact storage is free for public repos and expires after 90 days by default
- The GitHub Pages site and Supabase backend run on free tiers; tests issue only a few requests per run
- **Effectively zero cost**

## Test Reporting & Failure Screenshots

The suite produces two reports on every run:

- **pytest-html**: a self-contained `reports/report.html` for quick local viewing.
- **Allure**: rich results written to `reports/allure-results/` (timeline, history,
  per-step detail, attachments).

When a browser test fails, a full-page screenshot is saved to
`reports/screenshots/<test_name>.png` automatically (via a `pytest_runtest_makereport`
hook) **and attached to its Allure result**, so failures come with visual evidence
instead of just a stack trace.

View the Allure report locally (requires Java + the Allure CLI):

```bash
allure serve reports/allure-results
```

In CI, the Allure report, pytest-html report, and failure screenshots are all uploaded
as build artifacts.

## Documentation

- [Test Strategy](docs/test_strategy.md)
- [AI Testing Strategy](docs/ai_testing_strategy.md)
- [Bug Report Sample](docs/bug_report_sample.md)
- [CI/CD Design](docs/ci_cd_design.md)
