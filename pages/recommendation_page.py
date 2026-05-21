import re

from playwright.sync_api import Page, expect


class RecommendationPage:
    """The AI recommendation experience lives on the home page (cards are
    rendered directly) plus the login-gated favourite action."""

    def __init__(self, page: Page, base_url: str, content: dict) -> None:
        self.page = page
        self.base_url = base_url
        self.content = content

    def open(self, wait_until: str = "networkidle") -> None:
        self.page.goto(f"{self.base_url}/", wait_until=wait_until)

    def open_login(self) -> None:
        self.page.goto(f"{self.base_url}/login", wait_until="networkidle")

    def assert_results_visible(self) -> None:
        expect(self.page.get_by_role("button", name=self.content["favorite_button_text"]).first).to_be_visible()

    def assert_card_metrics_visible(self) -> None:
        for label in self.content["metric_labels"]:
            expect(self.page.get_by_text(label).first).to_be_visible()

    def favorite_first_card(self) -> None:
        self.page.get_by_role("button", name=self.content["favorite_button_text"]).first.click()

    def assert_login_required_after_favorite(self) -> None:
        # Favouriting is gated behind auth: the click routes to the login page.
        expect(self.page).to_have_url(re.compile(r".*/login"))
        expect(self.page.get_by_text(self.content["login_coming_soon_text"]).first).to_be_visible()

    def assert_login_coming_soon(self) -> None:
        expect(self.page.get_by_text(self.content["login_coming_soon_text"]).first).to_be_visible()

    def assert_friendly_load_error(self) -> None:
        # When the data source is unavailable the shell stays up and shows a
        # friendly message rather than crashing.
        expect(self.page.get_by_text(self.content["load_error_text"]).first).to_be_visible()
