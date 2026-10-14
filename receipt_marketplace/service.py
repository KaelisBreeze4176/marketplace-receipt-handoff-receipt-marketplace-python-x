from fastapi import Depends, FastAPI, HTTPException

from .infrai_email import InfraiEmail, InfraiError
from .models import ReceiptHandoff, ReceiptRequest
from .receipt_sender import OrderNotReady, hand_off_order

app = FastAPI(title="Marketplace receipt handoff")


def email_client() -> InfraiEmail:
    return InfraiEmail()


@app.post("/orders/handoff", response_model=ReceiptHandoff)
def create_handoff(
    order: ReceiptRequest, email: InfraiEmail = Depends(email_client)
) -> ReceiptHandoff:
    try:
        return hand_off_order(order, email)
    except OrderNotReady as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InfraiError as exc:
        caller_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=caller_status,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc

