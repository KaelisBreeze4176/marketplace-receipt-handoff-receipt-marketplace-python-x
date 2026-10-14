import os

from receipt_marketplace.infrai_email import InfraiEmail
from receipt_marketplace.models import ReceiptRequest
from receipt_marketplace.receipt_sender import hand_off_order


def main() -> None:
    buyer_email = os.environ.get("DEMO_BUYER_EMAIL")
    if not buyer_email:
        raise RuntimeError("Set DEMO_BUYER_EMAIL to the receipt destination")

    order = ReceiptRequest.model_validate(
        {
            "order_id": "ORDER-1042",
            "buyer_email": buyer_email,
            "buyer_name": "Avery",
            "state": "paid",
            "assets": [
                {
                    "seller_name": "Northwind Type",
                    "title": "Field Notes font family",
                    "download_url": "https://example.com/downloads/order-1042/font",
                    "price_cents": 3200,
                },
                {
                    "seller_name": "Studio Grid",
                    "title": "Dashboard icon set",
                    "download_url": "https://example.com/downloads/order-1042/icons",
                    "price_cents": 1800,
                },
            ],
        }
    )
    result = hand_off_order(order, InfraiEmail())
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

