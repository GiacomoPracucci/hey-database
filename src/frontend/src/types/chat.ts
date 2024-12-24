import { ApiResponse } from "./api";

// messaggio inviato dall'utente
export interface ChatMessage {
  message: string;
}

// risposta dell'agente SQL
export interface ChatResponse extends ApiResponse {
  query?: string;
  explanation?: string;
  results?: any[];
  preview?: any[];
  original_question?: string;
  from_vector_store?: boolean;
}

// feedback di risposta corretta
export interface FeedbackRequest {
  question: string;
  sql_query: string;
  explanation: string;
}

export interface FeedbackResponse extends ApiResponse {}
