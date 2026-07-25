from typing import List, Optional, TypedDict
from app.domain.models import ExtractedQuoteRequest, QuoteDraft, ValidationStatus


class QuoteState(TypedDict):
    """
    Estado explícito que fluye a través de los nodos de LangGraph.
    """
    request_id: str
    customer_id: str
    raw_text: str
    
    # Datos extraídos por el LLM
    extracted_data: Optional[ExtractedQuoteRequest]
    
    # Resultado de la validación determinista
    validation_status: Optional[ValidationStatus]
    quote_draft: Optional[QuoteDraft]
    validation_reasons: List[str]
    
    # Control de Human-in-the-Loop (HITL)
    requires_approval: bool
    approval_status: str  # "PENDING", "APPROVED", "REJECTED"
    human_comment: Optional[str]
    
    # Trazabilidad y auditoría
    trace_logs: List[str]
    errors: List[str]