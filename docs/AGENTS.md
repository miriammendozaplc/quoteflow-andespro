# AGENTS.md - Instrucciones y Reglas de Trabajo para Agentes de IA

Este documento define la fuente de verdad, convenciones de ingeniería, restricciones y criterios de aceptación para las herramientas de IA que colaboran en el repositorio de **QuoteFlow**.

---

## 1. Contexto del Proyecto y Arquitectura

- **Negocio:** Cotizador B2B automatizado con control humano para equipos industriales (AndesPro Industrial).
- **Backend:** Python 3.11+, FastAPI, LangGraph, PostgreSQL (`AsyncPostgresSaver`).
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS (Feature-Driven / Stream Architecture).
- **Checkpointer:** Persistente en Docker/PostgreSQL para reanudación durable.

---

## 2. Comandos de Entorno y Ejecución

- **Servicios e Infraestructura:** `docker-compose up -d` (Postgres on port 5432).
- **Run Backend:** `cd backend && uvicorn app.main:app --reload`
- **Run Frontend:** `cd frontend && npm run dev`
- **Testing:** `pytest` (Backend unit & integration tests).

---

## 3. Reglas de Oro y Restricciones Estrictas (Do-Not Rules)
- 🛑 **Prohibido Lógica LLM en Cálculos Comercial/Financieros** El modelo de lenguaje NO DEBE calcular precios, aplicar descuentos, verificar stock ni inventar clientes. Toda la lógica determinista vive exclusivamente en backend/app/domain/services.py. `backend/app/domain/services.py`.
- 🛑 **Cero Secretos en Commits** Nunca registres API Keys (OpenAI/Anthropic) ni credenciales en código (usar `.env.example`).
- 🛑 **Protección contra Inyección de Prompts** El texto ingresado por el cliente es entrada no confiable. El LLM solo extrae entidades estructuradas y jamás puede modificar las políticas comerciales o instrucciones del sistema.
- 🛑 **Idempotencia en Decisiones Humanas** La reanudación de una cotización mediante aprobación o rechazo humano (`interrupt`) no debe duplicar cálculos, generar efectos secundarios dobles ni alterar la trazabilidad previa.

---

## 4. Estándares de Código y Git

- **Convención de Commits (Conventional Commits):**
  - `docs(gsd): ...` para cambios en la gobernanza del proyecto y fuentes de verdad en Markdown (`.md`).
  - `feat(domain): ...` para modelos y funciones de lógica comercial determinista (precios, stock, políticas).
  - `feat(agent): ...` para construcción del grafo de LangGraph, nodos, rutas condicionales e interrupciones (`interrupt`).
  - `feat(api): ...` para endpoints de la API REST en FastAPI.
  - `feat(ui): ...` para componentes y módulos de interfaz en Next.js.
  - `test(evals): ...` para suites de prueba, evals y generación de evidencias.

- **Estructura de Ramas (GSD Cycle):**
  - Cada fase del desarrollo debe trabajarse en su rama correspondiente (`docs/gsd-setup`, `feat/domain-core`, `feat/agent-graph`, `feat/fullstack-app`, `test/evidence`).

- **Frontend Architecture:**
  - Desarrollo modular basado en **Feature-Driven Architecture** (`frontend/src/modules/quotes/`).
  - Tipado estricto reutilizando esquemas exportados desde OpenAPI/Pydantic.

---

## 5. Criterios de Aceptación (Definition of Done)

Una tarea o fase solo se considerará **completada** si satisface la siguiente lista de verificación:

- [ ] **Pruebas Automatizadas en Verde:** Toda la suite de `pytest` se ejecuta exitosamente, incluyendo el modo de prueba offline (*Mock LLM*).
- [ ] **Reanudación Durable Probada:** Se ha verificado que al apagar y levantar el servidor FastAPI, la ejecución pausada se reanuda correctamente desde PostgreSQL mediante el `thread_id`.
- [ ] **Reglas Protegidas sin Alucinaciones:** Ningún cálculo de precio o descuento proviene del LLM; todos son generados por las funciones deterministas del dominio.
- [ ] **Trazabilidad Completa:** El historial de nodos ejecutados y decisiones humanas es visible tanto en la API como en la interfaz de Next.js.
- [ ] **Evidencia Registrada:** Los 3 casos de uso principales (Caso Estándar, Caso Falta de Stock y Caso Aprobación HITL) cuentan con sus logs y cargas útiles documentadas en `EVIDENCE.md`.