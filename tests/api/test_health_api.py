import pytest
import requests


@pytest.mark.api
@pytest.mark.smoke
def test_frontend_site_is_reachable(base_url) -> None:
    response = requests.get(f"{base_url}/", timeout=15)

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()


@pytest.mark.api
@pytest.mark.smoke
def test_recommendation_api_is_available(api_client, endpoint_config) -> None:
    response = api_client.get(endpoint_config["ai_recommendation"], params={"select": "id", "limit": 1})

    assert response.status_code == 200
