from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page, base_url: str, content: dict) -> None:
        self.page = page
        self.base_url = base_url
        self.content = content

    def open(self) -> None:
        # networkidle so the Supabase recommendation fetch has resolved.
        self.page.goto(f"{self.base_url}/", wait_until="networkidle")

    def assert_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name=self.content["ai_section_heading"])).to_be_visible()

    def assert_disclaimer_visible(self) -> None:
        expect(self.page.get_by_text(self.content["disclaimer_text"]).first).to_be_visible()

    def assert_navigation_visible(self) -> None:
        for name in self.content["nav_links"]:
            expect(self.page.get_by_role("link", name=name, exact=True).first).to_be_visible()

    def stock_card_count(self) -> int:
        # Each recommendation card carries exactly one "add to favorites" button.
        return self.page.get_by_role("button", name=self.content["favorite_button_text"]).count()
