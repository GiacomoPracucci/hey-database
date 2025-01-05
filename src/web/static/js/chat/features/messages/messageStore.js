import { ChatStorage } from "../../utils/chatStorage.js";
import {
  MessageFactory,
  MessageType,
  MessageValidator,
} from "./messageTypes.js";
import { chatNotificationService } from "../../utils/chatNotifications.js";

/**
 * MessageStore gestisce lo stato e la persistenza dei messaggi della chat.
 * Mantiene la lista dei messaggi in memoria e gestisce la sincronizzazione con il localStorage.
 */
export class MessageStore {
  /**
   * Inizializza lo store dei messaggi
   */
  constructor() {
    // Array interno dei messaggi
    this.messages = [];

    // Inizializza il servizio di storage
    this.storage = new ChatStorage();

    // Lista degli observer per il pattern pub/sub
    this.observers = new Set();

    // Carica i messaggi salvati
    this.loadMessages();
  }

  /**
   * Carica i messaggi dal localStorage
   * @private
   */
  loadMessages() {
    try {
      const savedMessages = this.storage.loadMessages();
      // Converte i messaggi salvati in istanze appropriate
      this.messages = savedMessages.map((msg) =>
        MessageFactory.fromSerialized(msg)
      );
      this.notifyObservers();
    } catch (error) {
      console.error("Error loading messages:", error);
      chatNotificationService.showError("Error loading chat history");
    }
  }

  /**
   * Salva i messaggi nel localStorage
   * @private
   */
  saveMessages() {
    try {
      // Serializza i messaggi prima del salvataggio
      const serializedMessages = this.messages.map((msg) => msg.serialize());
      this.storage.saveMessages(serializedMessages);
    } catch (error) {
      console.error("Error saving messages:", error);
      chatNotificationService.showError("Error saving chat history");
    }
  }

  /**
   * Aggiunge un nuovo messaggio utente
   * @param {string} content - Contenuto del messaggio
   * @returns {boolean} true se il messaggio è stato aggiunto con successo
   */
  addUserMessage(content) {
    if (!MessageValidator.validateUserMessage(content)) {
      return false;
    }

    const message = MessageFactory.createMessage(MessageType.USER, content);
    this.messages.push(message);
    this.saveMessages();
    this.notifyObservers();
    return true;
  }

  /**
   * Aggiunge una risposta del bot
   * @param {Object} content - Contenuto della risposta
   * @returns {boolean} true se il messaggio è stato aggiunto con successo
   */
  addBotResponse(content) {
    if (!MessageValidator.validateBotResponse(content)) {
      return false;
    }

    const message = MessageFactory.createMessage(MessageType.BOT, content);
    this.messages.push(message);
    this.saveMessages();
    this.notifyObservers();
    return true;
  }

  /**
   * Aggiunge un messaggio di errore
   * @param {Object} error - Oggetto errore
   * @returns {boolean} true se il messaggio è stato aggiunto con successo
   */
  addErrorMessage(error) {
    if (!MessageValidator.validateErrorMessage(error)) {
      return false;
    }

    const message = MessageFactory.createMessage(MessageType.ERROR, error);
    this.messages.push(message);
    this.saveMessages();
    this.notifyObservers();
    return true;
  }

  /**
   * Aggiunge un messaggio di sistema
   * @param {string} content - Contenuto del messaggio
   * @returns {boolean} true se il messaggio è stato aggiunto con successo
   */
  addSystemMessage(content) {
    const message = MessageFactory.createMessage(MessageType.SYSTEM, content);
    this.messages.push(message);
    this.saveMessages();
    this.notifyObservers();
    return true;
  }

  /**
   * Recupera tutti i messaggi
   * @returns {Array} Array dei messaggi
   */
  getMessages() {
    return [...this.messages];
  }

  /**
   * Recupera l'ultimo messaggio
   * @returns {Object|null} Ultimo messaggio o null se non ce ne sono
   */
  getLastMessage() {
    return this.messages[this.messages.length - 1] || null;
  }

  /**
   * Cancella tutti i messaggi
   */
  clearMessages() {
    this.messages = [];
    this.storage.clearMessages();
    this.notifyObservers();
  }

  /**
   * Registra un observer per le modifiche allo store
   * @param {Function} observer - Funzione da chiamare quando lo store cambia
   */
  subscribe(observer) {
    this.observers.add(observer);
  }

  /**
   * Rimuove un observer
   * @param {Function} observer - Observer da rimuovere
   */
  unsubscribe(observer) {
    this.observers.delete(observer);
  }

  /**
   * Notifica tutti gli observer di un cambiamento
   * @private
   */
  notifyObservers() {
    this.observers.forEach((observer) => observer(this.getMessages()));
  }

  /**
   * Filtra i messaggi per tipo
   * @param {string} type - Tipo di messaggi da filtrare
   * @returns {Array} Messaggi filtrati
   */
  filterByType(type) {
    return this.messages.filter((msg) => msg.type === type);
  }

  /**
   * Conta i messaggi per tipo
   * @param {string} type - Tipo di messaggi da contare
   * @returns {number} Numero di messaggi del tipo specificato
   */
  countByType(type) {
    return this.filterByType(type).length;
  }

  /**
   * Verifica se ci sono messaggi di un certo tipo
   * @param {string} type - Tipo di messaggi da verificare
   * @returns {boolean} true se esistono messaggi del tipo specificato
   */
  hasMessageType(type) {
    return this.countByType(type) > 0;
  }

  /**
   * Trova un messaggio per indice
   * @param {number} index - Indice del messaggio
   * @returns {Object|null} Messaggio trovato o null
   */
  getMessageAt(index) {
    return this.messages[index] || null;
  }

  /**
   * Verifica se lo store è vuoto
   * @returns {boolean} true se non ci sono messaggi
   */
  isEmpty() {
    return this.messages.length === 0;
  }

  /**
   * Ottiene il numero totale di messaggi
   * @returns {number} Numero totale di messaggi
   */
  getMessageCount() {
    return this.messages.length;
  }
}

// Creiamo un'istanza singola dello store per l'applicazione
export const messageStore = new MessageStore();
