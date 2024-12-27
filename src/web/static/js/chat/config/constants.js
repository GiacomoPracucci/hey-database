/**
 * Configurazione delle costanti per il modulo chat
 * Questo modulo contiene tutte le costanti utilizzate nell'applicazione chat,
 * organizzate per categoria e scopo
 */

/**
 * Costanti per lo storage locale
 * Definisce le chiavi utilizzate per il localStorage
 */
export const STORAGE = {
  CHAT_MESSAGES: "chat_messages", // Chiave per i messaggi salvati
  SETTINGS: "chat_settings", // Chiave per le impostazioni utente
};

/**
 * Costanti per le API endpoints
 * Definisce i percorsi delle API utilizzate dalla chat
 */
export const API = {
  CHAT: "/chat/api/chat", // Endpoint per l'invio dei messaggi
  FEEDBACK: "/chat/api/feedback", // Endpoint per l'invio del feedback
};

/**
 * Configurazione dei delays e timeouts
 * Definisce i tempi di attesa per varie operazioni
 */
export const TIMING = {
  DEBOUNCE_DELAY: 300, // Delay per il debounce dell'input (ms)
  TOAST_DURATION: 3000, // Durata di visualizzazione dei toast (ms)
  COPY_FEEDBACK: 2000, // Durata del feedback di copia (ms)
  TYPING_DELAY: 2000, // Delay simulazione digitazione per risposte cache (ms)
};

/**
 * Classi CSS utilizzate dinamicamente
 * Definisce le classi CSS usate per manipolare l'interfaccia
 */
export const CSS_CLASSES = {
  // Classi per i messaggi
  MESSAGE: {
    CONTAINER: "message",
    USER: "user",
    BOT: "bot",
    WELCOME: "welcome",
    CONTENT: "message-content",
  },
  // Classi per gli stati di loading
  LOADING: {
    CONTAINER: "typing-indicator-container",
    INDICATOR: "typing-indicator",
  },
  // Classi per i feedback
  FEEDBACK: {
    BUTTON: "feedback-button",
    VOTED: "voted",
  },
  // Classi per la query SQL
  SQL: {
    CONTAINER: "sql-query-container",
    QUERY: "sql-query",
    TOOLBAR: "sql-query-toolbar",
    LABEL: "sql-label",
  },
  // Classi per gli errori
  ERROR: {
    CONTAINER: "error-container",
    MESSAGE: "error-message",
    DETAILS: "error-details",
    QUERY: "error-query",
  },
};

/**
 * Configurazione dei messaggi di errore
 * Definisce i messaggi di errore standard
 */
export const ERROR_MESSAGES = {
  COMMUNICATION: "Errore di comunicazione con il server",
  MISSING_DATA: "Dati mancanti nella richiesta",
  VECTOR_STORE: "Please, enable vectorstore in config.yaml to use this feature",
  GENERIC: "Si è verificato un errore",
};

/**
 * Configurazione delle icone
 * Definisce le classi Font Awesome per le icone utilizzate
 */
export const ICONS = {
  COPY: "fa-copy",
  CHECK: "fa-check",
  TIMES: "fa-times",
  THUMBS_UP: "fa-thumbs-up",
  PAPER_PLANE: "fa-paper-plane",
  ERROR: "fa-exclamation-triangle",
};

/**
 * Configurazione degli stati dei messaggi
 * Definisce gli stati possibili per i messaggi
 */
export const MESSAGE_STATES = {
  SENDING: "sending",
  SENT: "sent",
  ERROR: "error",
  LOADING: "loading",
};

/**
 * Configurazione dei tipi di notifica
 * Definisce i tipi di notifiche toast disponibili
 */
export const NOTIFICATION_TYPES = {
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
};

/**
 * Configurazione dei testi predefiniti
 * Definisce i testi statici utilizzati nell'interfaccia
 */
export const UI_TEXTS = {
  COPY_BUTTON: "Copia query",
  COPIED: "Copiato!",
  COPY_ERROR: "Errore nella copia",
  FEEDBACK_BUTTON: "Mark as correct answer",
  FEEDBACK_THANKS: "Thank you for your feedback!",
  LOADING: "Loading...",
};

/**
 * Configurazione degli elementi DOM
 * Definisce gli ID degli elementi DOM principali
 */
export const DOM_ELEMENTS = {
  CHAT_MESSAGES: "chatMessages",
  USER_INPUT: "userInput",
  SEND_BUTTON: "sendButton",
  TYPING_INDICATOR: "typingIndicator",
  CLEAR_BUTTON: "clearChat",
};
