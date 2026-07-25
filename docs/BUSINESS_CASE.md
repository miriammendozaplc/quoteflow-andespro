# BUSINESS_CASE.md - QuoteFlow (AndesPro Industrial)

## 1. Usuario y Proceso Actual
- **Usuario Objetivo:** Ejecutivo de Ventas B2B de AndesPro Industrial.
- **Proceso Manual:** El ejecutivo recibe correos, mensajes de texto o formularios con requerimientos en lenguaje natural (ej. *"Necesito 20 cascos HX-200 para Arequipa, cliente Gold, 8% descuento"*). Debe buscar manualmente al cliente en el sistema, revisar stock en inventario, verificar la política de descuentos, solicitar aprobación por correo al gerente de ventas si excede los límites, calcular el precio final y redactar la respuesta.
- **Problema:** Alto *lead time* (promedio 45 minutos por cotización), riesgo de errores de cálculo, pérdida de margen por descuentos mal aplicados y falta de trazabilidad en las aprobaciones.

---

## 2. Hipótesis de Valor y Propuesta MVP
- **Hipótesis:** Automatizar la extracción de datos en lenguaje natural y la ejecución de reglas comerciales mediante un flujo agéntico con control humano reduciendo el tiempo de generación de borradores a **menos de 2 minutos**, sin comprometer el margen ni el control operacional.
- **En Alcance:**
  - Ingesta de solicitudes en texto libre.
  - Extracción de entidades estructuradas mediante LLM.
  - Validación determinista contra base de datos local (Clientes, Catálogo, Stock, Políticas).
  - Pausa y reanudación persistente (*Human-in-the-Loop*) para aprobaciones por monto (> USD 10,000) o excepción de descuento.
  - Emisión de borrador final de cotización.
- **Fuera de Alcance (No Alcance Priorizado - 20%):**
  - Envío automático de correos o mensajes al cliente.
  - Integración en tiempo real con ERPs de producción (SAP/Oracle).
  - Autenticación empresarial multi-tenancy.

---

## 3. Métricas de Éxito y Métrica de Guardia

| Métrica | Objetivo | Tipo |
| :--- | :--- | :--- |
| **Tiempo de Preparación (Lead Time)** | Reducir de 45 min a < 2 min por borrador | Éxito |
| **Tasa de Cotizaciones Procesadas Automáticamente** | > 70% de solicitudes procesadas sin intervención (Caso Estándar) | Éxito |
| **Tasa de Error en Precios o Stock Alucinados** | **0% Stricto** (Garantizado por Dominio Determinista) | **Métrica de Guardia** |

---

## 4. Matriz de Autonomía y Riesgos

- **Nivel de Autonomía Recomendado:** **Borradores Automáticos con Aprobación Condicional (Human-in-the-Loop)**.
- **Gatillos de Interrupción (HITL):**
  1. Cotización superior a **USD 10,000**.
  2. Descuento solicitado superior al permitido por el Tier del cliente (Gold: 10%, Silver: 5%, Standard: 0%).
  3. Cliente no registrado o sin historial.