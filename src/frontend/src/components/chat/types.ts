import { ChatMessage, ChatResponse } from "../../types";

export type MessageType = "user" | "bot";

// indipendentemente dal tipo abbiamo per ogni messaggio un id e un timestamp
export interface BaseMessage {
  id: string;
  timestamp: number;
}

// se è un user message semplicemente abbiamo il contenuto del messaggio
export interface UserMessage extends BaseMessage {
  type: "user";
  content: ChatMessage["message"];
}

// se è una risposta del bot abbiamo tutto ciò che espone l'API
export interface BotMessage extends BaseMessage {
  type: "bot";
  content: string;
  query?: ChatResponse["query"];
  explanation?: ChatResponse["explanation"];
  results?: ChatResponse["results"];
  error?: string;
  originalQuestion?: ChatResponse["original_question"];
  fromVectorStore?: ChatResponse["from_vector_store"];
}

export type Message = UserMessage | BotMessage;
