import pytest

from pages.recommendation_page import RecommendationPage


@pytest.mark.web
@pytest.mark.ai
def test_recommendation_cards_show_key_metrics(page, base_url, web_content) -> None:
    recommendation_page = RecommendationPage(page, base_url, web_content)

    recommendation_page.open()

    recommendation_page.assert_results_visible()
    recommendation_page.assert_card_metrics_visible()


@pytest.mark.web
@pytest.mark.ai
def test_adding_favorite_requires_login(page, base_url, web_content) -> None:
    recommendation_page = RecommendationPage(page, base_url, web_content)

    recommendation_page.open()
    recommendation_page.favorite_first_card()

    recommendation_page.assert_login_required_after_favorite()


@pytest.mark.web
def test_login_is_coming_soon(page, base_url, web_content) -> None:
    recommendation_page = RecommendationPage(page, base_url, web_content)

    recommendation_page.open_login()

    recommendation_page.assert_login_coming_soon()


@pytest.mark.web
@pytest.mark.ai
def test_friendly_error_when_data_source_unavailable(page, base_url, web_content) -> None:
    page.route("**/*supabase*/**", lambda route: route.abort())
    recommendation_page = RecommendationPage(page, base_url, web_content)

    recommendation_page.open(wait_until="domcontentloaded")

    recommendation_page.assert_friendly_load_error()
