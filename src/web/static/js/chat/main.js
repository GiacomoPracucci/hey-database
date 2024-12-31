import { messageStore } from "./features/messages/messageStore.js";
import { messageView } from "./features/messages/messageView.js";
import { chatInput } from "./features/input/chatInput.js";
import { feedbackView } from "./features/feedback/feedbackView.js";
import { feedbackApiService } from "./features/feedback/feedbackApi.js";
import { chatApiService } from "./utils/chatApi.js";
import { chatDomService } from "./utils/chatDom.js";
import { chatNotificationService } from "./utils/chatNotifications.js";
import { DOM_ELEMENTS } from "./config/constants.js";

/**
 * ChatApplication è la classe principale che orchesttra tutti i moduli della chat.
 * Gestisce l'inizializzazione e il coordinamento tra i vari componenti.
 */
class ChatApplication {
  /**
   * Inizializza l'applicazione chat
   */
  constructor() {
    // Verifica che tutti i servizi necessari siano disponibili
    this.validateServices();

    // Inizializza i listener per gli eventi DOM
    this.initializeEventListeners();

    // Inizializza la gestione della cronologia chat
    this.initializeChatHistory();

    // Flag per tracciare lo stato di invio
    this.isSending = false;
  }

  /**
   * Valida la presenza di tutti i servizi necessari
   * @private
   * @throws {Error} Se manca qualche servizio essenziale
   */
  validateServices() {
    const requiredServices = {
      messageStore,
      messageView,
      chatInput,
      feedbackView,
      feedbackApiService,
      chatApiService,
      chatDomService,
      chatNotificationService,
    };

    for (const [name, service] of Object.entries(requiredServices)) {
      if (!service) {
        throw new Error(`Required service ${name} is not available`);
      }
    }
  }

  /**
   * Inizializza tutti gli event listener necessari
   * @private
   */
  /**
   * Inizializza tutti gli event listener necessari
   * @private
   */
  initializeEventListeners() {
    // Inizializza il pulsante di pulizia chat
    const clearButton = document.querySelector(`#${DOM_ELEMENTS.CLEAR_BUTTON}`);
    if (clearButton) {
      clearButton.addEventListener("click", (e) => this.handleClearChat(e));
    }

    // Sottoscrive agli aggiornamenti dello store
    messageStore.subscribe((messages) => {
      messageView.updateView(messages);
    });

    // Configura il callback per l'input
    chatInput.onSubmit = (message) => this.handleMessageSubmit(message);

    // Configura il callback per il feedback
    feedbackView.onFeedbackSubmit = (data) => this.handleFeedbackSubmit(data);

    // Gestisce il reload della pagina
    window.addEventListener("beforeunload", () => this.handlePageUnload());
  }

  /**
   * Inizializza la cronologia della chat
   * @private
   */
  initializeChatHistory() {
    // Pulisce il localStorage solo su reload effettivo
    if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
      messageStore.clearMessages();
    } else {
      // Ripristina i messaggi solo durante la navigazione SPA
      messageStore.loadMessages();
    }
  }

  /**
   * Gestisce l'invio di un nuovo messaggio
   * @param {string} message - Messaggio da inviare
   * @private
   */
  async handleMessageSubmit(message) {
    if (this.isSending) return;

    try {
      this.isSending = true;
      this.setInterfaceState(true);

      // Aggiunge il messaggio utente
      messageStore.addUserMessage(message);

      // Mostra l'indicatore di digitazione
      messageView.showLoading();

      // Invia la richiesta al server
      const response = await chatApiService.sendMessage(message);

      // Aggiunge la risposta del bot
      if (!response.success) {
        messageStore.addErrorMessage({
          error: response.error || "Unknown error",
          query: response.query,
        });
      } else {
        messageStore.addBotResponse(response);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      messageStore.addErrorMessage({
        error: error.message,
      });
    } finally {
      messageView.hideLoading();
      this.setInterfaceState(false);
      this.isSending = false;
      chatInput.focus();
    }
  }

  /**
   * Gestisce l'invio di un feedback
   * @param {Object} feedbackData - Dati del feedback
   * @private
   */
  /**
   * Gestisce l'invio di un feedback
   * @param {Object} feedbackData - Dati del feedback
   * @private
   */
  async handleFeedbackSubmit(feedbackData) {
    try {
      await feedbackApiService.submitFeedback(feedbackData);
      return true; // Ritorna true in caso di successo
    } catch (error) {
      console.error("Error submitting feedback:", error);
      throw error; // Rilancia l'errore per gestirlo nel componente feedback
    }
  }

  /**
   * Gestisce la pulizia della chat
   * @param {Event} event - Evento click
   * @private
   */
  handleClearChat(event) {
    event.preventDefault();

    // Disabilita temporaneamente il pulsante
    const button = event.target;
    button.disabled = true;

    // Esegue la pulizia
    messageStore.clearMessages();
    chatInput.clear();

    // Mostra notifica di conferma
    chatNotificationService.showSuccess("Chat cleared successfully");

    // Riabilita il pulsante dopo un breve delay
    setTimeout(() => {
      button.disabled = false;
    }, 500);
  }

  /**
   * Gestisce lo scaricamento della pagina
   * @private
   */
  handlePageUnload() {
    if (messageStore.hasMessages()) {
      messageStore.saveMessages();
    }
  }

  /**
   * Imposta lo stato dell'interfaccia
   * @param {boolean} disabled - Se true, disabilita l'interfaccia
   * @private
   */
  setInterfaceState(disabled) {
    if (disabled) {
      chatInput.disable();
      feedbackView.disableAllButtons();
    } else {
      chatInput.enable();
      feedbackView.enableAllButtons();
    }
  }
}

// Inizializza l'applicazione quando il DOM è pronto
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.chatApp = new ChatApplication();
  } catch (error) {
    console.error("Error initializing chat application:", error);
    chatNotificationService.showError("Error initializing chat application");
  }
});
