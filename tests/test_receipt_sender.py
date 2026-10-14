from typing import Any

import pytest

from receipt_marketplace.models import ReceiptRequest
from receipt_marketplace.receipt_sender import OrderNotReady, hand_off_order


class RecordingEmail:
    def __init__(self) -> None:
        self.sent: dict[str, Any] | None = None

    def send_receipt(self, **payload: Any) -> str:
        self.sent = payload
        return "msg_receipt_1042"

    def get_email(self, message_id: str) -> dict[str, object]:
        return {"message_id": message_id}


def order(state: str = "paid") -> ReceiptRequest:
    return ReceiptRequest.model_validate(
        {
            "order_id": "ORDER-1042",
            "buyer_email": "buyer@example.com",
            "buyer_name": "Avery",
            "state": state,
            "assets": [
                {
                    "seller_name": "Studio Grid",
                    "title": "Dashboard icons",
                    "download_url": "https://example.com/icons",
                    "price_cents": 1800,
                },
                {
                    "seller_name": "Northwind Type",
                    "title": "Field Notes font",
                    "download_url": "https://example.com/font",
                    "price_cents": 3200,
                },
            ],
        }
    )


def test_paid_order_hands_off_seller_assets_then_reads_email_record() -> None:
    email = RecordingEmail()

    result = hand_off_order(order(), email)  # type: ignore[arg-type]

    assert result.message_id == "msg_receipt_1042"
    assert result.email_record == {"message_id": "msg_receipt_1042"}
    assert email.sent is not None
    assert email.sent["idempotency_key"] == "marketplace-receipt-ORDER-1042"
    assert "Northwind Type" in email.sent["html"]
    assert "Studio Grid" in email.sent["html"]
    assert "Total: $50.00" in email.sent["html"]


def test_pending_order_never_sends_buyer_update() -> None:
    email = RecordingEmail()

    with pytest.raises(OrderNotReady):
        hand_off_order(order("pending"), email)  # type: ignore[arg-type]

    assert email.sent is None

