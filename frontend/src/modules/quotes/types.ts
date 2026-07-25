export interface CalculatedItem {
  sku: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface QuoteDraft {
  customer_id: string;
  customer_name: string;
  customer_tier: string;
  items: CalculatedItem[];
  subtotal: number;
  discount_pct: number;
  discount_amount: number;
  total_usd: number;
  requires_approval: boolean;
  approval_reasons: string[];
}

export interface QuoteResponse {
  thread_id: string;
  is_paused: boolean;
  state: {
    request_id: string;
    customer_id: string;
    raw_text: string;
    validation_status?: string;
    quote_draft?: QuoteDraft;
    validation_reasons?: string[];
    approval_status?: string;
    human_comment?: string;
    trace_logs?: string[];
  };
}