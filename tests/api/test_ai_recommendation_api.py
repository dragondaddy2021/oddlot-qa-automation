import pytest
import requests


REQUIRED_STOCK_FIELDS = ("symbol", "name", "reason")


def _latest_recommendation(api_client, endpoint: str) -> dict:
    response = api_client.get(endpoint, params={"select": "*", "order": "date.desc", "limit": 1})

    assert response.status_code == 200, response.text

    body = response.json()
    assert isinstance(body, list) and body, "expected a non-empty list of recommendation rows"
    return body[0]


@pytest.mark.api
@pytest.mark.ai
def test_latest_recommendation_has_valid_schema(api_client, endpoint_config) -> None:
    row = _latest_recommendation(api_client, endpoint_config["ai_recommendation"])

    assert isinstance(row.get("date"), str) and row["date"].strip()

    stocks = row.get("stocks")
    assert isinstance(stocks, list) and stocks, "row is missing the stocks list"
    assert len(stocks) == 10  # product contract: top 10 odd-lot picks

    for stock in stocks:
        for field in REQUIRED_STOCK_FIELDS:
            value = stock.get(field)
            assert isinstance(value, str) and value.strip(), f"missing/empty '{field}' in {stock}"


@pytest.mark.api
@pytest.mark.ai
def test_recommendation_numeric_fields_are_sane(api_client, endpoint_config) -> None:
    row = _latest_recommendation(api_client, endpoint_config["ai_recommendation"])

    for stock in row["stocks"]:
        assert isinstance(stock.get("price"), (int, float)) and stock["price"] > 0
        assert isinstance(stock.get("yield_rate"), (int, float)) and stock["yield_rate"] >= 0
        assert isinstance(stock.get("pe_ratio"), (int, float))


@pytest.mark.api
def test_request_without_apikey_is_rejected(supabase_url, endpoint_config) -> None:
    response = requests.get(
        f"{supabase_url}{endpoint_config['ai_recommendation']}",
        params={"select": "*", "limit": 1},
        timeout=15,
    )

    assert response.status_code == 401

    body = response.json()
    assert any(field in body for field in ("message", "error", "msg", "hint"))
