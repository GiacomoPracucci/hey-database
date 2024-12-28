import { chatDomService } from "../../utils/dom.js";
import { DOM_ELEMENTS, TIMING } from "../../config/constants.js";

/**
 * ChatInput gestisce l'input utente nella chat.
 * Si occupa della textarea, del pulsante di invio e di tutte le interazioni correlate.
 */
export class ChatInput {
  /**
   * Inizializza il gestore dell'input
   * @param {Function} onSubmit - Callback da chiamare quando viene inviato un messaggio
   */
  constructor(onSubmit) {
    // Riferimenti DOM
    this.textarea = document.getElementById(DOM_ELEMENTS.USER_INPUT);
    this.sendButton = document.getElementById(DOM_ELEMENTS.SEND_BUTTON);

    // Validazione elementi necessari
    if (!this.textarea || !this.sendButton) {
      throw new Error("Required input elements not found");
    }

    this.onSubmit = onSubmit;
    this.isDisabled = false;

    // Inizializza gli event listener
    this.initializeEventListeners();

    // Imposta l'altezza iniziale
    this.adjustHeight();
  }

  /**
   * Inizializza tutti gli event listener necessari
   * @private
   */
  initializeEventListeners() {
    // Gestione invio con pulsante
    this.sendButton.addEventListener("click", () => this.handleSubmit());

    // Gestione eventi textarea
    this.textarea.addEventListener("input", () => this.adjustHeight());
    this.textarea.addEventListener("keypress", (e) => this.handleKeyPress(e));
    this.textarea.addEventListener("keydown", (e) => this.handleKeyDown(e));
    this.textarea.addEventListener("paste", () => {
      // Aggiusta l'altezza dopo il paste
      setTimeout(() => this.adjustHeight(), 0);
    });
  }

  /**
   * Gestisce la pressione dei tasti nella textarea
   * @param {KeyboardEvent} event - Evento keyboard
   * @private
   */
  handleKeyPress(event) {
    // Invio senza shift preme il tasto di invio
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      this.handleSubmit();
    }
  }

  /**
   * Gestisce gli eventi keydown nella textarea
   * @param {KeyboardEvent} event - Evento keyboard
   * @private
   */
  handleKeyDown(event) {
    // Impedisce l'invio se il testo è vuoto
    if (event.key === "Enter" && !event.shiftKey && !this.getValue().trim()) {
      event.preventDefault();
    }
  }

  /**
   * Gestisce l'invio del messaggio
   * @private
   */
  handleSubmit() {
    const value = this.getValue().trim();
    if (!value || this.isDisabled) return;

    // Chiama il callback di submit
    if (this.onSubmit) {
      this.onSubmit(value);
    }

    // Pulisce l'input
    this.clear();
  }

  /**
   * Aggiusta l'altezza della textarea in base al contenuto
   * @private
   */
  adjustHeight() {
    this.textarea.style.height = "auto";
    this.textarea.style.height = `${this.textarea.scrollHeight}px`;
  }

  /**
   * Imposta il focus sulla textarea
   */
  focus() {
    this.textarea.focus();
  }

  /**
   * Rimuove il focus dalla textarea
   */
  blur() {
    this.textarea.blur();
  }

  /**
   * Ottiene il valore corrente della textarea
   * @returns {string} Il valore corrente
   */
  getValue() {
    return this.textarea.value;
  }

  /**
   * Imposta il valore della textarea
   * @param {string} value - Il nuovo valore
   */
  setValue(value) {
    this.textarea.value = value;
    this.adjustHeight();
  }

  /**
   * Pulisce la textarea
   */
  clear() {
    this.setValue("");
  }

  /**
   * Disabilita l'input
   */
  disable() {
    this.isDisabled = true;
    this.textarea.disabled = true;
    this.sendButton.disabled = true;
  }

  /**
   * Abilita l'input
   */
  enable() {
    this.isDisabled = false;
    this.textarea.disabled = false;
    this.sendButton.disabled = false;
  }

  /**
   * Verifica se l'input è vuoto
   * @returns {boolean} true se l'input è vuoto
   */
  isEmpty() {
    return !this.getValue().trim();
  }

  /**
   * Verifica se l'input è disabilitato
   * @returns {boolean} true se l'input è disabilitato
   */
  isInputDisabled() {
    return this.isDisabled;
  }

  /**
   * Seleziona tutto il testo nella textarea
   */
  selectAll() {
    this.textarea.select();
  }

  /**
   * Imposta la posizione del cursore
   * @param {number} position - Posizione del cursore
   */
  setCursorPosition(position) {
    this.textarea.setSelectionRange(position, position);
  }

  /**
   * Inserisce il testo nella posizione corrente del cursore
   * @param {string} text - Testo da inserire
   */
  insertAtCursor(text) {
    const start = this.textarea.selectionStart;
    const end = this.textarea.selectionEnd;
    const current = this.getValue();

    this.setValue(current.substring(0, start) + text + current.substring(end));

    this.setCursorPosition(start + text.length);
  }

  /**
   * Gestisce il resize della textarea quando la finestra cambia dimensione
   */
  handleResize() {
    this.adjustHeight();
  }

  /**
   * Aggiunge una classe CSS alla textarea
   * @param {string} className - Classe da aggiungere
   */
  addClass(className) {
    this.textarea.classList.add(className);
  }

  /**
   * Rimuove una classe CSS dalla textarea
   * @param {string} className - Classe da rimuovere
   */
  removeClass(className) {
    this.textarea.classList.remove(className);
  }
}

// Creiamo un'istanza del gestore input quando il DOM è pronto
let chatInput;
document.addEventListener("DOMContentLoaded", () => {
  chatInput = new ChatInput((message) => {
    // Qui verrà iniettato il gestore del submit dal main.js
    console.log("Message submitted:", message);
  });

  // Gestisce il resize della finestra
  window.addEventListener("resize", () => {
    if (chatInput) {
      chatInput.handleResize();
    }
  });
});

export { chatInput };
