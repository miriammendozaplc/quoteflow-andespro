"use client";
// Componente de inspección, visualización del borrador, trazabilidad de auditoría y panel Human-in-the-Loop (HITL):
import { useState } from "react";
import { QuoteResponse } from "../types";

interface Props {
  data: QuoteResponse;
  onRefresh: (threadId: string) => void;
}

export function QuoteInspector({ data, onRefresh }: Props) {
  const [comment, setComment] = useState("");
  const [resuming, setResuming] = useState(false);

  const handleResume = async (action: "APPROVED" | "REJECTED") => {
    setResuming(true);
    try {
      await fetch(`http://localhost:8000/api/quotes/${data.thread_id}/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, comment }),
      });
      onRefresh(data.thread_id);
    } catch (err) {
      alert("Error al reanudar la cotización.");
    } finally {
      setResuming(false);
    }
  };

  const draft = data.state.quote_draft;

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            Cotización ID: {data.state.request_id || "N/A"}
          </h3>
          <p className="text-sm text-gray-500">Thread ID (LangGraph): {data.thread_id}</p>
        </div>
        <div>
          {data.is_paused ? (
            <span className="px-3 py-1 bg-amber-100 text-amber-800 font-semibold text-xs rounded-full animate-pulse">
              PAUSADA (Aprobación Requerida)
            </span>
          ) : (
            <span className="px-3 py-1 bg-green-100 text-green-800 font-semibold text-xs rounded-full">
              {data.state.validation_status || "PROCESADO"}
            </span>
          )}
        </div>
      </div>

      {/* Panel HITL de Aprobación si está Pausado */}
      {data.is_paused && (
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg">
          <h4 className="font-bold text-amber-900 mb-2">Aprobación Humana Requerida (Human-In-The-Loop)</h4>
          <ul className="list-disc ml-5 text-sm text-amber-800 mb-4">
            {data.state.validation_reasons?.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Agregar observación o motivo (opcional)..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full p-2 border rounded text-sm"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => handleResume("APPROVED")}
                disabled={resuming}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded text-sm transition-all"
              >
                Aprobar Cotización
              </button>
              <button
                onClick={() => handleResume("REJECTED")}
                disabled={resuming}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded text-sm transition-all"
              >
                Rechazar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detalle del Borrador Calculado */}
      {draft && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Borrador de Cotización Generado</h4>
          <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
            <p><strong>Cliente:</strong> {draft.customer_name} ({draft.customer_tier})</p>
            <p><strong>Subtotal:</strong> ${draft.subtotal.toLocaleString()} USD</p>
            <p><strong>Descuento ({draft.discount_pct}%):</strong> -${draft.discount_amount.toLocaleString()} USD</p>
            <p className="text-base font-bold text-blue-900"><strong>Total Final:</strong> ${draft.total_usd.toLocaleString()} USD</p>
          </div>
        </div>
      )}

      {/* Auditoría y Trace Logs de LangGraph */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-2">Trazabilidad del Grafo Agéntico (Logs)</h4>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg text-xs font-mono max-h-48 overflow-y-auto space-y-1">
          {data.state.trace_logs?.map((log, i) => (
            <div key={i}>&gt; {log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}