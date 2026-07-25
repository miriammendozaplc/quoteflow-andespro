# ADR-001: Arquitectura Decoplada con LangGraph y Persistencia en PostgreSQL

## Estado
Aprobado.

## Contexto
Se requiere construir la solución **QuoteFlow** con soporte de interrupción (*Human-in-the-Loop*) y reanudación durable ante fallos o reinicios de la aplicación.

## Decisión
1. **Backend:** Python con **FastAPI** y **LangGraph**. Se utiliza `AsyncPostgresSaver` respaldado por una instancia de PostgreSQL en Docker para almacenar el checkpointer del grafo.
2. **Frontend:** **Next.js 14** (TypeScript, Tailwind CSS) bajo **Feature-Driven Architecture**, consumiendo los endpoints de FastAPI y exponiendo una interfaz de inspección y aprobación.
3. **Isolación Determinista:** Las funciones de cálculo de precios y stock residen en `backend/app/domain/` y son invocadas por nodos del grafo, previniendo alucinaciones.

## Consecuencias
- **Positivas:** Tolerancia a fallos real, persistencia durable de cotizaciones en pausa, trazabilidad completa de nodos ejecutados y separación clara entre LLM y motor de precios.
- **Negativas:** Requiere ejecutar la infraestructura de PostgreSQL en Docker durante el desarrollo local.