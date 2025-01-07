import { API, ERROR_MESSAGES } from "../../config/constants.js";
import { chatNotificationService } from "../../utils/chatNotifications.js";

/**
 * FeedbackApiService gestisce tutte le interazioni API relative al feedback.
 * Fornisce metodi per inviare e gestire i feedback degli utenti.
 */
export class FeedbackApiService {
  /**
   * Invia un feedback positivo al server
   * @param {Object} feedbackData - Dati del feedback
   * @param {string} feedbackData.question - Domanda originale
   * @param {string} feedbackData.sql_query - Query SQL generata
   * @param {string} feedbackData.explanation - Spiegazione fornita
   * @returns {Promise<Object>} Risposta dal server
   * @throws {Error} Se l'invio del feedback fallisce
   */
  async submitFeedback(feedbackData) {
    try {
      // Valida i dati prima dell'invio
      this.validateFeedbackData(feedbackData);
      console.log('Sending feedback data:', feedbackData);

      const response = await fetch(API.FEEDBACK, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(feedbackData),
      });

      const data = await response.json();

      // Gestione specifica degli errori noti
      if (!response.ok) {
        if (data.error === "vector_store_disabled") {
          throw new Error(ERROR_MESSAGES.VECTOR_STORE);
        }
        throw new Error(data.error || ERROR_MESSAGES.GENERIC);
      }
      console.log('Response from server:', data);
      return data;
    } catch (error) {
      console.error("Error submitting feedback:", error);

      // Rilancia l'errore per gestirlo nel chiamante
      throw this.formatError(error);
    }
  }

  /**
   * Valida i dati del feedback prima dell'invio
   * @param {Object} data - Dati da validare
   * @throws {Error} Se i dati non sono validi
   * @private
   */
  validateFeedbackData(data) {
    // Verifica la presenza di tutti i campi richiesti
    const requiredFields = ["question", "sql_query", "explanation"];
    const missingFields = requiredFields.filter((field) => !data[field]);

    if (missingFields.length > 0) {
      throw new Error(
        `${ERROR_MESSAGES.MISSING_DATA}: ${missingFields.join(", ")}`
      );
    }

    // Verifica che i campi non siano vuoti
    for (const field of requiredFields) {
      if (typeof data[field] !== "string" || !data[field].trim()) {
        throw new Error(`${field} cannot be empty`);
      }
    }
  }

  /**
   * Formatta un errore per l'output
   * @param {Error|string} error - Errore da formattare
   * @returns {Error} Errore formattato
   * @private
   */
  formatError(error) {
    if (error instanceof Error) {
      return error;
    }
    return new Error(
      typeof error === "string" ? error : ERROR_MESSAGES.GENERIC
    );
  }

  /**
   * Verifica se una risposta contiene un errore
   * @param {Object} response - Risposta da verificare
   * @returns {boolean} true se la risposta contiene un errore
   * @static
   */
  static hasError(response) {
    return !response.success;
  }

  /**
   * Estrae il messaggio di errore da una risposta
   * @param {Object} response - Risposta da cui estrarre l'errore
   * @returns {string} Il messaggio di errore
   * @static
   */
  static getErrorMessage(response) {
    return response.error || ERROR_MESSAGES.GENERIC;
  }

  /**
   * Verifica se un errore è dovuto al vector store disabilitato
   * @param {Error} error - Errore da verificare
   * @returns {boolean} true se l'errore è relativo al vector store
   * @static
   */
  static isVectorStoreError(error) {
    return error.message === ERROR_MESSAGES.VECTOR_STORE;
  }

  /**
   * Invia feedback positivo e gestisce notifiche
   * @param {Object} feedbackData - Dati del feedback
   * @returns {Promise<boolean>} true se l'invio è riuscito
   */
  async sendFeedbackWithNotification(feedbackData) {
    try {
        const response = await this.submitFeedback(feedbackData);
        if (response.success) {  // Verifica che la risposta sia avvenuta con successo
            chatNotificationService.showSuccess("Thank you for your feedback!");
            return true;
        } else {
            chatNotificationService.showError(response.error || ERROR_MESSAGES.GENERIC);
            return false;
        }
    } catch (error) {
        if (FeedbackApiService.isVectorStoreError(error)) {
            chatNotificationService.showWarning(error.message);
        } else {
            chatNotificationService.showError(error.message);
        }
        return false;
    }
  }

  /**
   * Crea un oggetto feedback dai dati grezzi
   * @param {string} question - Domanda originale
   * @param {string} sqlQuery - Query SQL
   * @param {string} explanation - Spiegazione
   * @returns {Object} Oggetto feedback formattato
   * @static
   */
  static createFeedbackData(question, sqlQuery, explanation) {
    return {
      question: question?.trim(),
      sql_query: sqlQuery?.trim(),
      explanation: explanation?.trim(),
    };
  }
}

// Creiamo un'istanza singola del servizio per l'applicazione
export const feedbackApiService = new FeedbackApiService();
