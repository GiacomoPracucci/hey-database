import { chatDomService } from "../../utils/chatDom.js";
import { DOM_ELEMENTS, TIMING } from "../../config/constants.js";
import { chatViewManager } from "../../utils/chatViewManager.js";

/**
 * ChatInput gestisce l'input utente nella chat.
 * Si occupa della gestione degli input in entrambe le viste (welcome e chat)
 * e di tutte le interazioni correlate.
 */
export class ChatInput {
    /**
     * Inizializza il gestore dell'input
     * @param {Function} onSubmit - Callback da chiamare quando viene inviato un messaggio
     */
    constructor(onSubmit) {
        // Welcome View elements
        this.welcomeInput = document.getElementById(DOM_ELEMENTS.WELCOME_INPUT);
        this.welcomeSendButton = document.getElementById(DOM_ELEMENTS.WELCOME_SEND_BUTTON);

        // Chat View elements
        this.chatInput = document.getElementById(DOM_ELEMENTS.CHAT_INPUT);
        this.chatSendButton = document.getElementById(DOM_ELEMENTS.CHAT_SEND_BUTTON);

        // Validazione elementi necessari
        this.validateElements();

        this.onSubmit = onSubmit;
        this.isDisabled = false;
        this.currentView = 'welcome';

        // Inizializza gli event listener
        this.initializeEventListeners();

        // Imposta l'altezza iniziale
        this.adjustHeight(this.welcomeInput);
        this.adjustHeight(this.chatInput);
    }

    /**
     * Valida la presenza di tutti gli elementi DOM necessari
     * @private
     * @throws {Error} Se mancano elementi necessari
     */
    validateElements() {
        if (!this.welcomeInput || !this.welcomeSendButton || 
            !this.chatInput || !this.chatSendButton) {
            throw new Error("Required input elements not found");
        }
    }

    /**
     * Inizializza tutti gli event listener necessari
     * @private
     */
    initializeEventListeners() {
        // Welcome View listeners
        this.welcomeInput.addEventListener("input", () => {
            this.adjustHeight(this.welcomeInput);
            this.updateButtonState(this.welcomeInput, this.welcomeSendButton);
        });

        this.welcomeInput.addEventListener("keypress", (e) => 
            this.handleKeyPress(e, this.welcomeInput));

        this.welcomeSendButton.addEventListener("click", () => 
            this.handleSubmit(this.welcomeInput));

        // Chat View listeners
        this.chatInput.addEventListener("input", () => {
            this.adjustHeight(this.chatInput);
            this.updateButtonState(this.chatInput, this.chatSendButton);
        });

        this.chatInput.addEventListener("keypress", (e) => 
            this.handleKeyPress(e, this.chatInput));

        this.chatSendButton.addEventListener("click", () => 
            this.handleSubmit(this.chatInput));

        // Paste handlers
        [this.welcomeInput, this.chatInput].forEach(input => {
            input.addEventListener("paste", () => {
                setTimeout(() => this.adjustHeight(input), 0);
            });
        });
    }

    /**
     * Gestisce la pressione dei tasti
     * @param {KeyboardEvent} event - Evento keyboard
     * @param {HTMLElement} input - Input element corrente
     * @private
     */
    handleKeyPress(event, input) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.handleSubmit(input);
        }
    }

    /**
     * Gestisce l'invio del messaggio
     * @param {HTMLElement} input - Input element da cui proviene il messaggio
     * @private
     */
    handleSubmit(input) {
        const value = input.value.trim();
        if (!value || this.isDisabled) return;

        // Chiama il callback di submit
        if (this.onSubmit) {
            this.onSubmit(value);
        }

        // Pulisce l'input
        this.clear(input);
    }

    /**
     * Aggiusta l'altezza dell'input in base al contenuto
     * @param {HTMLElement} input - Input element da aggiustare
     * @private
     */
    adjustHeight(input) {
        input.style.height = "auto";
        input.style.height = `${input.scrollHeight}px`;
    }

    /**
     * Aggiorna lo stato del pulsante di invio
     * @param {HTMLElement} input - Input element di riferimento
     * @param {HTMLElement} button - Button element da aggiornare
     * @private
     */
    updateButtonState(input, button) {
        button.disabled = !input.value.trim();
    }

    /**
     * Imposta il focus sull'input appropriato
     */
    focus() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        input.focus();
    }

    /**
     * Rimuove il focus dall'input appropriato
     */
    blur() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        input.blur();
    }

    /**
     * Ottiene il valore dell'input corrente
     * @returns {string} Il valore corrente
     */
    getValue() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        return input.value;
    }

    /**
     * Imposta il valore dell'input
     * @param {string} value - Il nuovo valore
     * @param {HTMLElement} input - Input element da aggiornare
     */
    setValue(value, input) {
        input.value = value;
        this.adjustHeight(input);
        this.updateButtonState(input, 
            input === this.welcomeInput ? this.welcomeSendButton : this.chatSendButton);
    }

    /**
     * Pulisce l'input specificato
     * @param {HTMLElement} input - Input element da pulire
     */
    clear(input) {
        this.setValue("", input);
    }

    /**
     * Disabilita entrambi gli input
     */
    disable() {
        this.isDisabled = true;
        [this.welcomeInput, this.chatInput].forEach(input => {
            input.disabled = true;
        });
        [this.welcomeSendButton, this.chatSendButton].forEach(button => {
            button.disabled = true;
        });
    }

    /**
     * Abilita entrambi gli input
     */
    enable() {
        this.isDisabled = false;
        [this.welcomeInput, this.chatInput].forEach(input => {
            input.disabled = false;
        });
        // Aggiorna lo stato dei pulsanti in base al contenuto
        this.updateButtonState(this.welcomeInput, this.welcomeSendButton);
        this.updateButtonState(this.chatInput, this.chatSendButton);
    }

    /**
     * Cambia la vista corrente
     * @param {string} view - Vista da attivare ('welcome' o 'chat')
     */
    switchView(view) {
        if (view !== 'welcome' && view !== 'chat') return;
        this.currentView = view;
        
        // Reset e focus appropriato
        if (view === 'chat') {
            this.clear(this.welcomeInput);
            this.chatInput.focus();
        } else {
            this.clear(this.chatInput);
            this.welcomeInput.focus();
        }
    }

    /**
     * Verifica se l'input corrente è vuoto
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
     * Gestisce il resize della finestra
     */
    handleResize() {
        this.adjustHeight(this.welcomeInput);
        this.adjustHeight(this.chatInput);
    }

    /**
     * Aggiunge una classe CSS all'input corrente
     * @param {string} className - Classe da aggiungere
     */
    addClass(className) {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        input.classList.add(className);
    }

    /**
     * Rimuove una classe CSS dall'input corrente
     * @param {string} className - Classe da rimuovere
     */
    removeClass(className) {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        input.classList.remove(className);
    }
}

// Creiamo un'istanza del gestore input quando il DOM è pronto
let chatInput;
document.addEventListener("DOMContentLoaded", () => {
    try {
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
    } catch (error) {
        console.error("Error initializing chat input:", error);
    }
});

export { chatInput };