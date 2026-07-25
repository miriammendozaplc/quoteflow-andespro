# REQUIREMENTS - QuoteFlow

## Requerimientos Funcionales (RF)
- **RF1 (Ingesta):** Registrar una solicitud recibiendo identificador de cliente y texto en lenguaje natural.
- **RF2 (Interpretación Estructurada):** Extraer productos, cantidades, ubicación, fecha requerida y descuento mediante salida Pydantic.
- **RF3 (Consulta de Dominio):** Consultar herramientas deterministas locales de clientes, catálogo, inventario y políticas.
- **RF4 (Validación y Rutado):** Clasificar la solicitud en: Aclaración, Producto Desconocido, Falta de Stock, Aprobación Requerida o Listo.
- **RF5 (Cálculo Determinista):** Calcular precio unitario, descuento aplicado y total exclusivamente desde funciones del dominio.
- **RF6 (Pausar y Reanudar HITL):** Interrumpir el grafo para aprobación/rechazo humano conservando el estado en PostgreSQL tras reinicios del sistema.
- **RF7 (Auditoría y Entrega):** Generar borrador final y mostrar registro de estados y decisiones tomadas.

## Requerimientos No Funcionales (RFN)
- **RFN1 (Orquestación):** Uso obligatorio de LangGraph con estado explícito y tipado.
- **RFN2 (Persistencia):** Checkpointer persistente con PostgreSQL (`AsyncPostgresSaver`).
- **RFN3 (Lógica Determinista Aislada):** Lógica financiera separada 100% de invocaciones al LLM.
- **RFN4 (Idempotencia):** Reanudaciones repetidas no generan duplicación de cálculos.