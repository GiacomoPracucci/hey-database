import { messageStore } from "./features/messages/messageStore.js";
import { messageView } from "./features/messages/messageView.js";
import { feedbackView } from "./features/feedback/feedbackView.js";
import { feedbackApiService } from "./features/feedback/feedbackApi.js";
import { chatApiService } from "./utils/chatApi.js";
import { chatDomService } from "./utils/chatDom.js";
import { chatNotificationService } from "./utils/chatNotifications.js";
import { chatViewManager } from "./utils/chatViewManager.js";
import { DOM_ELEMENTS } from "./config/constants.js";

class ChatApplication {
    constructor() {
        this.validateServices();
        this.initializeEventListeners();
        this.initializeChatHistory();
        this.isSending = false;
    }

    validateServices() {
        const requiredServices = {
            messageStore,
            messageView,
            feedbackApiService,
            chatApiService,
            chatDomService,
            chatNotificationService,
            chatViewManager
        };

        for (const [name, service] of Object.entries(requiredServices)) {
            if (!service) {
                throw new Error(`Required service ${name} is not available`);
            }
        }
    }

    initializeEventListeners() {
        // Clear button
        const clearButton = document.querySelector(`#${DOM_ELEMENTS.CLEAR_BUTTON}`);
        if (clearButton) {
            clearButton.addEventListener("click", (e) => this.handleClearChat(e));
        }

        // Store updates
        messageStore.subscribe((messages) => {
            messageView.updateView(messages);
        });

        // Welcome Input Events
        this.initializeWelcomeInputHandlers();

        // Chat Input Events
        this.initializeChatInputHandlers();

        // Suggestion Buttons
        this.initializeSuggestionButtons();

        // Page unload
        window.addEventListener("beforeunload", () => this.handlePageUnload());
    }

    initializeWelcomeInputHandlers() {
        const welcomeInput = document.getElementById(DOM_ELEMENTS.WELCOME_INPUT);
        const welcomeSendButton = document.getElementById(DOM_ELEMENTS.WELCOME_SEND_BUTTON);

        if (welcomeInput && welcomeSendButton) {
            welcomeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = welcomeInput.value.trim();
                    if (message) {
                        this.handleInitialMessage(message);
                    }
                }
            });

            welcomeSendButton.addEventListener('click', () => {
                const message = welcomeInput.value.trim();
                if (message) {
                    this.handleInitialMessage(message);
                }
            });
        }
    }

    initializeChatInputHandlers() {
        const chatInput = document.getElementById(DOM_ELEMENTS.CHAT_INPUT);
        const chatSendButton = document.getElementById(DOM_ELEMENTS.CHAT_SEND_BUTTON);

        if (chatInput && chatSendButton) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = chatInput.value.trim();
                    if (message) {
                        this.handleMessageSubmit(message);
                    }
                }
            });

            chatSendButton.addEventListener('click', () => {
                const message = chatInput.value.trim();
                if (message) {
                    this.handleMessageSubmit(message);
                }
            });
        }
    }

    initializeSuggestionButtons() {
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                if (query) {
                    this.handleInitialMessage(query);
                }
            });
        });
    }

    /**
     * Gestisce il messaggio iniziale e la transizione
     * @param {string} message - Messaggio da inviare
     * @private
     */
    async handleInitialMessage(message) {
        if (this.isSending) return;

        try {
            this.isSending = true;
            this.disableInterface();

            // Prima esegui la transizione
            await chatViewManager.transitionToChatView();
            
            // Aggiungi una piccola pausa per permettere alla transizione di completarsi
            await new Promise(resolve => setTimeout(resolve, 300));

            // Poi aggiungi il messaggio utente e mostralo
            messageStore.addUserMessage(message);
            messageView.showLoading();

            // Invia il messaggio al server
            const response = await chatApiService.sendMessage(message);

            // Gestisci la risposta
            if (!response.success) {
                messageStore.addErrorMessage({
                    error: response.error || "Unknown error",
                    query: response.query
                });
            } else {
                messageStore.addBotResponse(response);
            }

        } catch (error) {
            console.error("Error handling initial message:", error);
            messageStore.addErrorMessage({
                error: error.message
            });
            chatNotificationService.showError("Error sending message");
        } finally {
            messageView.hideLoading();
            this.enableInterface();
            this.isSending = false;
            chatViewManager.clearCurrentInput();
            chatViewManager.focusCurrentInput();
        }
    }

    async handleMessageSubmit(message) {
        if (this.isSending) return;

        try {
            this.isSending = true;
            this.disableInterface();

            // Aggiungi il messaggio utente
            messageStore.addUserMessage(message);
            messageView.showLoading();

            const response = await chatApiService.sendMessage(message);

            if (!response.success) {
                messageStore.addErrorMessage({
                    error: response.error || "Unknown error",
                    query: response.query
                });
            } else {
                messageStore.addBotResponse(response);
            }
        } catch (error) {
            console.error("Error sending message:", error);
            messageStore.addErrorMessage({
                error: error.message
            });
        } finally {
            messageView.hideLoading();
            this.enableInterface();
            this.isSending = false;
            chatViewManager.clearCurrentInput();
            chatViewManager.focusCurrentInput();
        }
    }

    handleClearChat(event) {
        event.preventDefault();
        const button = event.target;
        button.disabled = true;

        try {
            messageStore.clearMessages();
            chatViewManager.clearCurrentInput();
            chatNotificationService.showSuccess("Chat cleared successfully");
        } catch (error) {
            console.error("Error clearing chat:", error);
            chatNotificationService.showError("Error clearing chat");
        } finally {
            setTimeout(() => {
                button.disabled = false;
            }, 500);
        }
    }

    handlePageUnload() {
        if (messageStore.messages && messageStore.messages.length > 0) {
            messageStore.saveMessages();
        }
    }

    /**
     * Disabilita l'interfaccia durante l'elaborazione
     * @private
     */
    disableInterface() {
        chatViewManager.setInterfaceState(true);
        if (feedbackView) {
            try {
                feedbackView.setInterfaceState(true);
            } catch (error) {
                console.warn('Error disabling feedback interface:', error);
            }
        }
    }

    /**
     * Riabilita l'interfaccia dopo l'elaborazione
     * @private
     */
    enableInterface() {
        chatViewManager.setInterfaceState(false);
        if (feedbackView) {
            try {
                feedbackView.setInterfaceState(false);
            } catch (error) {
                console.warn('Error enabling feedback interface:', error);
            }
        }
    }

    initializeChatHistory() {
        try {
            if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
                messageStore.clearMessages();
            } else {
                const messages = messageStore.loadMessages();
                
                if (messages && messages.length > 0) {
                    // Nascondiamo immediatamente la welcome view
                    const welcomeView = document.getElementById(DOM_ELEMENTS.WELCOME_VIEW);
                    const chatView = document.getElementById(DOM_ELEMENTS.CHAT_VIEW);
                    
                    if (welcomeView && chatView) {
                        welcomeView.style.display = 'none';
                        chatView.classList.remove('hidden');
                        chatView.classList.add('visible');
                    }
                }
            }
        } catch (error) {
            console.error("Error initializing chat history:", error);
            chatNotificationService.showError("Error loading chat history");
        }
    }
}

// Initialize the application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    try {
        window.chatApp = new ChatApplication();
    } catch (error) {
        console.error("Error initializing chat application:", error);
        chatNotificationService.showError("Error initializing chat application");
    }
});