"use client";

import { useState } from "react";
import { CreateQuoteForm } from "@/modules/quotes/components/CreateQuoteForm";
import { QuoteInspector } from "@/modules/quotes/components/QuoteInspector";
import { QuoteResponse } from "@/modules/quotes/types";

export default function Home() {
  const [activeQuote, setActiveQuote] = useState<QuoteResponse | null>(null);

  const refreshQuoteState = async (threadId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/quotes/${threadId}`);
      const data = await res.json();
      setActiveQuote(data);
    } catch (err) {
      console.error("Error al refrescar estado", err);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">QuoteFlow System</h1>
          <p className="text-gray-600 mt-2">
            Automatización Agéntica de Cotizaciones B2B con LangGraph & Human-in-the-Loop
          </p>
        </header>

        <CreateQuoteForm onQuoteCreated={setActiveQuote} />

        {activeQuote && (
          <QuoteInspector data={activeQuote} onRefresh={refreshQuoteState} />
        )}
      </div>
    </main>
  );
}