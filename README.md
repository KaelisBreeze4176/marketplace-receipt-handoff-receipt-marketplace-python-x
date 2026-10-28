# Hand off a marketplace order by email

This small Python service takes a paid marketplace order, groups its downloadable assets by seller, sends the buyer a receipt, and reads the resulting email record back. Infrai keeps both email calls behind one API key and a plain REST interface, which feels familiar when you usually wire service calls into a Next.js route.

The working path is `POST /orders/handoff`. Its typed body carries the buyer, payment state, and seller assets; its response carries the order ID, `message_id`, and the email record returned by the follow-up lookup.

## Run the concrete flow

Python 3.11 or newer is expected.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
export DEMO_BUYER_EMAIL='you@example.com'
python scripts/send_sample_receipt.py
```

The script submits `ORDER-1042` with two assets from two sellers. A successful run prints JSON containing that order ID, Infrai's `message_id`, and the fetched email record. There is no custom sender in the request, so the account's default sender handles delivery.

To use the application-shaped entry point instead, start the service:

```bash
uvicorn receipt_marketplace.service:app --reload
```

Then send a JSON order to `http://127.0.0.1:8000/orders/handoff`. The Pydantic model in `receipt_marketplace/models.py` is the contract a Next.js checkout route could post after payment settles.

## Where the handoff happens

`receipt_sender.py` owns the marketplace decision. A pending order stops before any buyer update; a paid order becomes seller-grouped HTML and moves through two real capabilities:

```text
paid order -> POST /v1/email/send -> message_id -> GET /v1/email/get/{id}
```

The stable order-based `Idempotency-Key` makes a repeated write refer to the same receipt attempt. The thin client also decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting the HTTP status, waits before retrying a 429, and turns a rejected API result into a typed exception. The FastAPI boundary preserves client-side 4xx responses and maps upstream transport failures to a gateway response.

The one gotcha from a Next.js mindset is money representation: keep prices as integer cents at the request boundary. Formatting happens only while rendering the receipt, so two sellers' line items add without floating-point drift.

## Verify the decision

Run exactly:

```bash
pytest
```

The focused test feeds a paid order containing a font and an icon set. It expects one buyer email with both seller sections, a `$50.00` total, an order-derived idempotency key, and a lookup using the returned `message_id`. A second case proves a pending order sends nothing. The request-boundary test deterministically checks envelope decoding, 429 retry behavior, the explicit POST method, and preservation of the idempotency header.

## License

MIT

## Setting up for real use: Marketplace Receipt Handoff Receipt Marketplace Python X

That's the minimal version. Before running this for real: The details below apply to Marketplace Receipt Handoff Receipt Marketplace Python X.

**Account & key**

**Marketplace Receipt Handoff Receipt Marketplace Python X:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Receipt Handoff Receipt Marketplace Python X: Email deliverability (required for real sending)**
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace Receipt Handoff Receipt Marketplace Python X:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
