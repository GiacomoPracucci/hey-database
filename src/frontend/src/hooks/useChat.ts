import { useState, useEffect, useCallback } from "react";
import { v4 as uuidv4 } from "uuid"; // Dovrai installare uuid con npm
import { Message } from "../components/chat/types";
import { FeedbackRequest } from "../types";
import ChatService from "../services/chat";

const STORAGE_KEY = "chat_messages";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  sendFeedback: (feedback: FeedbackRequest) => Promise<void>;
  clearMessages: () => void;
}

const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carica i messaggi dal localStorage all'avvio
  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEY);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error("Error loading saved messages:", e);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  // Salva i messaggi nel localStorage quando cambiano
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  // Invia un messaggio
  const sendMessage = useCallback(async (content: string) => {
    setError(null);
    setIsLoading(true);

    // Aggiungi immediatamente il messaggio dell'utente
    const userMessage: Message = {
      id: uuidv4(),
      type: "user",
      content,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      // Invia il messaggio all'API
      const response = await ChatService.sendMessage(content);

      // Crea il messaggio del bot
      const botMessage: Message = {
        id: uuidv4(),
        type: "bot",
        content: "",
        timestamp: Date.now(),
        query: response.query,
        explanation: response.explanation,
        results: response.results,
        error: response.error,
        originalQuestion: response.original_question,
        fromVectorStore: response.from_vector_store,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An unknown error occurred";

      // Crea il messaggio di errore del bot
      const botErrorMessage: Message = {
        id: uuidv4(),
        type: "bot",
        content: "",
        timestamp: Date.now(),
        error: errorMessage,
      };

      setMessages((prev) => [...prev, botErrorMessage]);
      setError(errorMessage); // Ora passiamo direttamente la stringa
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Invia feedback positivo
  const sendFeedback = useCallback(async (feedback: FeedbackRequest) => {
    try {
      await ChatService.sendFeedback(feedback);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error sending feedback");
    }
  }, []);

  // Pulisce la chat
  const clearMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    sendFeedback,
    clearMessages,
  };
};

export default useChat;
