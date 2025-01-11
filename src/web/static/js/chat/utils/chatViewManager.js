import { CSS_CLASSES, DOM_ELEMENTS } from "../config/constants.js";

/**
 * Gestisce le diverse viste della chat e le transizioni tra di esse.
 * Si occupa di tutta la gestione degli stati dell'interfaccia e delle transizioni.
 */
export class ChatViewManager {
    /**
     * Inizializza il gestore delle viste
     */
    constructor() {
        this.initializeElements();
        this.currentView = 'welcome';
        this.isInputEnabled = true;
    }

    /**
     * Inizializza i riferimenti agli elementi DOM necessari
     * @private
     * @throws {Error} Se mancano elementi essenziali
     */
    initializeElements() {
        // Views
        this.welcomeView = document.getElementById(DOM_ELEMENTS.WELCOME_VIEW);
        this.chatView = document.getElementById(DOM_ELEMENTS.CHAT_VIEW);

        // Input elements
        this.welcomeInput = document.getElementById(DOM_ELEMENTS.WELCOME_INPUT);
        this.chatInput = document.getElementById(DOM_ELEMENTS.CHAT_INPUT);

        // Buttons
        this.welcomeSendButton = document.getElementById(DOM_ELEMENTS.WELCOME_SEND_BUTTON);
        this.chatSendButton = document.getElementById(DOM_ELEMENTS.CHAT_SEND_BUTTON);

        // Validation
        this.validateElements();

        // Initialize input handlers
        this.initializeInputHandlers();
    }

    /**
     * Valida la presenza di tutti gli elementi necessari
     * @private
     * @throws {Error} Se mancano elementi essenziali
     */
    validateElements() {
        const requiredElements = {
            welcomeView: this.welcomeView,
            chatView: this.chatView,
            welcomeInput: this.welcomeInput,
            chatInput: this.chatInput,
            welcomeSendButton: this.welcomeSendButton,
            chatSendButton: this.chatSendButton
        };

        for (const [name, element] of Object.entries(requiredElements)) {
            if (!element) {
                throw new Error(`Required element '${name}' not found`);
            }
        }
    }

    /**
     * Inizializza gli handler per gli input
     * @private
     */
    initializeInputHandlers() {
        // Input resize handlers
        [this.welcomeInput, this.chatInput].forEach(input => {
            input.addEventListener('input', () => {
                this.autoResizeInput(input);
                this.updateButtonState(input === this.welcomeInput);
            });
        });

        // Welcome input specific handlers
        this.welcomeInput.addEventListener('paste', () => {
            setTimeout(() => this.autoResizeInput(this.welcomeInput), 0);
        });

        // Chat input specific handlers
        this.chatInput.addEventListener('paste', () => {
            setTimeout(() => this.autoResizeInput(this.chatInput), 0);
        });
    }

    /**
     * Esegue la transizione alla vista chat
     * @returns {Promise<void>}
     */
    async transitionToChatView() {
        if (this.currentView === 'chat') return;
    
        // Fade out welcome view
        this.welcomeView.classList.add(CSS_CLASSES.VIEW.FADE_OUT);
        await this.waitForAnimation(300);
    
        // Hide welcome and show chat
        this.welcomeView.classList.add(CSS_CLASSES.VIEW.HIDDEN);
        this.chatView.classList.remove(CSS_CLASSES.VIEW.HIDDEN);
        
        // Trigger reflow
        void this.chatView.offsetWidth;
        
        // Fade in chat view
        this.chatView.classList.add(CSS_CLASSES.VIEW.VISIBLE);
        
        // Show clear button with animation
        this.toggleClearButton(true);
        
        this.currentView = 'chat';
        this.chatInput.focus();
    }

    toggleClearButton(show, animate = true) {
        const clearButton = document.getElementById(DOM_ELEMENTS.CLEAR_BUTTON);
        if (!clearButton) return;
    
        if (show) {
            // Invece di impostare display: flex direttamente, aggiungiamo una classe CSS
            clearButton.classList.add('visible');
            if (animate) {
                clearButton.style.opacity = '0';
                requestAnimationFrame(() => {
                    clearButton.style.opacity = '1';
                });
            } else {
                clearButton.style.opacity = '1';
            }
        } else {
            if (animate) {
                clearButton.style.opacity = '0';
                setTimeout(() => {
                    clearButton.classList.remove('visible');
                }, 300);
            } else {
                clearButton.classList.remove('visible');
                clearButton.style.opacity = '0';
            }
        }
    }

    /**
     * Utility per attendere il completamento delle animazioni
     * @private
     * @param {number} ms - Millisecondi da attendere
     * @returns {Promise<void>}
     */
    waitForAnimation(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Aggiorna lo stato del pulsante di invio
     * @param {boolean} isWelcomeView - Se true, aggiorna il pulsante della welcome view
     * @private
     */
    updateButtonState(isWelcomeView = true) {
        const input = isWelcomeView ? this.welcomeInput : this.chatInput;
        const button = isWelcomeView ? this.welcomeSendButton : this.chatSendButton;
        
        if (button) {
            const isEmpty = !input.value.trim();
            button.disabled = isEmpty || !this.isInputEnabled;
        }
    }

    /**
     * Adatta l'altezza dell'input al contenuto
     * @param {HTMLTextAreaElement} input - Input da ridimensionare
     * @private
     */
    autoResizeInput(input) {
        if (!input) return;
        
        input.style.height = 'auto';
        input.style.height = `${input.scrollHeight}px`;
    }

    /**
     * Ottiene il valore dell'input corrente
     * @returns {string} Il valore dell'input corrente
     */
    getCurrentInput() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        return input ? input.value : '';
    }

    /**
     * Pulisce l'input corrente
     */
    clearCurrentInput() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        if (input) {
            input.value = '';
            this.autoResizeInput(input);
            this.updateButtonState(this.currentView === 'welcome');
        }
    }

    /**
     * Imposta il focus sull'input corrente
     */
    focusCurrentInput() {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        if (input && !input.disabled) {
            input.focus();
        }
    }

    /**
     * Imposta lo stato di abilitazione dell'interfaccia
     * @param {boolean} disabled - Se true, disabilita l'interfaccia
     */
    setInterfaceState(disabled) {
        this.isInputEnabled = !disabled;

        // Disable/enable inputs
        [this.welcomeInput, this.chatInput].forEach(input => {
            if (input) {
                input.disabled = disabled;
            }
        });

        // Update button states
        this.updateButtonState(this.currentView === 'welcome');
    }

    /**
     * Gestisce il resize della finestra
     */
    handleResize() {
        // Riadatta l'altezza degli input
        [this.welcomeInput, this.chatInput].forEach(input => {
            if (input) {
                this.autoResizeInput(input);
            }
        });
    }

    /**
     * Aggiunge una classe CSS all'input corrente
     * @param {string} className - Nome della classe da aggiungere
     */
    addInputClass(className) {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        if (input) {
            input.classList.add(className);
        }
    }

    /**
     * Rimuove una classe CSS dall'input corrente
     * @param {string} className - Nome della classe da rimuovere
     */
    removeInputClass(className) {
        const input = this.currentView === 'welcome' ? this.welcomeInput : this.chatInput;
        if (input) {
            input.classList.remove(className);
        }
    }

    /**
     * Verifica se l'input corrente è vuoto
     * @returns {boolean} true se l'input è vuoto
     */
    isCurrentInputEmpty() {
        return !this.getCurrentInput().trim();
    }
}

// Creiamo un'istanza singola del manager per l'applicazione
export const chatViewManager = new ChatViewManager();