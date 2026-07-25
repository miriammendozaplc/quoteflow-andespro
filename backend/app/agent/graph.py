import os
from typing import Literal
from psycopg_pool import AsyncConnectionPool
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agent.nodes import (
    extract_intent_node,
    finalize_quote_node,
    human_approval_node,
    validate_domain_node,
)
from app.agent.state import QuoteState
from app.domain.models import ValidationStatus


def route_next_step(state: QuoteState) -> Literal["human_approval_node", "finalize_quote_node", "__end__"]:
    """Enrutamiento condicional basado exclusivamente en la validación determinista."""
    status = state.get("validation_status")
    
    if status == ValidationStatus.REQUIRES_APPROVAL:
        return "human_approval_node"
    elif status == ValidationStatus.READY:
        return "finalize_quote_node"
    else:
        # Casos OUT_OF_STOCK, UNKNOWN_CUSTOMER, UNKNOWN_PRODUCT o NEED_CLARIFICATION terminan el flujo
        return END


def build_graph():
    """Construye el StateGraph de LangGraph."""
    workflow = StateGraph(QuoteState)
    
    # Agregar Nodos
    workflow.add_node("extract_intent_node", extract_intent_node)
    workflow.add_node("validate_domain_node", validate_domain_node)
    workflow.add_node("human_approval_node", human_approval_node)
    workflow.add_node("finalize_quote_node", finalize_quote_node)
    
    # Flujo de Aristas
    workflow.add_edge(START, "extract_intent_node")
    workflow.add_edge("extract_intent_node", "validate_domain_node")
    
    # Arista Condicional
    workflow.add_conditional_edges(
        "validate_domain_node",
        route_next_step,
        {
            "human_approval_node": "human_approval_node",
            "finalize_quote_node": "finalize_quote_node",
            END: END
        }
    )
    
    workflow.add_edge("human_approval_node", "finalize_quote_node")
    workflow.add_edge("finalize_quote_node", END)
    
    return workflow


async def get_compiled_graph():
    """Retorna el grafo compilado con checkpointer persistente de PostgreSQL."""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@localhost:5432/quoteflow_db")
    
    # Crear Pool de conexiones asíncronas para el Checkpointer
    pool = AsyncConnectionPool(conninfo=db_url, max_size=10, kwargs={"autocommit": True})
    checkpointer = AsyncPostgresSaver(pool)
    
    # Inicializar las tablas del checkpointer si no existen
    await checkpointer.setup()
    
    workflow = build_graph()
    return workflow.compile(checkpointer=checkpointer)