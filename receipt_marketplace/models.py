from enum import Enum

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class OrderState(str, Enum):
    pending = "pending"
    paid = "paid"


class SellerAsset(BaseModel):
    seller_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    download_url: HttpUrl
    price_cents: int = Field(ge=0)


class ReceiptRequest(BaseModel):
    order_id: str = Field(min_length=1)
    buyer_email: EmailStr
    buyer_name: str = Field(min_length=1)
    state: OrderState
    assets: list[SellerAsset] = Field(min_length=1)


class ReceiptHandoff(BaseModel):
    order_id: str
    message_id: str
    email_record: dict[str, object]

