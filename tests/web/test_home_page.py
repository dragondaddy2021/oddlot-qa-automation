import pytest

from pages.home_page import HomePage


@pytest.mark.web
@pytest.mark.smoke
def test_home_page_loads_successfully(page, base_url, web_content) -> None:
    home_page = HomePage(page, base_url, web_content)

    home_page.open()

    home_page.assert_loaded()
    home_page.assert_disclaimer_visible()
    home_page.assert_navigation_visible()


@pytest.mark.web
@pytest.mark.ai
def test_home_displays_expected_number_of_stock_cards(page, base_url, web_content) -> None:
    home_page = HomePage(page, base_url, web_content)

    home_page.open()

    assert home_page.stock_card_count() == web_content["expected_stock_count"]
