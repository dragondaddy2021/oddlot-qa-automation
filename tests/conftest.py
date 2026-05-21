import os
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from clients.api_client import ApiClient


load_dotenv()


SCREENSHOTS_DIR = Path("reports/screenshots")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Capture a full-page screenshot whenever a browser test fails, so CI
    artifacts include visual evidence of the failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = SCREENSHOTS_DIR / f"{item.name}.png"
    try:
        png = page.screenshot(path=str(screenshot_path), full_page=True)
        # Attach the same screenshot to the Allure report for that test.
        allure.attach(png, name=item.name, attachment_type=allure.attachment_type.PNG)
    except Exception:
        # A screenshot is best-effort; never mask the real test failure.
        pass


DEFAULT_BASE_URL = "https://dragondaddy2021.github.io/oddlot"
DEFAULT_SUPABASE_URL = "https://mmcoqujhhrltdaozfkwj.supabase.co"
DEFAULT_SUPABASE_KEY = "sb_publishable_r3aGW9I-7L88V_4cAD-RzQ_BajY_hDU"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--headed", action="store_true", default=False, help="Run browser tests in headed mode")
    parser.addoption("--slowmo", action="store", default=0, type=int, help="Playwright slow motion in milliseconds")


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def supabase_url() -> str:
    return os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def supabase_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY", DEFAULT_SUPABASE_KEY)


@pytest.fixture(scope="session")
def endpoint_config() -> dict[str, str]:
    return {
        "ai_recommendation": os.getenv("AI_RECOMMENDATION_ENDPOINT", "/rest/v1/ai_recommendations"),
    }


@pytest.fixture(scope="session")
def web_content() -> dict[str, object]:
    """User-facing texts the tests assert against. Centralised so the suite can
    adapt to copy or i18n changes without touching test logic."""
    return {
        "site_title": os.getenv("SITE_TITLE", "龍爹地的零股投資學習平台"),
        "ai_section_heading": os.getenv("AI_SECTION_HEADING", "今日 AI 選股"),
        "disclaimer_text": os.getenv("DISCLAIMER_TEXT", "僅供參考"),
        "favorite_button_text": os.getenv("FAVORITE_BUTTON_TEXT", "登入以加入收藏"),
        "login_coming_soon_text": os.getenv("LOGIN_COMING_SOON_TEXT", "登入功能即將開放"),
        "load_error_text": os.getenv("LOAD_ERROR_TEXT", "資料載入失敗"),
        "metric_labels": ["殖利率", "本益比", "填息速度", "填息率"],
        "nav_links": ["首頁", "我的最愛", "我的 ETF", "選股說明"],
        "expected_stock_count": int(os.getenv("EXPECTED_STOCK_COUNT", "10")),
    }


@pytest.fixture(scope="session")
def api_client(supabase_url: str, supabase_key: str) -> ApiClient:
    return ApiClient(
        supabase_url,
        default_headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
    )


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
    headed = bool(request.config.getoption("--headed"))
    slow_mo = int(request.config.getoption("--slowmo"))

    if headed or slow_mo:
        with sync_playwright() as playwright:
            headed_browser = playwright.chromium.launch(headless=not headed, slow_mo=slow_mo)
            context = headed_browser.new_context()
            page = context.new_page()
            yield page
            context.close()
            headed_browser.close()
        return

    context: BrowserContext = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
