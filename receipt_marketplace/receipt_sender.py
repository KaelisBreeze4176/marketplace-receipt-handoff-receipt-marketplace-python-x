from collections import defaultdict
from html import escape

from .infrai_email import InfraiEmail
from .models import OrderState, ReceiptHandoff, ReceiptRequest


class OrderNotReady(ValueError):
    pass


def render_receipt(order: ReceiptRequest) -> str:
    by_seller: dict[str, list[str]] = defaultdict(list)
    for asset in order.assets:
        price = f"${asset.price_cents / 100:.2f}"
        by_seller[asset.seller_name].append(
            f'<li><a href="{escape(str(asset.download_url))}">'
            f"{escape(asset.title)}</a> - {price}</li>"
        )

    sections = "".join(
        f"<h2>{escape(seller)}</h2><ul>{''.join(items)}</ul>"
        for seller, items in sorted(by_seller.items())
    )
    total = sum(asset.price_cents for asset in order.assets) / 100
    return (
        f"<h1>Thanks, {escape(order.buyer_name)}</h1>"
        f"<p>Order {escape(order.order_id)} is paid. Your downloads are ready.</p>"
        f"{sections}<p><strong>Total: ${total:.2f}</strong></p>"
    )


def hand_off_order(order: ReceiptRequest, email: InfraiEmail) -> ReceiptHandoff:
    if order.state is not OrderState.paid:
        raise OrderNotReady("Receipt handoff requires a paid order")

    message_id = email.send_receipt(
        to=str(order.buyer_email),
        subject=f"Receipt and downloads for order {order.order_id}",
        html=render_receipt(order),
        idempotency_key=f"marketplace-receipt-{order.order_id}",
    )
    email_record = email.get_email(message_id)
    return ReceiptHandoff(
        order_id=order.order_id,
        message_id=message_id,
        email_record=email_record,
    )

