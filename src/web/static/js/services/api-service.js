/**
 * ApiService
 *
 * Servizio base per gestire tutte le chiamate API.
 * Fornisce metodi di utilità per le chiamate HTTP e gestione degli errori.
 */
class ApiService {
  /**
   * Effettua una richiesta HTTP
   * @param {string} endpoint - L'endpoint da chiamare
   * @param {Object} options - Opzioni della richiesta
   * @returns {Promise} Promise con la risposta
   */
  async request(endpoint, options = {}) {
    try {
      const defaultOptions = {
        headers: {
          "Content-Type": "application/json",
        },
      };

      const response = await fetch(endpoint, { ...defaultOptions, ...options });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Si è verificato un errore");
      }

      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  /**
   * Effettua una richiesta GET
   * @param {string} endpoint
   * @returns {Promise}
   */
  get(endpoint) {
    return this.request(endpoint);
  }

  /**
   * Effettua una richiesta POST
   * @param {string} endpoint
   * @param {Object} data
   * @returns {Promise}
   */
  post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

// Esporta un'istanza singola del servizio
export const apiService = new ApiService();
