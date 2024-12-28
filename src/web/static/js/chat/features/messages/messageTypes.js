/**
 * Definisce i tipi e le strutture dei messaggi supportati nella chat
 */

/**
 * Enumerazione dei tipi di messaggio
 * @enum {string}
 */
export const MessageType = {
  USER: "user",
  BOT: "bot",
  SYSTEM: "system",
  ERROR: "error",
};

/**
 * Classe base per tutti i messaggi
 * Fornisce la struttura e i metodi comuni a tutti i tipi di messaggio
 */
export class BaseMessage {
  /**
   * @param {string} type - Tipo del messaggio
   * @param {string|Object} content - Contenuto del messaggio
   * @param {Date} [timestamp] - Timestamp del messaggio
   */
  constructor(type, content, timestamp = new Date()) {
    this.type = type;
    this.content = content;
    this.timestamp = timestamp;
  }

  /**
   * Serializza il messaggio per il salvataggio
   * @returns {Object} Versione serializzata del messaggio
   */
  serialize() {
    return {
      type: this.type,
      content: this.content,
      timestamp: this.timestamp.toISOString(),
    };
  }

  /**
   * Crea un'istanza di messaggio dalla sua versione serializzata
   * @param {Object} data - Dati serializzati
   * @returns {BaseMessage} Nuova istanza del messaggio
   */
  static deserialize(data) {
    return new BaseMessage(data.type, data.content, new Date(data.timestamp));
  }
}

/**
 * Rappresenta un messaggio dell'utente
 * @extends BaseMessage
 */
export class UserMessage extends BaseMessage {
  /**
   * @param {string} content - Testo del messaggio
   */
  constructor(content) {
    super(MessageType.USER, content);
  }

  /**
   * Valida il contenuto del messaggio utente
   * @returns {boolean} true se il messaggio è valido
   */
  isValid() {
    return typeof this.content === "string" && this.content.trim().length > 0;
  }
}

/**
 * Rappresenta un messaggio del bot
 * @extends BaseMessage
 */
export class BotMessage extends BaseMessage {
  /**
   * @param {Object} content - Contenuto della risposta del bot
   * @param {boolean} content.success - Indica se la risposta è valida
   * @param {string} [content.query] - Query SQL generata
   * @param {string} [content.explanation] - Spiegazione della query
   * @param {Array} [content.results] - Risultati dell'esecuzione
   * @param {string} [content.original_question] - Domanda originale
   * @param {boolean} [content.from_vector_store] - Se proviene dalla cache
   */
  constructor(content) {
    super(MessageType.BOT, content);
  }

  /**
   * Verifica se la risposta contiene un errore
   * @returns {boolean} true se la risposta è un errore
   */
  hasError() {
    return !this.content.success;
  }

  /**
   * Verifica se la risposta proviene dalla cache
   * @returns {boolean} true se la risposta proviene dalla cache
   */
  isFromCache() {
    return !!this.content.from_vector_store;
  }

  /**
   * Verifica se la risposta contiene una query SQL
   * @returns {boolean} true se presente una query SQL
   */
  hasQuery() {
    return !!this.content.query;
  }

  /**
   * Verifica se la risposta contiene risultati
   * @returns {boolean} true se presenti risultati
   */
  hasResults() {
    return (
      Array.isArray(this.content.results) && this.content.results.length > 0
    );
  }
}

/**
 * Rappresenta un messaggio di errore
 * @extends BaseMessage
 */
export class ErrorMessage extends BaseMessage {
  /**
   * @param {Object} content - Contenuto dell'errore
   * @param {string} content.error - Messaggio di errore
   * @param {string} [content.query] - Query che ha generato l'errore
   */
  constructor(content) {
    super(MessageType.ERROR, content);
  }

  /**
   * Ottiene il messaggio di errore formattato
   * @returns {string} Messaggio di errore
   */
  getErrorMessage() {
    return this.content.error || "Unknown error";
  }

  /**
   * Verifica se l'errore contiene una query
   * @returns {boolean} true se presente una query
   */
  hasQuery() {
    return !!this.content.query;
  }
}

/**
 * Rappresenta un messaggio di sistema (es. welcome message)
 * @extends BaseMessage
 */
export class SystemMessage extends BaseMessage {
  /**
   * @param {string} content - Contenuto del messaggio di sistema
   */
  constructor(content) {
    super(MessageType.SYSTEM, content);
  }
}

/**
 * Factory per la creazione di messaggi
 * Centralizza la logica di creazione dei vari tipi di messaggio
 */
export class MessageFactory {
  /**
   * Crea un nuovo messaggio del tipo appropriato
   * @param {string} type - Tipo di messaggio da creare
   * @param {string|Object} content - Contenuto del messaggio
   * @returns {BaseMessage} Nuova istanza del messaggio
   * @throws {Error} Se il tipo di messaggio non è supportato
   */
  static createMessage(type, content) {
    switch (type) {
      case MessageType.USER:
        return new UserMessage(content);
      case MessageType.BOT:
        return new BotMessage(content);
      case MessageType.ERROR:
        return new ErrorMessage(content);
      case MessageType.SYSTEM:
        return new SystemMessage(content);
      default:
        throw new Error(`Unsupported message type: ${type}`);
    }
  }

  /**
   * Crea un messaggio dalla sua versione serializzata
   * @param {Object} data - Dati serializzati del messaggio
   * @returns {BaseMessage} Nuova istanza del messaggio
   */
  static fromSerialized(data) {
    return MessageFactory.createMessage(data.type, data.content);
  }
}

/**
 * Validatore per i messaggi
 * Fornisce metodi di validazione per i vari tipi di messaggio
 */
export class MessageValidator {
  /**
   * Valida un messaggio utente
   * @param {string} content - Contenuto da validare
   * @returns {boolean} true se il contenuto è valido
   */
  static validateUserMessage(content) {
    return typeof content === "string" && content.trim().length > 0;
  }

  /**
   * Valida una risposta del bot
   * @param {Object} content - Contenuto da validare
   * @returns {boolean} true se il contenuto è valido
   */
  static validateBotResponse(content) {
    return content && typeof content === "object" && "success" in content;
  }

  /**
   * Valida un messaggio di errore
   * @param {Object} content - Contenuto da validare
   * @returns {boolean} true se il contenuto è valido
   */
  static validateErrorMessage(content) {
    return (
      content &&
      typeof content === "object" &&
      typeof content.error === "string"
    );
  }
}
