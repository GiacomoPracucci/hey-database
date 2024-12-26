/**
 * ChatService
 *
 * Gestisce la logica di business per la funzionalità di chat.
 * Si occupa di:
 * - Processare i messaggi
 * - Gestire il feedback
 * - Gestire lo storage locale dei messaggi
 */
import { apiService } from "./api-service.js";

class ChatService {
  constructor() {
    this.STORAGE_KEY = "chat_messages";
    this.endpoints = {
      chat: "/chat/api/chat",
      feedback: "/chat/api/feedback",
    };
  }

  /**
   * Processa un messaggio utente
   * @param {string} message
   * @returns {Promise} Promise con la risposta elaborata
   */
  async processMessage(message) {
    const response = await apiService.post(this.endpoints.chat, { message });

    if (response.success) {
      this.saveMessageToStorage({
        type: "user",
        content: message,
      });

      this.saveMessageToStorage({
        type: "bot",
        content: response,
      });
    }

    return response;
  }

  /**
   * Gestisce il feedback positivo
   * @param {Object} data
   * @returns {Promise}
   */
  async handleFeedback(data) {
    return apiService.post(this.endpoints.feedback, data);
  }

  /**
   * Salva un messaggio nel localStorage
   * @param {Object} message
   */
  saveMessageToStorage(message) {
    const messages = this.getMessagesFromStorage();
    messages.push(message);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(messages));
  }

  /**
   * Recupera i messaggi dal localStorage
   * @returns {Array}
   */
  getMessagesFromStorage() {
    try {
      const messages = localStorage.getItem(this.STORAGE_KEY);
      return messages ? JSON.parse(messages) : [];
    } catch (error) {
      console.error("Error reading from storage:", error);
      return [];
    }
  }

  /**
   * Pulisce la cronologia dei messaggi
   */
  clearMessages() {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}

// Esporta un'istanza singola del servizio
export const chatService = new ChatService();
