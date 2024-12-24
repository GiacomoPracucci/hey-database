import { useState, useEffect, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
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
  const [messages, setMessages] = useState<Message[]>(() => {
    // Inizializza lo stato dai dati salvati
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Error loading saved messages:", e);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    return [];
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Salva i messaggi nel localStorage quando cambiano
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  const sendMessage = useCallback(async (content: string) => {
    setError(null);
    setIsLoading(true);

    const userMessage: Message = {
      id: uuidv4(),
      type: "user",
      content,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await ChatService.sendMessage(content);

      const botMessage: Message = {
        id: uuidv4(),
        type: "bot",
        content: "",
        timestamp: Date.now(),
        query: response.query,
        explanation: response.explanation,
        results: response.results,
        originalQuestion: response.original_question,
        fromVectorStore: response.from_vector_store,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An unknown error occurred";
      setError(errorMessage);

      const errorBotMessage: Message = {
        id: uuidv4(),
        type: "bot",
        content: "",
        timestamp: Date.now(),
        error: errorMessage,
      };

      setMessages((prev) => [...prev, errorBotMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendFeedback = useCallback(async (feedback: FeedbackRequest) => {
    try {
      await ChatService.sendFeedback(feedback);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An unknown error occurred";
      setError(errorMessage);
    }
  }, []);

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
