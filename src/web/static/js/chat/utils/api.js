import { API, ERROR_MESSAGES } from "../config/constants.js";

/**
 * ChatApiService gestisce tutte le interazioni con le API del backend per la chat.
 * Fornisce metodi per inviare messaggi e gestire le risposte del server.
 */
export class ChatApiService {
  /**
   * Invia un messaggio al server e gestisce la risposta
   * @param {string} message - Il messaggio da inviare
   * @returns {Promise<Object>} La risposta elaborata dal server
   * @throws {Error} Se la richiesta fallisce
   *
   * Formato risposta atteso:
   * {
   *   success: boolean,
   *   query?: string,              // La query SQL generata
   *   explanation?: string,        // Spiegazione in linguaggio naturale
   *   results?: Array,            // Risultati dell'esecuzione
   *   preview?: Array,            // Dati di preview opzionali
   *   original_question?: string,  // La domanda originale
   *   from_vector_store?: boolean, // Se la risposta proviene dalla cache
   *   error?: string              // Presente solo se success è false
   * }
   */
  async sendMessage(message) {
    try {
      const response = await fetch(API.CHAT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();

      // Se la risposta viene dalla cache, simuliamo un delay
      // per una migliore esperienza utente
      if (data.from_vector_store) {
        await this.simulateTypingDelay();
      }

      return data;
    } catch (error) {
      console.error("Error in chat API:", error);
      throw new Error(ERROR_MESSAGES.COMMUNICATION);
    }
  }

  /**
   * Invia feedback positivo per una risposta
   * @param {Object} feedbackData - I dati del feedback
   * @param {string} feedbackData.question - La domanda originale
   * @param {string} feedbackData.sql_query - La query SQL generata
   * @param {string} feedbackData.explanation - La spiegazione fornita
   * @returns {Promise<Object>} Risposta del server
   * @throws {Error} Se l'invio del feedback fallisce
   */
  async sendFeedback(feedbackData) {
    try {
      // Validazione dei dati di input
      this.validateFeedbackData(feedbackData);

      const response = await fetch(API.FEEDBACK, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(feedbackData),
      });

      const data = await response.json();

      if (!response.ok) {
        // Gestione specifica degli errori noti
        if (data.error === "vector_store_disabled") {
          throw new Error(ERROR_MESSAGES.VECTOR_STORE);
        }
        throw new Error(data.error || ERROR_MESSAGES.GENERIC);
      }

      return data;
    } catch (error) {
      console.error("Error sending feedback:", error);
      throw error; // Rilanciamo l'errore per gestirlo nel chiamante
    }
  }

  /**
   * Valida i dati del feedback prima dell'invio
   * @param {Object} data - I dati da validare
   * @throws {Error} Se i dati non sono validi
   * @private
   */
  validateFeedbackData(data) {
    const requiredFields = ["question", "sql_query", "explanation"];
    const missingFields = requiredFields.filter((field) => !data[field]);

    if (missingFields.length > 0) {
      throw new Error(
        `${ERROR_MESSAGES.MISSING_DATA}: ${missingFields.join(", ")}`
      );
    }
  }

  /**
   * Simula un delay di digitazione per le risposte dalla cache
   * @returns {Promise<void>}
   * @private
   */
  simulateTypingDelay() {
    return new Promise((resolve) => setTimeout(resolve, 1500));
  }

  /**
   * Verifica se una risposta contiene un errore
   * @param {Object} response - La risposta da verificare
   * @returns {boolean} true se la risposta contiene un errore
   * @static
   */
  static hasError(response) {
    return !response.success;
  }

  /**
   * Estrae il messaggio di errore da una risposta
   * @param {Object} response - La risposta da cui estrarre l'errore
   * @returns {string} Il messaggio di errore
   * @static
   */
  static getErrorMessage(response) {
    return response.error || ERROR_MESSAGES.GENERIC;
  }

  /**
   * Verifica se una risposta proviene dalla cache
   * @param {Object} response - La risposta da verificare
   * @returns {boolean} true se la risposta proviene dalla cache
   * @static
   */
  static isFromCache(response) {
    return !!response.from_vector_store;
  }

  /**
   * Formatta una risposta di errore
   * @param {string|Error} error - L'errore da formattare
   * @returns {Object} Risposta di errore formattata
   * @static
   */
  static formatErrorResponse(error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : error,
    };
  }
}

// Creiamo un'istanza singola del servizio per l'applicazione
export const chatApiService = new ChatApiService();
