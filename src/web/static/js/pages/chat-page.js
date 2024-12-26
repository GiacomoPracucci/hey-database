/**
 * ChatPage
 *
 * Gestisce la logica della pagina di chat, coordinando l'interazione tra
 * i Web Components e i servizi. Questo script è responsabile di:
 * - Inizializzare i componenti della chat
 * - Gestire l'invio e la ricezione dei messaggi
 * - Gestire lo stato della chat
 * - Coordinare le interazioni UI
 */

import { chatService } from "../services/chat-service.js";

class ChatPage {
  constructor() {
    // Riferimenti agli elementi del DOM
    this.chatMessages = document.getElementById("chatMessages");
    this.userInput = document.getElementById("userInput");
    this.sendButton = document.getElementById("sendButton");
    this.clearButton = document.getElementById("clearChat");

    // Binding dei metodi per mantenere il contesto
    this.handleSendMessage = this.handleSendMessage.bind(this);
    this.handleInputKeypress = this.handleInputKeypress.bind(this);
    this.handleClearChat = this.handleClearChat.bind(this);

    // Inizializza la pagina
    this.initialize();
  }

  /**
   * Inizializza la pagina di chat
   * - Imposta gli event listener
   * - Ripristina i messaggi precedenti
   */
  initialize() {
    // Imposta gli event listener
    this.sendButton.addEventListener("click", this.handleSendMessage);
    this.userInput.addEventListener("keypress", this.handleInputKeypress);
    this.clearButton.addEventListener("click", this.handleClearChat);
    this.userInput.addEventListener(
      "input",
      this.adjustTextareaHeight.bind(this)
    );

    // Ripristina i messaggi dal localStorage
    this.restoreChatMessages();

    // Imposta l'altezza iniziale della textarea
    this.adjustTextareaHeight();
  }

  /**
   * Gestisce l'invio di un messaggio
   * @returns {Promise<void>}
   */
  async handleSendMessage() {
    const message = this.userInput.value.trim();
    if (!message) return;

    // Disabilita l'input durante l'elaborazione
    this.setInputState(true);

    // Aggiunge il messaggio dell'utente
    this.addMessage(message, "user");
    this.userInput.value = "";
    this.adjustTextareaHeight();

    // Mostra l'indicatore di digitazione
    this.addLoadingIndicator();

    try {
      // Invia il messaggio al servizio chat
      const response = await chatService.processMessage(message);

      // Rimuove l'indicatore di digitazione
      this.removeLoadingIndicator();

      // Aggiunge la risposta del bot
      this.addMessage(response, "bot");
    } catch (error) {
      // Rimuove l'indicatore di digitazione
      this.removeLoadingIndicator();

      // Mostra l'errore
      this.addMessage(
        {
          success: false,
          error: "Errore di comunicazione con il server",
        },
        "bot"
      );
    } finally {
      // Riabilita l'input
      this.setInputState(false);
      this.userInput.focus();
    }
  }

  /**
   * Gestisce l'evento keypress sulla textarea
   * @param {KeyboardEvent} e
   */
  handleInputKeypress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      this.handleSendMessage();
    }
  }

  /**
   * Gestisce la pulizia della chat
   */
  handleClearChat() {
    chatService.clearMessages();

    // Mantiene solo il messaggio di benvenuto
    const welcomeMessage = this.chatMessages.querySelector(
      ".message.bot.welcome"
    );
    this.chatMessages.innerHTML = "";
    if (welcomeMessage) {
      this.chatMessages.appendChild(welcomeMessage);
    }

    // Resetta l'input
    this.userInput.value = "";
    this.adjustTextareaHeight();

    // Mostra notifica
    this.showToast("success", "Chat cleared successfully", "fa-check");
  }

  /**
   * Aggiunge un messaggio alla chat
   * @param {string|Object} content - Contenuto del messaggio
   * @param {string} type - Tipo di messaggio ('user' o 'bot')
   */
  addMessage(content, type = "user") {
    if (type === "user") {
      // Crea un messaggio utente semplice
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${type}`;
      messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
            `;
      this.chatMessages.appendChild(messageDiv);
    } else {
      // Utilizza il componente personalizzato per i messaggi bot
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${type}`;

      if (!content.success) {
        // Messaggio di errore
        messageDiv.innerHTML = `
                    <div class="message-content">
                        <toast-notification 
                            type="error"
                            message="${content.error}"
                            duration="5000">
                        </toast-notification>
                    </div>
                `;
      } else {
        // Risposta normale con query SQL
        messageDiv.innerHTML = `
                    <div class="message-content">
                        <sql-query-box
                            query="${content.query}"
                            explanation="${content.explanation}"
                            show-feedback="true">
                        </sql-query-box>
                        ${
                          content.results
                            ? `
                            <results-table
                                page-size="10"
                                show-pagination="true">
                            </results-table>
                        `
                            : ""
                        }
                    </div>
                `;

        // Se ci sono risultati, li imposta nella tabella
        if (content.results) {
          const table = messageDiv.querySelector("results-table");
          table.data = content.results;
        }
      }

      this.chatMessages.appendChild(messageDiv);
    }

    // Scrolla alla fine della chat
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  /**
   * Aggiunge l'indicatore di caricamento
   */
  addLoadingIndicator() {
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "typing-indicator-container";
    loadingDiv.id = "typingIndicator";

    loadingDiv.innerHTML = `
            <typing-indicator text="Thinking..."></typing-indicator>
        `;

    this.chatMessages.appendChild(loadingDiv);
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  /**
   * Rimuove l'indicatore di caricamento
   */
  removeLoadingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) {
      indicator.remove();
    }
  }

  /**
   * Mostra un toast di notifica
   * @param {string} type - Tipo di notifica
   * @param {string} message - Messaggio da mostrare
   * @param {string} icon - Classe dell'icona FontAwesome
   */
  showToast(type, message, icon = null) {
    const toast = document.createElement("toast-notification");
    toast.setAttribute("type", type);
    toast.setAttribute("message", message);
    if (icon) {
      toast.setAttribute("icon", icon);
    }
    document.body.appendChild(toast);
  }

  /**
   * Ripristina i messaggi precedenti dal localStorage
   */
  restoreChatMessages() {
    const messages = chatService.getMessagesFromStorage();
    messages.forEach((msg) => {
      this.addMessage(msg.content, msg.type);
    });
  }

  /**
   * Regola l'altezza della textarea in base al contenuto
   */
  adjustTextareaHeight() {
    this.userInput.style.height = "auto";
    this.userInput.style.height = `${this.userInput.scrollHeight}px`;
  }

  /**
   * Imposta lo stato di abilitazione/disabilitazione degli input
   * @param {boolean} disabled
   */
  setInputState(disabled) {
    this.userInput.disabled = disabled;
    this.sendButton.disabled = disabled;
  }
}

// Inizializza la pagina quando il DOM è caricato
document.addEventListener("DOMContentLoaded", () => {
  new ChatPage();
});
