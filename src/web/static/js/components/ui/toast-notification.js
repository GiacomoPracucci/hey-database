/**
 * ToastNotification Web Component
 *
 * Componente per mostrare notifiche temporanee all'utente.
 * Supporta diversi tipi di notifiche (success, error, warning, info)
 * e si auto-distrugge dopo un tempo configurabile.
 *
 * Attributes:
 * - type: tipo di notifica ('success', 'error', 'warning', 'info')
 * - message: messaggio da visualizzare
 * - duration: durata in millisecondi (default: 3000)
 * - position: posizione del toast ('top', 'bottom') (default: 'top')
 *
 * Events:
 * - dismiss: emesso quando il toast viene chiuso
 * - show: emesso quando il toast viene mostrato
 *
 * Usage:
 * <toast-notification
 *   type="success"
 *   message="Operazione completata"
 *   duration="3000">
 * </toast-notification>
 */
class ToastNotification extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  /**
   * Lifecycle callback chiamato quando il componente viene aggiunto al DOM
   */
  connectedCallback() {
    this.render();
    this.setupAutoDismiss();
    this.dispatchEvent(
      new CustomEvent("show", {
        bubbles: true,
        composed: true,
      })
    );
  }

  /**
   * Definisce gli attributi che devono essere osservati per cambiamenti
   */
  static get observedAttributes() {
    return ["type", "message", "duration", "position"];
  }

  /**
   * Lifecycle callback chiamato quando gli attributi osservati cambiano
   */
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  /**
   * Configura l'auto-dismissione del toast
   */
  setupAutoDismiss() {
    const duration = parseInt(this.getAttribute("duration")) || 3000;
    setTimeout(() => {
      this.dismiss();
    }, duration);
  }

  /**
   * Chiude il toast e rimuove l'elemento dal DOM
   */
  dismiss() {
    this.dispatchEvent(
      new CustomEvent("dismiss", {
        bubbles: true,
        composed: true,
      })
    );
    this.remove();
  }

  /**
   * Restituisce l'icona appropriata per il tipo di notifica
   */
  getIconForType(type) {
    const icons = {
      success: '<i class="fas fa-check"></i>',
      error: '<i class="fas fa-times"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      info: '<i class="fas fa-info-circle"></i>',
    };
    return icons[type] || icons.info;
  }

  /**
   * Renderizza il componente
   */
  render() {
    const type = this.getAttribute("type") || "info";
    const message = this.getAttribute("message") || "";
    const position = this.getAttribute("position") || "top";
    const icon = this.getIconForType(type);

    this.shadowRoot.innerHTML = `
          <style>
              :host {
                  position: fixed;
                  left: 50%;
                  transform: translateX(-50%);
                  z-index: var(--toast-z-index);
                  pointer-events: none;
              }

              :host([position="top"]) {
                  top: var(--toast-spacing);
              }

              :host([position="bottom"]) {
                  bottom: var(--toast-spacing);
              }

              .toast {
                  display: flex;
                  align-items: center;
                  gap: var(--layout-spacing-md);
                  padding: var(--layout-spacing-lg) var(--layout-spacing-xl);
                  min-width: var(--toast-min-width);
                  border-radius: var(--toast-border-radius);
                  box-shadow: var(--toast-shadow);
                  pointer-events: all;
                  animation: slideIn 0.3s ease forwards;
                  font-size: var(--toast-font-size);
              }

              .toast.success {
                  background-color: var(--toast-success-bg);
                  color: var(--text-light);
              }

              .toast.error {
                  background-color: var(--toast-error-bg);
                  color: var(--text-light);
              }

              .toast.warning {
                  background-color: var(--toast-warning-bg);
                  color: var(--toast-warning-color);
              }

              .toast.info {
                  background-color: var(--brand-secondary);
                  color: var(--text-light);
              }

              i {
                  font-size: var(--toast-icon-size);
              }

              @keyframes slideIn {
                  from {
                      transform: translate(-50%, ${
                        position === "top" ? "-100%" : "100%"
                      });
                      opacity: 0;
                  }
                  to {
                      transform: translate(-50%, 0);
                      opacity: 1;
                  }
              }
          </style>

          <div class="toast ${type}">
              ${icon}
              ${message}
          </div>
      `;
  }
}

// Registra il componente
customElements.define("toast-notification", ToastNotification);
