# QuoteFlow - Sistema Agéntico de Cotizaciones B2B (AndesPro Industrial)

QuoteFlow es un MVP full-stack diseñado para automatizar la preparación de cotizaciones industriales B2B a partir de solicitudes en lenguaje natural. Utiliza **LangGraph** para la orquestación de flujos agénticos con **Human-in-the-Loop (HITL)** y un motor comercial determinista aislado de alucinaciones.

---

## 🏛️ Arquitectura General

```text
 ┌────────────────────────────────────────────────────────┐
 │                   Next.js 14 Frontend                  │
 │   - Feature-Driven Architecture (src/modules/quotes)   │
 └───────────────────────────┬────────────────────────────┘
                             │ REST API
 ┌───────────────────────────▼────────────────────────────┐
 │                   FastAPI Backend                      │
 │  ┌──────────────────────────────────────────────────┐  │
 │  │              LangGraph Workflow Engine           │  │
 │  │  - Nodos: Extracción LLM, Validaciones, HITL     │  │
 │  │  - Checkpointer Persistente: AsyncPostgresSaver  │  │
 │  └───────────────────────────┬──────────────────────┘  │
 │                              │ Invoca
 ┌──────────────────────────────▼─────────────────────────┐
 │               Dominio Determinista (Python)             │
 │  - Reglas de Precios, Stock, Tiers y Aprobaciones       │
 └────────────────────────────────────────────────────────┘
```

---

## 🚀 Guía de Inicio Rápido (Entorno Limpio)

### Requisitos Previos
- Docker Desktop con Docker Compose V2.
- Python 3.11+.
- Node.js 18+.

### 1. Iniciar Base de Datos PostgreSQL
```bash
docker compose up -d
```

### 2. Iniciar Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env # Configura tus API Keys si deseas usar LLM Live
python -m pytest     # Ejecutar suite de pruebas
uvicorn app.main:app --reload --port 8000
```

### 3. Iniciar Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev
```

Abre tu navegador en `http://localhost:3000`.

---

## 📄 Gobernanza y Documentación Viva (Docs)

Toda la documentación técnica y de negocio se encuentra dentro de la carpeta `docs/`:

- [`BUSINESS_CASE.md`](docs/BUSINESS_CASE.md): Problema de negocio, hipótesis de valor y métricas.
- [`REQUIREMENTS.md`](docs/REQUIREMENTS.md): Requisitos funcionales y no funcionales.
- [`ADR-001`](docs/ADR-001-ARCHITECTURE-LANGGRAPH-POSTGRES.md): Decisión de arquitectura del grafo y persistencia.
- [`AGENTS.md`](docs/AGENTS.md): Fuente de verdad y normas de desarrollo para GitHub Copilot.
- [`EVIDENCE.md`](docs/EVIDENCE.md): Evidencia de prueba de los 3 casos mínimos del reto.
- [`AI_USE.md`](docs/AI_USE.md): Informe de uso asistido de IA.