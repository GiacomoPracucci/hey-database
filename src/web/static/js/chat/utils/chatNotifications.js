import { NOTIFICATION_TYPES, TIMING, ICONS } from "../config/constants.js";

/**
 * ChatNotificationService gestisce il sistema di notifiche toast dell'applicazione.
 * Fornisce un'interfaccia per mostrare notifiche temporanee all'utente.
 */
export class ChatNotificationService {
  /**
   * Inizializza il servizio di notifiche
   */
  constructor() {
    // Tiene traccia delle notifiche attive
    this.activeToasts = new Set();
    // Contatore per gli ID univoci dei toast
    this.toastCounter = 0;
  }

  /**
   * Mostra una notifica toast
   * @param {string} type - Tipo di notifica ('success', 'error', 'warning')
   * @param {string} message - Messaggio da mostrare
   * @param {string} [icon] - Classe dell'icona FontAwesome (opzionale)
   * @returns {string} ID univoco del toast creato
   */
  show(type, message, icon = null) {
    // Rimuove eventuali toast esistenti
    this.removeAllToasts();

    // Crea il nuovo toast
    const toast = this.createToastElement(type, message, icon);
    const toastId = `toast-${++this.toastCounter}`;
    toast.id = toastId;

    // Aggiunge il toast al DOM
    document.body.appendChild(toast);
    this.activeToasts.add(toastId);

    // Imposta il timer per la rimozione automatica
    setTimeout(() => {
      this.removeToast(toastId);
    }, TIMING.TOAST_DURATION);

    return toastId;
  }

  /**
   * Crea l'elemento DOM del toast
   * @param {string} type - Tipo di notifica
   * @param {string} message - Messaggio da mostrare
   * @param {string} icon - Classe dell'icona
   * @returns {HTMLElement} Elemento toast creato
   * @private
   */
  createToastElement(type, message, icon) {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let iconHtml = "";
    if (icon) {
      iconHtml = `<i class="fas ${icon}"></i>`;
    }

    toast.innerHTML = `${iconHtml}${message}`;

    return toast;
  }

  /**
   * Rimuove un toast specifico
   * @param {string} toastId - ID del toast da rimuovere
   */
  removeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
      // Aggiungiamo una classe per l'animazione di uscita
      toast.classList.add("toast-fade-out");

      // Rimuoviamo l'elemento dopo l'animazione
      setTimeout(() => {
        toast.remove();
        this.activeToasts.delete(toastId);
      }, 300); // Durata dell'animazione
    }
  }

  /**
   * Rimuove tutti i toast attivi
   */
  removeAllToasts() {
    const existingToasts = document.querySelectorAll(".toast");
    existingToasts.forEach((toast) => {
      if (toast.id) {
        this.removeToast(toast.id);
      } else {
        toast.remove();
      }
    });
    this.activeToasts.clear();
  }

  /**
   * Mostra una notifica di successo
   * @param {string} message - Messaggio di successo
   */
  showSuccess(message) {
    this.show(NOTIFICATION_TYPES.SUCCESS, message, ICONS.CHECK);
  }

  /**
   * Mostra una notifica di errore
   * @param {string} message - Messaggio di errore
   */
  showError(message) {
    this.show(NOTIFICATION_TYPES.ERROR, message, ICONS.TIMES);
  }

  /**
   * Mostra una notifica di avvertimento
   * @param {string} message - Messaggio di avvertimento
   */
  showWarning(message) {
    this.show(NOTIFICATION_TYPES.WARNING, message, ICONS.ERROR);
  }

  /**
   * Verifica se ci sono toast attivi
   * @returns {boolean} true se ci sono toast attivi
   */
  hasActiveToasts() {
    return this.activeToasts.size > 0;
  }

  /**
   * Aggiorna la posizione dei toast attivi
   * Utile quando cambiano le dimensioni della finestra
   */
  updateToastPositions() {
    const toasts = document.querySelectorAll(".toast");
    let offset = 20; // Margine iniziale dal top

    toasts.forEach((toast) => {
      toast.style.top = `${offset}px`;
      offset += toast.offsetHeight + 10; // 10px di spazio tra i toast
    });
  }
}

// Aggiungiamo il CSS necessario dinamicamente
const style = document.createElement("style");
style.textContent = `
    .toast {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        color: #ffffff;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        animation: slideDown 0.3s ease;
    }

    .toast.success {
        background-color: var(--success-base);
    }

    .toast.error {
        background-color: var(--error-base);
    }

    .toast.warning {
        background-color: var(--warning-light);
        color: var(--text-primary);
    }

    .toast i {
        font-size: 16px;
    }

    .toast-fade-out {
        animation: fadeOut 0.3s ease forwards;
    }

    @keyframes slideDown {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }

    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translate(-50%, 0);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
    }
`;
document.head.appendChild(style);

// Creiamo un'istanza singola del servizio per l'applicazione
export const chatNotificationService = new ChatNotificationService();
