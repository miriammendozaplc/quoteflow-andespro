import pytest
from app.domain.models import ExtractedQuoteRequest, RequestedItem, ValidationStatus
from app.domain.services import calculate_quote_draft

def test_standard_quote_auto_approved():
    request = ExtractedQuoteRequest(
        customer_id="CUST-GOLD-01",  # Max desc 10%
        items=[RequestedItem(sku="HX-200", quantity=20)], # 20 * $50 = $1,000
        requested_discount_pct=8.0
    )
    status, draft, reasons = calculate_quote_draft(request)
    assert status == ValidationStatus.READY
    assert draft is not None
    assert draft.total_usd == 920.0
    assert draft.requires_approval is False

def test_quote_exceeds_discount_requires_approval():
    request = ExtractedQuoteRequest(
        customer_id="CUST-STD-01",  # Max desc 0%
        items=[RequestedItem(sku="HX-200", quantity=10)], # 10 * $50 = $500
        requested_discount_pct=5.0  # Pide 5% excede su 0%
    )
    status, draft, reasons = calculate_quote_draft(request)
    assert status == ValidationStatus.REQUIRES_APPROVAL
    assert draft.requires_approval is True
    assert "excede el máximo permitido" in reasons[0]

def test_quote_exceeds_monto_threshold_requires_approval():
    request = ExtractedQuoteRequest(
        customer_id="CUST-GOLD-01",
        items=[RequestedItem(sku="HX-200", quantity=250)], # 250 * $50 = $12,500 (> $10k)
        requested_discount_pct=5.0
    )
    status, draft, reasons = calculate_quote_draft(request)
    assert status == ValidationStatus.REQUIRES_APPROVAL
    assert draft.requires_approval is True
    assert "supera el umbral" in reasons[0]

def test_out_of_stock_triggers_error():
    request = ExtractedQuoteRequest(
        customer_id="CUST-GOLD-01",
        items=[RequestedItem(sku="TX-500", quantity=50)], # Stock disponible: 5
        requested_discount_pct=0.0
    )
    status, draft, reasons = calculate_quote_draft(request)
    assert status == ValidationStatus.OUT_OF_STOCK
    assert draft is None
    assert "Stock insuficiente" in reasons[0]