import { MessageType } from "./messageTypes.js";
import { chatDomService } from "../../utils/dom.js";
import { CSS_CLASSES } from "../../config/constants.js";

/**
 * MessageView gestisce la visualizzazione dei messaggi nella chat.
 * Si occupa di renderizzare i messaggi e gestire le interazioni UI correlate.
 */
export class MessageView {
  /**
   * Inizializza la vista dei messaggi
   * @param {Element} container - Elemento contenitore dei messaggi
   */
  constructor(container) {
    this.container = container;
    if (!this.container) {
      throw new Error("Message container element not found");
    }

    // Stato interno del loading
    this.isLoading = false;
  }

  /**
   * Renderizza un nuovo messaggio
   * @param {Object} message - Messaggio da renderizzare
   * @returns {HTMLElement} Elemento messaggio renderizzato
   */
  renderMessage(message) {
    let messageElement;

    switch (message.type) {
      case MessageType.USER:
        messageElement = this.renderUserMessage(message);
        break;
      case MessageType.BOT:
        messageElement = this.renderBotMessage(message);
        break;
      case MessageType.ERROR:
        messageElement = this.renderErrorMessage(message);
        break;
      case MessageType.SYSTEM:
        messageElement = this.renderSystemMessage(message);
        break;
      default:
        console.error("Unknown message type:", message.type);
        return null;
    }

    this.container.appendChild(messageElement);
    this.scrollToBottom();
    return messageElement;
  }

  /**
   * Renderizza un messaggio utente
   * @param {Object} message - Messaggio utente
   * @returns {HTMLElement} Elemento messaggio
   * @private
   */
  renderUserMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${CSS_CLASSES.MESSAGE.USER}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = CSS_CLASSES.MESSAGE.CONTENT;
    contentDiv.textContent = message.content;

    messageDiv.appendChild(contentDiv);
    return messageDiv;
  }

  /**
   * Renderizza un messaggio del bot
   * @param {Object} message - Messaggio bot
   * @returns {HTMLElement} Elemento messaggio
   * @private
   */
  renderBotMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${CSS_CLASSES.MESSAGE.BOT}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = CSS_CLASSES.MESSAGE.CONTENT;

    // Aggiungi query SQL se presente
    if (message.content.query) {
      contentDiv.appendChild(
        chatDomService.createQueryContainer({
          query: message.content.query,
          original_question: message.content.original_question,
          explanation: message.content.explanation,
        })
      );
    }

    // Aggiungi spiegazione se presente
    if (message.content.explanation) {
      contentDiv.appendChild(
        chatDomService.createExplanation(message.content.explanation)
      );
    }

    // Aggiungi risultati se presenti
    if (message.content.results?.length > 0) {
      contentDiv.appendChild(
        chatDomService.createResultsTable(message.content.results)
      );
    }

    messageDiv.appendChild(contentDiv);
    return messageDiv;
  }

  /**
   * Renderizza un messaggio di errore
   * @param {Object} message - Messaggio errore
   * @returns {HTMLElement} Elemento messaggio
   * @private
   */
  renderErrorMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${CSS_CLASSES.MESSAGE.BOT}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = CSS_CLASSES.MESSAGE.CONTENT;

    chatDomService.createErrorMessage(contentDiv, {
      error: message.content.error,
      query: message.content.query,
    });

    messageDiv.appendChild(contentDiv);
    return messageDiv;
  }

  /**
   * Renderizza un messaggio di sistema
   * @param {Object} message - Messaggio sistema
   * @returns {HTMLElement} Elemento messaggio
   * @private
   */
  renderSystemMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${CSS_CLASSES.MESSAGE.BOT} ${CSS_CLASSES.MESSAGE.WELCOME}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = CSS_CLASSES.MESSAGE.CONTENT;
    contentDiv.innerHTML = message.content;

    messageDiv.appendChild(contentDiv);
    return messageDiv;
  }

  /**
   * Aggiorna la vista con una lista di messaggi
   * @param {Array} messages - Lista di messaggi da visualizzare
   */
  updateView(messages) {
    // Pulisce il contenitore
    this.clearMessages();

    // Renderizza tutti i messaggi
    messages.forEach((message) => this.renderMessage(message));
  }

  /**
   * Mostra l'indicatore di caricamento
   */
  showLoading() {
    if (!this.isLoading) {
      this.loadingIndicator = chatDomService.addLoadingIndicator();
      this.isLoading = true;
    }
  }

  /**
   * Nasconde l'indicatore di caricamento
   */
  hideLoading() {
    if (this.isLoading) {
      chatDomService.removeLoadingIndicator();
      this.isLoading = false;
    }
  }

  /**
   * Pulisce tutti i messaggi dal contenitore
   */
  clearMessages() {
    // Mantiene solo il messaggio di benvenuto
    const welcomeMessage = this.container.querySelector(
      `.${CSS_CLASSES.MESSAGE.WELCOME}`
    );
    const loadingIndicator = this.container.querySelector(
      `.${CSS_CLASSES.LOADING.CONTAINER}`
    );

    this.container.innerHTML = "";

    if (welcomeMessage) {
      this.container.appendChild(welcomeMessage);
    }
    if (loadingIndicator) {
      this.container.appendChild(loadingIndicator);
    }
  }

  /**
   * Scorre la chat fino all'ultimo messaggio
   */
  scrollToBottom() {
    this.container.scrollTop = this.container.scrollHeight;
  }

  /**
   * Verifica se un elemento è visibile nel contenitore
   * @param {HTMLElement} element - Elemento da verificare
   * @returns {boolean} true se l'elemento è visibile
   */
  isElementVisible(element) {
    const rect = element.getBoundingClientRect();
    const containerRect = this.container.getBoundingClientRect();

    return rect.top >= containerRect.top && rect.bottom <= containerRect.bottom;
  }

  /**
   * Evidenzia temporaneamente un messaggio
   * @param {HTMLElement} messageElement - Elemento da evidenziare
   */
  highlightMessage(messageElement) {
    messageElement.classList.add("highlighted");
    setTimeout(() => {
      messageElement.classList.remove("highlighted");
    }, 2000);
  }
}

// Creiamo l'istanza della vista quando il DOM è pronto
let messageView;
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("chatMessages");
  if (container) {
    messageView = new MessageView(container);
  }
});

export { messageView };
