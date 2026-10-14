import httpx

from receipt_marketplace.infrai_email import InfraiEmail


def test_send_decodes_envelope_and_retries_rate_limit() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "0"},
                json={"ok": False, "data": None, "error": {"code": "RATE_LIMIT"}, "metadata": {}},
            )
        return httpx.Response(
            200,
            json={"ok": True, "data": {"message_id": "msg_42"}, "error": None, "metadata": {}},
        )

    client = InfraiEmail(
        api_key="test-key",
        transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )

    message_id = client.send_receipt(
        to="buyer@example.com",
        subject="Receipt",
        html="<p>Ready</p>",
        idempotency_key="marketplace-receipt-42",
    )

    assert message_id == "msg_42"
    assert [request.method for request in requests] == ["POST", "POST"]
    assert requests[1].headers["Idempotency-Key"] == "marketplace-receipt-42"

