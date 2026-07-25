import pytest
from app.agent.graph import build_graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

@pytest.mark.asyncio
async def test_graph_standard_flow_auto_completes():
    """Valida flujo estándar sin interrupción."""
    workflow = build_graph()
    app = workflow.compile(checkpointer=MemorySaver())
    
    initial_state = {
        "request_id": "REQ-001",
        "customer_id": "CUST-GOLD-01",
        "raw_text": "Necesito 20 cascos HX-200 para Arequipa con 8% descuento",
        "approval_status": "PENDING",
        "trace_logs": [],
        "errors": []
    }
    
    config = {"configurable": {"thread_id": "thread-1"}}
    final_state = await app.ainvoke(initial_state, config=config)
    
    assert final_state["validation_status"].value == "READY"
    assert final_state["requires_approval"] is False


@pytest.mark.asyncio
async def test_graph_hitl_interrupt_and_resume():
    """Valida la pausa con interrupt() y la reanudación al aprobar."""
    workflow = build_graph()
    app = workflow.compile(checkpointer=MemorySaver())
    
    # Solicitud > $10,000 USD (250 cascos * $50 = $12,500)
    initial_state = {
        "request_id": "REQ-002",
        "customer_id": "CUST-GOLD-01",
        "raw_text": "Necesito 250 cascos HX-200 para Arequipa con 5% descuento",
        "approval_status": "PENDING",
        "trace_logs": [],
        "errors": []
    }
    
    config = {"configurable": {"thread_id": "thread-2"}}
    
    # 1. Ejecución inicial -> Debe pausar en interrupt()
    state_before_interrupt = await app.ainvoke(initial_state, config=config)
    
    # Obtener el estado del thread pausado
    snapshot = await app.aget_state(config)
    assert len(snapshot.next) > 0
    assert snapshot.next[0] == "human_approval_node"
    
    # 2. Reanudar enviando la aprobación del usuario
    resume_command = Command(resume={"action": "APPROVED", "comment": "Aprobado por Gerencia"})
    final_state = await app.ainvoke(resume_command, config=config)
    
    assert final_state["approval_status"] == "APPROVED"
    assert final_state["human_comment"] == "Aprobado por Gerencia"
    assert final_state["validation_status"].value == "READY"