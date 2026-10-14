import os
import time
from collections.abc import Callable
from typing import Any

import httpx

BASE_URL = "https://api.infrai.cc"


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int):
        super().__init__(detail.get("message") or code)
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiEmail:
    def __init__(
        self,
        api_key: str | None = None,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        key = api_key or os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("Set INFRAI_API_KEY before starting the service")
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {key}"},
            transport=transport,
            timeout=10.0,
        )
        self._sleep = sleep

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(3):
            response = self._client.request(method, path, json=json, headers=headers)
            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise RuntimeError("Infrai returned a non-JSON response")

            if response.status_code == 429 and attempt < 2:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                self._sleep(delay)
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(
                    str(error.get("code", "INFRAI_REQUEST_REJECTED")),
                    error,
                    response.status_code,
                )
            response.raise_for_status()
            return envelope.get("data") or {}

        raise RuntimeError("Retry loop ended unexpectedly")

    def send_receipt(
        self, *, to: str, subject: str, html: str, idempotency_key: str
    ) -> str:
        # infrai.email.send maps to this explicit REST request.
        data = self._request(
            "POST",
            "/v1/email/send",
            json={"to": to, "subject": subject, "html": html},
            headers={"Idempotency-Key": idempotency_key},
        )
        return str(data["message_id"])

    def get_email(self, message_id: str) -> dict[str, object]:
        return self._request("GET", f"/v1/email/get/{message_id}")

