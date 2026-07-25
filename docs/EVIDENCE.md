# EVIDENCE.md - Registro de Evidencia de Ejecución y Evals

Este documento contiene la evidencia de prueba ejecutable para los 3 casos representativos del reto **QuoteFlow** en AndesPro Industrial.

---

## 🧪 Caso 1: Flujo Estándar (Aprobación Automática)

### Solicitud de Entrada
- **Cliente:** `CUST-GOLD-01`
- **Texto:** *"Necesito 20 cascos HX-200 para la planta de Arequipa. Requiero 8% de descuento."*

### Payload de Respuesta de la API (`/api/quotes`)
```json
{
  "thread_id": "thread_std_001",
  "is_paused": false,
  "state": {
    "request_id": "REQ-STD-01",
    "customer_id": "CUST-GOLD-01",
    "validation_status": "READY",
    "quote_draft": {
      "customer_name": "Corporación Minera del Sur",
      "customer_tier": "Gold",
      "items": [
        {
          "sku": "HX-200",
          "product_name": "Casco Industrial de Alta Proteccion",
          "quantity": 20,
          "unit_price": 50.0,
          "subtotal": 1000.0
        }
      ],
      "subtotal": 1000.0,
      "discount_pct": 8.0,
      "discount_amount": 80.0,
      "total_usd": 920.0,
      "requires_approval": false
    },
    "trace_logs": [
      "Nodo 'extract_intent_node': Iniciando extracción de entidades.",
      "Nodo 'extract_intent_node': Datos extraídos exitosamente. SKUs: ['HX-200']",
      "Nodo 'validate_domain_node': Ejecutando reglas deterministas de negocio.",
      "Nodo 'validate_domain_node': Resultado determinista -> READY",
      "Nodo 'finalize_quote_node': Cotización FINALIZADA exitosamente en estado listo."
    ]
  }
}
```

---

## 🧪 Caso 2: Excepción por Falta de Stock (Detención de Caso)

### Solicitud de Entrada
- **Cliente:** `CUST-GOLD-01`
- **Texto:** *"Necesito 50 botas TX-500 para la planta de Lima."* (Stock actual disponible: 5)

### Payload de Respuesta de la API (`/api/quotes`)
```json
{
  "thread_id": "thread_stock_002",
  "is_paused": false,
  "state": {
    "request_id": "REQ-STOCK-02",
    "customer_id": "CUST-GOLD-01",
    "validation_status": "OUT_OF_STOCK",
    "quote_draft": null,
    "validation_reasons": [
      "Stock insuficiente para Bota de Seguridad Dielectrica (TX-500). Solicitado: 50, Stock actual: 5"
    ],
    "trace_logs": [
      "Nodo 'extract_intent_node': Iniciando extracción de entidades.",
      "Nodo 'validate_domain_node': Ejecutando reglas deterministas de negocio.",
      "Nodo 'validate_domain_node': Resultado determinista -> OUT_OF_STOCK",
      "Flujo detenido: Excepción por inventario insuficiente registrada."
    ]
  }
}
```

---

## 🧪 Caso 3: Human-in-the-Loop (Monto > $10,000 USD y Reanudación Persistente)

### Paso 3.1: Ingesta e Interrupción (`interrupt`)
- **Cliente:** `CUST-GOLD-01`
- **Texto:** *"Necesito 250 cascos HX-200 para Arequipa. Requiero 5% de descuento."* (Monto: $11,875.00 USD)

#### Respuesta API (Estado Pausado):
```json
{
  "thread_id": "thread_hitl_003",
  "is_paused": true,
  "state": {
    "request_id": "REQ-HITL-03",
    "validation_status": "REQUIRES_APPROVAL",
    "requires_approval": true,
    "validation_reasons": [
      "Monto total ($11,875.00 USD) supera el umbral de aprobación automática ($10,000.00 USD)."
    ],
    "approval_status": "PENDING"
  }
}
```

### Paso 3.2: Reanudación por Usuario Humano (`/api/quotes/thread_hitl_003/resume`)
- **Payload Enviado por Frontend:** `{"action": "APPROVED", "comment": "Aprobado por Gerencia de Ventas"}`

#### Respuesta API (Post-Reanudación):
```json
{
  "thread_id": "thread_hitl_003",
  "status": "RESUMED",
  "state": {
    "validation_status": "READY",
    "approval_status": "APPROVED",
    "human_comment": "Aprobado por Gerencia de Ventas",
    "trace_logs": [
      "Nodo 'human_approval_node': PAUSANDO GRAFO. Esperando decisión humana (HITL).",
      "Nodo 'human_approval_node': REANUDADO por usuario -> Acción: APPROVED, Comentario: Aprobado por Gerencia de Ventas",
      "Nodo 'finalize_quote_node': Cotización FINALIZADA exitosamente en estado listo."
    ]
  }
}
```