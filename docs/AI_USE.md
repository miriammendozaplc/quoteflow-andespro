# AI_USE.md - Gobierno y Uso de Herramientas de IA

## 1. Herramientas Utilizadas
- **GitHub Copilot con Claude Sonnet (3.7 / 4.5):** Co-piloto para generación de scaffolding, funciones deterministas en Python, tipado de LangGraph y componentes UI en Next.js.

## 2. Rol Asignado
- **Rol:** Sr. Full-Stack Agentic Engineer.
- **Interacción:** Desarrollo asistido spec-driven siguiendo el ciclo corto de la metodología GSD (Discutir -> Planificar -> Ejecutar -> Verificar -> Handoff).

## 3. Decisiones Aceptadas vs. Refactorizadas
- **Aceptado:**
  - Esquema explícito de `QuoteState` con TypedDict en LangGraph.
  - Persistencia con `AsyncPostgresSaver` y llamadas a `interrupt()`.
  - Estructura por características (*Feature-Driven Architecture*) en Next.js.
- **Refactorizado / Corregido:**
  - Fallback mock del agente: Se reemplazaron expresiones fijas por patrones Regex para soportar cantidades dinámicas y descuentos ingresados en el texto libre sin alucinar.
  - Configuración de Tailwind CSS: Se añadió la ruta `./src/modules/**/*.{js,ts,jsx,tsx,mdx}` al scanner de clases para evitar que los componentes perdieran diseño al clonar en limpio.

## 4. Estrategia de Verificación
- Ejecución continua de la suite unitaria e integración con `pytest`.
- Verificación del comportamiento del checkpointer persistente en PostgreSQL ante pausado/reanudación del servidor.