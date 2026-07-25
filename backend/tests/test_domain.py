import pytest
from app.domain.models import ExtractedQuoteRequest, RequestedItem, ValidationStatus
from app.domain.services import calculate_quote_draft

def test_standard_quote_auto_approved():
    """
    CASO 1: Cotización Estándar (Aprobación Automática).
    
    Escenario:
    - Cliente Gold (Máximo descuento permitido: 10%).
    - Solicitud de 20 cascos HX-200 ($50 c/u) = $1,000 subtotal.
    - Descuento solicitado: 8% (Dentro del margen permitido).
    
    Resultado Esperado:
    - Estado 'READY' (Lista para borrador).
    - Total de $920.0 USD.
    - No requiere aprobación humana (`requires_approval == False`).
    """
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
    """
    CASO 2: Excepción por Exceso de Descuento (Dispara Human-in-the-Loop).
    
    Escenario:
    - Cliente Standard (Máximo descuento permitido: 0%).
    - Solicitud de 10 cascos HX-200 ($50 c/u) = $500 subtotal.
    - Descuento solicitado: 5% (Excede el 0% asignado a su política).
    
    Resultado Esperado:
    - Estado 'REQUIRES_APPROVAL'.
    - Flag `requires_approval == True`.
    - Motivo explícito indicando la violación de la política comercial de descuento.
    """
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
    """
    CASO 3: Excepción por Monto Elevado > $10,000 USD (Dispara Human-in-the-Loop).
    
    Escenario:
    - Cliente Gold (Máximo descuento permitido: 10%).
    - Solicitud de 250 cascos HX-200 ($50 c/u) = $12,500 subtotal.
    - Descuento solicitado: 5% (Dentro de política, pero el monto total excede $10k).
    
    Resultado Esperado:
    - Estado 'REQUIRES_APPROVAL'.
    - Flag `requires_approval == True`.
    - Motivo explícito notificando que la cotización supera el umbral de $10,000 USD.
    """
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
    """
    CASO 4: Detención por Falta de Stock (Regla de Excepción RF4 / RF7).
    
    Escenario:
    - Solicitud de 50 botas TX-500.
    - Stock actual disponible en inventario mock: 5 unidades.
    
    Resultado Esperado:
    - Estado 'OUT_OF_STOCK' (Detiene el procesamiento).
    - No genera borrador de cotización (`draft is None`).
    - Devuelve una razón explicativa detallando las unidades faltantes para comunicación al usuario.
    """
    request = ExtractedQuoteRequest(
        customer_id="CUST-GOLD-01",
        items=[RequestedItem(sku="TX-500", quantity=50)], # Stock disponible: 5
        requested_discount_pct=0.0
    )
    status, draft, reasons = calculate_quote_draft(request)
    assert status == ValidationStatus.OUT_OF_STOCK
    assert draft is None
    assert "Stock insuficiente" in reasons[0]