from typing import List, Tuple
from app.domain.database import get_customer, get_product
from app.domain.models import (
    CalculatedItem,
    ExtractedQuoteRequest,
    QuoteDraft,
    ValidationStatus,
)

APPROVAL_THRESHOLD_USD = 10000.0


def check_stock_availability(items: List[dict]) -> Tuple[bool, List[str]]:
    """Verifica si hay stock suficiente para todos los productos solicitados."""
    missing_stock_info = []
    for item in items:
        sku = item.get("sku", "").upper()
        qty = item.get("quantity", 0)
        product = get_product(sku)

        if not product:
            missing_stock_info.append(f"Producto desconocido: SKU '{sku}'")
        elif product.stock < qty:
            missing_stock_info.append(
                f"Stock insuficiente para {product.name} ({sku}). "
                f"Solicitado: {qty}, Disponible: {product.stock}"
            )

    has_stock = len(missing_stock_info) == 0
    return has_stock, missing_stock_info


def calculate_quote_draft(request: ExtractedQuoteRequest) -> Tuple[ValidationStatus, Optional[QuoteDraft], List[str]]:
    """
    Calcula determinísticamente la cotización y evalúa políticas comerciales.
    NUNCA delega cálculos al LLM.
    """
    reasons = []

    # 1. Validar Cliente
    if not request.customer_id:
        return ValidationStatus.NEED_CLARIFICATION, None, ["No se proporcionó ID de cliente."]

    customer = get_customer(request.customer_id)
    if not customer:
        return ValidationStatus.UNKNOWN_CUSTOMER, None, [f"Cliente '{request.customer_id}' no encontrado en el sistema."]

    # 2. Validar Productos y Stock
    if not request.items:
        return ValidationStatus.NEED_CLARIFICATION, None, ["No se encontraron productos en la solicitud."]

    for item in request.items:
        product = get_product(item.sku)
        if not product:
            return ValidationStatus.UNKNOWN_PRODUCT, None, [f"Producto con SKU '{item.sku}' no existe en el catálogo."]
        if product.stock < item.quantity:
            return ValidationStatus.OUT_OF_STOCK, None, [
                f"Stock insuficiente para {product.name} ({item.sku}). Solicitado: {item.quantity}, Stock actual: {product.stock}"
            ]

    # 3. Calcular Totales Deterministas
    calculated_items: List[CalculatedItem] = []
    subtotal_general = 0.0

    for item in request.items:
        product = get_product(item.sku)
        item_subtotal = product.unit_price * item.quantity
        subtotal_general += item_subtotal

        calculated_items.append(
            CalculatedItem(
                sku=product.sku,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=product.unit_price,
                subtotal=item_subtotal,
            )
        )

    # 4. Evaluar Políticas de Descuento
    requested_discount = request.requested_discount_pct
    max_allowed_discount = customer.max_allowed_discount_pct
    requires_approval = False

    if requested_discount > max_allowed_discount:
        requires_approval = True
        reasons.append(
            f"Descuento solicitado ({requested_discount}%) excede el máximo permitido "
            f"para cliente {customer.tier.value} ({max_allowed_discount}%)."
        )

    discount_to_apply = requested_discount if not requires_approval else requested_discount
    discount_amount = subtotal_general * (discount_to_apply / 100.0)
    total_usd = subtotal_general - discount_amount

    # 5. Evaluar Umbral de Monto (> $10,000 USD) Requiere Aprobación
    if total_usd > APPROVAL_THRESHOLD_USD:
        requires_approval = True
        reasons.append(
            f"Monto total (${total_usd:,.2f} USD) supera el umbral de aprobación automática (${APPROVAL_THRESHOLD_USD:,.2f} USD)."
        )

    # 6. Construir Borrador
    draft = QuoteDraft(
        customer_id=customer.id,
        customer_name=customer.name,
        customer_tier=customer.tier,
        items=calculated_items,
        subtotal=subtotal_general,
        discount_pct=discount_to_apply,
        discount_amount=discount_amount,
        total_usd=total_usd,
        requires_approval=requires_approval,
        approval_reasons=reasons,
    )

    status = ValidationStatus.REQUIRES_APPROVAL if requires_approval else ValidationStatus.READY
    return status, draft, reasons