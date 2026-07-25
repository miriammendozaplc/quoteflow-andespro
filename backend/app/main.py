import os
import uuid
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.graph import get_compiled_graph
from langgraph.types import Command

load_dotenv()

app = FastAPI(
    title="QuoteFlow API - AndesPro Industrial",
    version="1.0.0",
    description="API REST para orquestación de cotizaciones con LangGraph y Human-in-the-Loop"
)

# Configuración de CORS para Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateQuoteRequest(BaseModel):
    customer_id: str
    raw_text: str


class ResumeQuoteRequest(BaseModel):
    action: str  # "APPROVED" o "REJECTED"
    comment: Optional[str] = ""


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "QuoteFlow Engine"}


@app.post("/api/quotes")
async def create_quote(payload: CreateQuoteRequest):
    """Inicia la ejecución del grafo de LangGraph para una nueva cotización."""
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"
    graph = await get_compiled_graph()
    
    initial_state = {
        "request_id": f"REQ-{uuid.uuid4().hex[:6].upper()}",
        "customer_id": payload.customer_id,
        "raw_text": payload.raw_text,
        "approval_status": "PENDING",
        "trace_logs": [],
        "errors": []
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Iniciar la ejecución asíncrona del grafo
    final_state = await graph.ainvoke(initial_state, config=config)
    
    # Inspeccionar si el grafo fue pausado en interrupt()
    state_snapshot = await graph.aget_state(config)
    is_paused = len(state_snapshot.next) > 0 and state_snapshot.next[0] == "human_approval_node"
    
    return {
        "thread_id": thread_id,
        "is_paused": is_paused,
        "state": final_state
    }


@app.get("/api/quotes/{thread_id}")
async def get_quote_state(thread_id: str):
    """Obtiene el estado actual y trazabilidad de un thread."""
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    state_snapshot = await graph.aget_state(config)
    if not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
        
    is_paused = len(state_snapshot.next) > 0 and state_snapshot.next[0] == "human_approval_node"
    
    return {
        "thread_id": thread_id,
        "is_paused": is_paused,
        "next_node": state_snapshot.next[0] if state_snapshot.next else None,
        "state": state_snapshot.values
    }


@app.post("/api/quotes/{thread_id}/resume")
async def resume_quote(thread_id: str, payload: ResumeQuoteRequest):
    """Reanuda la ejecución del grafo pausado en human_approval_node enviando el comando de decisión."""
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    state_snapshot = await graph.aget_state(config)
    if not state_snapshot.next or state_snapshot.next[0] != "human_approval_node":
        raise HTTPException(status_code=400, detail="La cotización no está pausada en espera de aprobación.")
        
    resume_command = Command(resume={"action": payload.action, "comment": payload.comment})
    final_state = await graph.ainvoke(resume_command, config=config)
    
    return {
        "thread_id": thread_id,
        "status": "RESUMED",
        "state": final_state
    }