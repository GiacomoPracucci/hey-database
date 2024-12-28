import { STORAGE } from "../config/constants.js";

/**
 * ChatStorage gestisce la persistenza dei dati della chat nel localStorage.
 * Fornisce metodi per salvare, recuperare e gestire la cronologia dei messaggi.
 */
export class ChatStorage {
  /**
   * Inizializza il servizio di storage
   * @throws {Error} Se localStorage non è disponibile
   */
  constructor() {
    // Verifica che localStorage sia disponibile
    if (!this.isStorageAvailable()) {
      throw new Error("LocalStorage non è disponibile in questo browser");
    }
  }

  /**
   * Verifica la disponibilità del localStorage
   * @returns {boolean} true se localStorage è disponibile, false altrimenti
   */
  isStorageAvailable() {
    try {
      const storage = window.localStorage;
      const test = "__storage_test__";
      storage.setItem(test, test);
      storage.removeItem(test);
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * Salva i messaggi nel localStorage
   * @param {Array} messages Array di messaggi da salvare
   * @throws {Error} Se la serializzazione fallisce
   */
  saveMessages(messages) {
    try {
      const processedMessages = messages
        .filter(
          (msg) =>
            !msg.classList.contains("welcome") &&
            !msg.classList.contains("typing-indicator-container")
        )
        .map((msg) => this.processMessageForStorage(msg));

      localStorage.setItem(
        STORAGE.CHAT_MESSAGES,
        JSON.stringify(processedMessages)
      );
    } catch (error) {
      console.error("Errore nel salvataggio dei messaggi:", error);
      throw new Error("Impossibile salvare i messaggi nel localStorage");
    }
  }

  /**
   * Processa un singolo messaggio per il salvataggio
   * @param {HTMLElement} msg Elemento DOM del messaggio
   * @returns {Object} Oggetto messaggio processato pronto per il salvataggio
   * @private
   */
  processMessageForStorage(msg) {
    const isUser = msg.classList.contains("user");
    const content = msg.querySelector(".message-content");

    if (isUser) {
      return {
        type: "user",
        content: content.textContent,
      };
    }

    const errorContainer = content.querySelector(".error-container");
    if (errorContainer) {
      return {
        type: "bot",
        isError: true,
        error: content.querySelector(".error-details").textContent,
        query: content.querySelector(".error-query code")?.textContent || null,
      };
    }

    const queryContainer = content.querySelector(".sql-query-container");
    return {
      type: "bot",
      isError: false,
      query:
        queryContainer?.querySelector(".sql-query code")?.textContent || null,
      explanation: content.querySelector(".explanation")?.textContent || null,
      originalQuestion: queryContainer?.dataset.originalQuestion || null,
      results: this.extractTableData(content.querySelector(".results-table")),
    };
  }

  /**
   * Estrae i dati da una tabella HTML
   * @param {HTMLElement} table Elemento tabella da processare
   * @returns {Array|null} Array di oggetti rappresentanti le righe della tabella, o null se la tabella non esiste
   * @private
   */
  extractTableData(table) {
    if (!table) return null;

    const results = [];
    const headers = Array.from(table.querySelectorAll("thead th")).map(
      (th) => th.textContent
    );

    table.querySelectorAll("tbody tr").forEach((tr) => {
      const row = {};
      Array.from(tr.children).forEach((td, index) => {
        row[headers[index]] = td.textContent;
      });
      results.push(row);
    });

    return results;
  }

  /**
   * Recupera i messaggi dal localStorage
   * @returns {Array} Array di messaggi recuperati
   * @throws {Error} Se il recupero o il parsing fallisce
   */
  loadMessages() {
    try {
      const savedMessages = localStorage.getItem(STORAGE.CHAT_MESSAGES);
      return savedMessages ? JSON.parse(savedMessages) : [];
    } catch (error) {
      console.error("Errore nel caricamento dei messaggi:", error);
      // In caso di errore, cancelliamo lo storage corrotto e restituiamo un array vuoto
      this.clearMessages();
      return [];
    }
  }

  /**
   * Cancella tutti i messaggi dal localStorage
   * @returns {boolean} true se l'operazione è riuscita, false altrimenti
   */
  clearMessages() {
    try {
      localStorage.removeItem(STORAGE.CHAT_MESSAGES);
      return true;
    } catch (error) {
      console.error("Errore nella pulizia dei messaggi:", error);
      return false;
    }
  }

  /**
   * Verifica se ci sono messaggi salvati
   * @returns {boolean} true se ci sono messaggi salvati, false altrimenti
   */
  hasMessages() {
    return !!localStorage.getItem(STORAGE.CHAT_MESSAGES);
  }

  /**
   * Conta il numero di messaggi salvati
   * @returns {number} Numero di messaggi salvati
   */
  getMessageCount() {
    try {
      const messages = this.loadMessages();
      return messages.length;
    } catch {
      return 0;
    }
  }

  /**
   * Salva le impostazioni della chat
   * @param {Object} settings Oggetto contenente le impostazioni da salvare
   */
  saveSettings(settings) {
    try {
      localStorage.setItem(STORAGE.SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error("Errore nel salvataggio delle impostazioni:", error);
    }
  }

  /**
   * Recupera le impostazioni della chat
   * @returns {Object|null} Oggetto impostazioni o null se non presenti
   */
  loadSettings() {
    try {
      const settings = localStorage.getItem(STORAGE.SETTINGS);
      return settings ? JSON.parse(settings) : null;
    } catch (error) {
      console.error("Errore nel caricamento delle impostazioni:", error);
      return null;
    }
  }
}
