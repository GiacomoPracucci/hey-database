import { CSS_CLASSES, ICONS, UI_TEXTS } from "../../config/constants.js";
import { chatNotificationService } from "../../utils/notifications.js";

/**
 * FeedbackView gestisce l'interfaccia utente per il sistema di feedback.
 * Si occupa della creazione e gestione dei pulsanti di feedback e delle loro interazioni.
 */
export class FeedbackView {
  /**
   * Inizializza il gestore della vista feedback
   * @param {Function} onFeedbackSubmit - Callback da chiamare quando viene inviato un feedback
   */
  constructor(onFeedbackSubmit) {
    this.onFeedbackSubmit = onFeedbackSubmit;
    // Mappa per tenere traccia dei pulsanti attivi
    this.activeButtons = new Map();
  }

  /**
   * Crea un nuovo pulsante di feedback
   * @param {Object} feedbackData - Dati associati al feedback
   * @returns {HTMLButtonElement} Pulsante di feedback creato
   */
  createFeedbackButton(feedbackData) {
    const button = document.createElement("button");
    button.className = CSS_CLASSES.FEEDBACK.BUTTON;
    button.innerHTML = `<i class="fas ${ICONS.THUMBS_UP}"></i>`;
    button.title = UI_TEXTS.FEEDBACK_BUTTON;

    // Genera un ID univoco per il pulsante
    const buttonId = `feedback-${Date.now()}-${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    button.setAttribute("data-feedback-id", buttonId);

    // Memorizza il pulsante e i suoi dati
    this.activeButtons.set(buttonId, {
      button,
      data: feedbackData,
      isVoted: false,
    });

    // Aggiunge il listener per il click
    button.addEventListener("click", () => this.handleFeedbackClick(buttonId));

    return button;
  }

  /**
   * Gestisce il click su un pulsante di feedback
   * @param {string} buttonId - ID del pulsante cliccato
   * @private
   */
  async handleFeedbackClick(buttonId) {
    const buttonData = this.activeButtons.get(buttonId);
    if (!buttonData || buttonData.isVoted) return;

    const { button, data } = buttonData;

    try {
      // Disabilita il pulsante durante l'invio
      this.setButtonLoading(button, true);

      // Chiama il callback di submit
      await this.onFeedbackSubmit(data);

      // Aggiorna lo stato del pulsante
      this.markButtonAsVoted(buttonId);
      chatNotificationService.showSuccess(UI_TEXTS.FEEDBACK_THANKS);
    } catch (error) {
      // Ripristina lo stato del pulsante in caso di errore
      this.setButtonLoading(button, false);
      chatNotificationService.showError(error.message);
    }
  }

  /**
   * Imposta lo stato di caricamento di un pulsante
   * @param {HTMLButtonElement} button - Pulsante da aggiornare
   * @param {boolean} isLoading - Stato di caricamento
   * @private
   */
  setButtonLoading(button, isLoading) {
    button.disabled = isLoading;
    button.innerHTML = `<i class="fas ${
      isLoading ? "fa-spinner fa-spin" : ICONS.THUMBS_UP
    }"></i>`;
  }

  /**
   * Marca un pulsante come votato
   * @param {string} buttonId - ID del pulsante
   * @private
   */
  markButtonAsVoted(buttonId) {
    const buttonData = this.activeButtons.get(buttonId);
    if (!buttonData) return;

    const { button } = buttonData;
    button.classList.add(CSS_CLASSES.FEEDBACK.VOTED);
    button.disabled = true;
    button.title = UI_TEXTS.FEEDBACK_SUBMITTED;
    // Rimuovi l'icona di loading e metti il check
    button.innerHTML = `<i class="fas fa-check"></i>`;
    buttonData.isVoted = true;

    // Aggiorna la mappa
    this.activeButtons.set(buttonId, buttonData);
  }

  /**
   * Resetta lo stato di un pulsante
   * @param {string} buttonId - ID del pulsante
   */
  resetButton(buttonId) {
    const buttonData = this.activeButtons.get(buttonId);
    if (!buttonData) return;

    const { button } = buttonData;
    button.classList.remove(CSS_CLASSES.FEEDBACK.VOTED);
    button.disabled = false;
    button.title = UI_TEXTS.FEEDBACK_BUTTON;
    button.innerHTML = `<i class="fas ${ICONS.THUMBS_UP}"></i>`;
    buttonData.isVoted = false;

    // Aggiorna la mappa
    this.activeButtons.set(buttonId, buttonData);
  }

  /**
   * Rimuove un pulsante di feedback
   * @param {string} buttonId - ID del pulsante da rimuovere
   */
  removeButton(buttonId) {
    const buttonData = this.activeButtons.get(buttonId);
    if (!buttonData) return;

    const { button } = buttonData;
    button.remove();
    this.activeButtons.delete(buttonId);
  }

  /**
   * Disabilita tutti i pulsanti di feedback
   */
  disableAllButtons() {
    for (const [buttonId, buttonData] of this.activeButtons) {
      buttonData.button.disabled = true;
    }
  }

  /**
   * Abilita tutti i pulsanti di feedback
   */
  enableAllButtons() {
    for (const [buttonId, buttonData] of this.activeButtons) {
      if (!buttonData.isVoted) {
        buttonData.button.disabled = false;
      }
    }
  }

  /**
   * Verifica se un pulsante è stato votato
   * @param {string} buttonId - ID del pulsante
   * @returns {boolean} true se il pulsante è stato votato
   */
  isButtonVoted(buttonId) {
    const buttonData = this.activeButtons.get(buttonId);
    return buttonData ? buttonData.isVoted : false;
  }

  /**
   * Ottiene tutti i pulsanti votati
   * @returns {Array<string>} Array di ID dei pulsanti votati
   */
  getVotedButtons() {
    return Array.from(this.activeButtons.entries())
      .filter(([_, data]) => data.isVoted)
      .map(([id]) => id);
  }

  /**
   * Pulisce la memoria dei pulsanti non più nel DOM
   */
  cleanup() {
    for (const [buttonId, buttonData] of this.activeButtons) {
      if (!document.body.contains(buttonData.button)) {
        this.activeButtons.delete(buttonId);
      }
    }
  }
}

// Creiamo un'istanza della vista feedback quando il DOM è pronto
let feedbackView;
document.addEventListener("DOMContentLoaded", () => {
  feedbackView = new FeedbackView(async (feedbackData) => {
    // Il callback verrà iniettato dal main.js
    console.log("Feedback submitted:", feedbackData);
  });
});

export { feedbackView };
