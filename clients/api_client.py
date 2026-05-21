from typing import Any

import requests


class ApiClient:
    """Thin requests wrapper that applies a set of default headers (e.g. the
    Supabase apikey / Authorization pair) to every call while still allowing
    per-request overrides."""

    def __init__(self, base_url: str, timeout: int = 15, default_headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = default_headers or {}

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        headers = self._merge_headers(kwargs.pop("headers", None))
        return requests.get(self._url(path), timeout=self.timeout, headers=headers, **kwargs)

    def post(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> requests.Response:
        headers = self._merge_headers(kwargs.pop("headers", None))
        return requests.post(self._url(path), json=json, timeout=self.timeout, headers=headers, **kwargs)

    def _merge_headers(self, extra: dict[str, str] | None) -> dict[str, str]:
        merged = dict(self.default_headers)
        if extra:
            merged.update(extra)
        return merged

    def _url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{normalized_path}"
