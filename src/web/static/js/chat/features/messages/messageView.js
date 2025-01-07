import { MessageType } from "./messageTypes.js";
import { chatDomService } from "../../utils/chatDom.js";
import { CSS_CLASSES } from "../../config/constants.js";
import { feedbackView } from "../feedback/feedbackView.js";
import { chatViewManager } from "../../utils/chatViewManager.js";

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

        // Stato interno del loading e della vista
        this.isLoading = false;
        this.isFirstMessage = true;
    }

    /**
     * Renderizza un nuovo messaggio con animazione
     * @param {Object} message - Messaggio da renderizzare
     * @returns {HTMLElement} Elemento messaggio renderizzato
     */
    renderMessage(message) {
        // Se è il primo messaggio, gestiamo la transizione
        if (this.isFirstMessage && message.type === MessageType.USER) {
            this.isFirstMessage = false;
            this.container.innerHTML = ''; // Rimuoviamo tutto il contenuto precedente
        }

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
                // Non renderizziamo più i messaggi di sistema nella chat view
                if (this.isFirstMessage) {
                    return null;
                }
                messageElement = this.renderSystemMessage(message);
                break;
            default:
                console.error("Unknown message type:", message.type);
                return null;
        }

        // Aggiungiamo la classe per l'animazione
        messageElement.classList.add('message-appear');
        
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

        // Crea la query SQL con feedback se presente
        if (message.content.query) {
            const queryContainer = chatDomService.createQueryContainer({
                query: message.content.query,
                original_question: message.content.original_question,
                explanation: message.content.explanation
            });
            
            // Non aggiungiamo più il feedback button qui, viene gestito da chatDomService
            contentDiv.appendChild(queryContainer);
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
     * Renderizza un messaggio di errore con animazione
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
     * Renderizza un messaggio di sistema (usato principalmente per notifiche in-chat)
     * @param {Object} message - Messaggio sistema
     * @returns {HTMLElement} Elemento messaggio
     * @private
     */
    renderSystemMessage(message) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${CSS_CLASSES.MESSAGE.BOT} system-message`;

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
        // Se siamo nella welcome view e non ci sono messaggi, non facciamo nulla
        if (chatViewManager.currentView === 'welcome' && messages.length === 0) {
            return;
        }

        this.clearMessages();
        messages.forEach((message) => this.renderMessage(message));
    }

    /**
     * Mostra l'indicatore di caricamento con animazione
     */
    showLoading() {
        if (!this.isLoading) {
            this.loadingIndicator = chatDomService.addLoadingIndicator();
            this.loadingIndicator.classList.add('typing-appear');
            this.isLoading = true;
        }
    }

    /**
     * Nasconde l'indicatore di caricamento con fade out
     */
    hideLoading() {
        if (this.isLoading && this.loadingIndicator) {
            this.loadingIndicator.classList.add('fade-out');
            setTimeout(() => {
                chatDomService.removeLoadingIndicator();
                this.isLoading = false;
            }, 300); // Tempo dell'animazione
        }
    }

    /**
     * Pulisce tutti i messaggi dal contenitore
     */
    clearMessages() {
        // Se siamo nella welcome view, non puliamo nulla
        if (chatViewManager.currentView === 'welcome') {
            return;
        }

        const loadingIndicator = this.container.querySelector(
            `.${CSS_CLASSES.LOADING.CONTAINER}`
        );

        this.container.innerHTML = "";

        if (loadingIndicator) {
            this.container.appendChild(loadingIndicator);
        }
    }

    /**
     * Scorre la chat fino all'ultimo messaggio con animazione smooth
     */
    scrollToBottom() {
        this.container.scrollTo({
            top: this.container.scrollHeight,
            behavior: 'smooth'
        });
    }

    /**
     * Resetta lo stato della vista
     */
    reset() {
        this.isFirstMessage = true;
        this.clearMessages();
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