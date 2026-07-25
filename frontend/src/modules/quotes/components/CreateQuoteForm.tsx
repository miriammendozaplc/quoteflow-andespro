"use client";
// Componente para ingresar solicitudes en lenguaje natural:
import { useState } from "react";

interface Props {
  onQuoteCreated: (data: any) => void;
}

export function CreateQuoteForm({ onQuoteCreated }: Props) {
  const [customerId, setCustomerId] = useState("CUST-GOLD-01");
  const [rawText, setRawText] = useState(
    "Necesito 20 cascos HX-200 para la planta de Arequipa. Requiero 8% de descuento."
  );
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/quotes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId, raw_text: rawText }),
      });
      const data = await res.json();
      onQuoteCreated(data);
    } catch (err) {
      alert("Error al conectar con el servidor de FastAPI.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Nueva Solicitud de Cotización (AndesPro)</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ID Cliente</label>
          <select
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="w-full p-2 border rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500"
          >
            <option value="CUST-GOLD-01">CUST-GOLD-01 (Corp. Minera del Sur - Gold)</option>
            <option value="CUST-SILVER-01">CUST-SILVER-01 (Constructora Arequipa - Silver)</option>
            <option value="CUST-STD-01">CUST-STD-01 (Talleres Lima - Standard)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Solicitud en Lenguaje Natural</label>
          <textarea
            rows={3}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Ejemplo: Necesito 250 cascos HX-200 y 5% descuento..."
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-all disabled:opacity-50"
        >
          {loading ? "Procesando Grafo Agéntico..." : "Procesar Cotización con LangGraph"}
        </button>
      </form>
    </div>
  );
}