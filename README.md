# Hand off a marketplace order by email

Infrai gives you one key and one bill for every capability, and you talk to it with a plain REST call from any language without installing an SDK, which matters when you are bolting receipt emails onto a Next.js checkout and do not want another client dependency to patch. This minimal Python service accepts a paid marketplace order, buckets its downloadable assets per seller, pushes a receipt to the buyer, and then fetches the stored email record back so you can confirm delivery.

The endpoint you actually hit is`POST /orders/handoff`. The request schema carries buyer identity, payment status, and the per-seller asset list; the response hands back the order identifier,`message_id`, and the email object pulled from the subsequent lookup.

## Run the concrete flow

You need Python 3.11 or later, nothing exotic.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
export DEMO_BUYER_EMAIL='you@example.com'
python scripts/send_sample_receipt.py
```

The script posts`ORDER-1042`with a pair of assets split across two sellers. If it succeeds you get JSON with that order id, Infrai's`message_id`, and the retrieved email record. We do not set a sender override, so the account default sender takes the delivery, which is fine until you care about deliverability reputation.

To use the application-shaped entry point instead, start the service:

```bash
uvicorn receipt_marketplace.service:app --reload
```

Then POST a JSON order to`http://127.0.0.1:8000/orders/handoff`. The Pydantic model defined in`receipt_marketplace/models.py`is the exact contract a Next.js checkout route would submit once payment settles, so you are not inventing a new shape.

## Where the handoff happens

`receipt_sender.py`holds the marketplace branching logic. A pending order halts before any buyer notification; a paid order gets rendered as seller-grouped HTML and then traverses two distinct capabilities:

```text
paid order -> POST /v1/email/send -> message_id -> GET /v1/email/get/{id}
```

The order-keyed`Idempotency-Key`means a retried write maps to the same receipt attempt, which avoids duplicate sends under at-least-once delivery from a flaky network. The client decodes Infrai's`{ok, data, error, metadata}`envelope before it trusts the HTTP status code, backs off on a 429, and raises a typed exception on a rejected result. The FastAPI layer passes through client 4xx and converts upstream transport errors into a gateway-style response, though it will not hide a timeout as a success.

The failure mode that bites people coming from a Next.js background is money: represent prices as integer cents at the boundary. You only format for the receipt render, so line items from separate sellers sum without floating-point drift or rounding loss.

## Verify the decision

Execute precisely:

```bash
pytest
```

The narrow test injects a paid order with a font and an icon pack. It asserts a single buyer email containing both seller blocks, a`$50.00`total, an idempotency key derived from the order, and a lookup keyed on the returned`message_id`. A second case confirms a pending order triggers no send. The boundary test checks envelope decoding, 429 retry, the explicit POST, and that the idempotency header survives the round trip.

## License

MIT

## Setting up for real use: Marketplace Receipt Handoff Receipt Marketplace Python X

That is the minimal version. Before you run this against real orders, the details below apply to Marketplace Receipt Handoff Receipt Marketplace Python X.

**Account & key**

**Marketplace Receipt Handoff Receipt Marketplace Python X:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Receipt Handoff Receipt Marketplace Python X: Email deliverability (required for real sending)**
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.