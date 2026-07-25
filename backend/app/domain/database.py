from typing import Dict, Optional
from app.domain.models import Customer, CustomerTier, Product

# Catálogo Mock de Clientes de AndesPro Industrial
CUSTOMERS_DB: Dict[str, Customer] = {
    "CUST-GOLD-01": Customer(
        id="CUST-GOLD-01",
        name="Corporación Minera del Sur",
        tier=CustomerTier.GOLD,
        max_allowed_discount_pct=10.0,
    ),
    "CUST-SILVER-01": Customer(
        id="CUST-SILVER-01",
        name="Constructora Arequipa S.A.",
        tier=CustomerTier.SILVER,
        max_allowed_discount_pct=5.0,
    ),
    "CUST-STD-01": Customer(
        id="CUST-STD-01",
        name="Talleres Industriales Lima",
        tier=CustomerTier.STANDARD,
        max_allowed_discount_pct=0.0,
    ),
}

# Catálogo Mock de Productos e Inventario
PRODUCTS_DB: Dict[str, Product] = {
    "HX-200": Product(
        sku="HX-200",
        name="Casco Industrial de Alta Proteccion",
        unit_price=50.0,
        stock=500,
    ),
    "TX-500": Product(
        sku="TX-500",
        name="Bota de Seguridad Dielectrica",
        unit_price=120.0,
        stock=5,  # Stock bajo intencional para probar caso de excepcion
    ),
    "GL-100": Product(
        sku="GL-100",
        name="Guantes Kevlar Multipropósito",
        unit_price=15.0,
        stock=500,
    ),
}


def get_customer(customer_id: str) -> Optional[Customer]:
    return CUSTOMERS_DB.get(customer_id.upper())


def get_product(sku: str) -> Optional[Product]:
    return PRODUCTS_DB.get(sku.upper())