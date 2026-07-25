import os
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.agent.prompts import EXTRACTION_SYSTEM_PROMPT
from app.agent.state import QuoteState
from app.domain.models import ExtractedQuoteRequest, RequestedItem, ValidationStatus
from app.domain.services import calculate_quote_draft
from langgraph.types import interrupt


def get_llm():
    """Retorna el cliente LLM configurado o una versión Mock para pruebas sin credenciales."""
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    
    if use_mock:
        return None
        
    api_key_openai = os.getenv("OPENAI_API_KEY")
    if api_key_openai and api_key_openai.startswith("sk-"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
    api_key_anthropic = os.getenv("ANTHROPIC_API_KEY")
    if api_key_anthropic and api_key_anthropic.startswith("sk-"):
        return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
        
    return None


async def extract_intent_node(state: QuoteState) -> Dict[str, Any]:
    """Nodo 1: Extrae datos estructurados desde el texto libre usando LLM."""
    logs = list(state.get("trace_logs", []))
    logs.append("Nodo 'extract_intent_node': Iniciando extracción de entidades.")
    
    llm = get_llm()
    
    if llm is None:
        # Fallback Mock Inteligente con Regex para Pruebas Locales
        import re
        raw_text = state["raw_text"].lower()
        requested_items = []
        
        # Extraer cantidad dinámica junto a HX-200 o cascos
        qty_match = re.search(r'(\d+)\s*(cascos|hx-200|botas|tx-500)', raw_text)
        qty = int(qty_match.group(1)) if qty_match else 20
        
        if "hx-200" in raw_text or "cascos" in raw_text:
            requested_items.append(RequestedItem(sku="HX-200", quantity=qty))
        elif "tx-500" in raw_text or "botas" in raw_text:
            requested_items.append(RequestedItem(sku="TX-500", quantity=qty))
            
        # Extraer porcentaje de descuento dinámico (ej. 1% o 8%)
        discount_match = re.search(r'(\d+)%\s*de\s*descuento', raw_text)
        discount = float(discount_match.group(1)) if discount_match else 0.0
        
        customer = state.get("customer_id") or "CUST-GOLD-01"
        
        extracted = ExtractedQuoteRequest(
            customer_id=customer,
            items=requested_items,
            location="Arequipa" if "arequipa" in raw_text else "Lima",
            requested_discount_pct=discount
        )
    else:
        # Invocación real a LLM con Output Estructurado Pydantic
        structured_llm = llm.with_structured_output(ExtractedQuoteRequest)
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Cliente ID: {state.get('customer_id', '')}\nTexto Solicitud: {state['raw_text']}"}
        ]
        extracted = await structured_llm.ainvoke(messages)
        if not extracted.customer_id and state.get("customer_id"):
            extracted.customer_id = state["customer_id"]

    logs.append(f"Nodo 'extract_intent_node': Datos extraídos exitosamente. SKUs: {[i.sku for i in extracted.items]}")
    return {
        "extracted_data": extracted,
        "trace_logs": logs
    }


async def validate_domain_node(state: QuoteState) -> Dict[str, Any]:
    """Nodo 2: Invocación determinista al motor de negocio (Sin LLM)."""
    logs = list(state.get("trace_logs", []))
    logs.append("Nodo 'validate_domain_node': Ejecutando reglas deterministas de negocio.")
    
    extracted = state.get("extracted_data")
    if not extracted:
        return {
            "validation_status": ValidationStatus.NEED_CLARIFICATION,
            "errors": ["No se obtuvieron datos extraídos válidos."],
            "trace_logs": logs
        }
        
    status, draft, reasons = calculate_quote_draft(extracted)
    
    logs.append(f"Nodo 'validate_domain_node': Resultado determinista -> {status.value}")
    
    return {
        "validation_status": status,
        "quote_draft": draft,
        "validation_reasons": reasons,
        "requires_approval": (status == ValidationStatus.REQUIRES_APPROVAL),
        "trace_logs": logs
    }


async def human_approval_node(state: QuoteState) -> Dict[str, Any]:
    """
    Nodo 3: Pausa la ejecución usando interrupt() para aprobación humana (HITL).
    Guarda el estado persistente en Postgres.
    """
    logs = list(state.get("trace_logs", []))
    logs.append("Nodo 'human_approval_node': PAUSANDO GRAFO. Esperando decisión humana (HITL).")
    
    draft = state.get("quote_draft")
    reasons = state.get("validation_reasons", [])
    
    # Dispara la interrupción del grafo guardando el payload de inspección
    human_response = interrupt({
        "action_required": "REVIEW_QUOTE_APPROVAL",
        "customer_id": state.get("customer_id"),
        "total_usd": draft.total_usd if draft else 0.0,
        "reasons": reasons,
        "message": "La cotización requiere revisión por monto elevado o excepción de descuento."
    })
    
    # Al reanudar (resume), el valor retornado por interrupt() se asigna a human_response
    action = human_response.get("action", "REJECTED")
    comment = human_response.get("comment", "")
    
    logs.append(f"Nodo 'human_approval_node': REANUDADO por usuario -> Acción: {action}, Comentario: {comment}")
    
    return {
        "approval_status": action,
        "human_comment": comment,
        "trace_logs": logs
    }


async def finalize_quote_node(state: QuoteState) -> Dict[str, Any]:
    """Nodo 4: Emite el borrador final o el estado de cierre."""
    logs = list(state.get("trace_logs", []))
    approval = state.get("approval_status", "APPROVED")
    
    if approval == "REJECTED":
        logs.append("Nodo 'finalize_quote_node': Cotización RECHAZADA por el ejecutivo.")
        status = ValidationStatus.NEED_CLARIFICATION
    else:
        logs.append("Nodo 'finalize_quote_node': Cotización FINALIZADA exitosamente en estado listo.")
        status = ValidationStatus.READY
        
    return {
        "validation_status": status,
        "trace_logs": logs
    }