from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CustomerTier(str, Enum):
    GOLD = "Gold"
    SILVER = "Silver"
    STANDARD = "Standard"


class Customer(BaseModel):
    id: str
    name: str
    tier: CustomerTier
    max_allowed_discount_pct: float


class Product(BaseModel):
    sku: str
    name: str
    unit_price: float
    stock: int


class RequestedItem(BaseModel):
    sku: str
    quantity: int


class ExtractedQuoteRequest(BaseModel):
    customer_id: Optional[str] = None
    items: List[RequestedItem] = []
    location: Optional[str] = None
    required_date: Optional[str] = None
    requested_discount_pct: float = 0.0


class CalculatedItem(BaseModel):
    sku: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class QuoteDraft(BaseModel):
    customer_id: str
    customer_name: str
    customer_tier: CustomerTier
    items: List[CalculatedItem]
    subtotal: float
    discount_pct: float
    discount_amount: float
    total_usd: float
    requires_approval: bool = False
    approval_reasons: List[str] = []


class ValidationStatus(str, Enum):
    READY = "READY"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN_CUSTOMER = "UNKNOWN_CUSTOMER"
    UNKNOWN_PRODUCT = "UNKNOWN_PRODUCT"
    NEED_CLARIFICATION = "NEED_CLARIFICATION"