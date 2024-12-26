/**
 * TypingIndicator Web Component
 *
 * Componente che mostra un indicatore di caricamento/digitazione animato.
 * Può essere utilizzato per indicare che il sistema sta elaborando una richiesta
 * o generando una risposta.
 *
 * Attributes:
 * - text: (opzionale) testo da mostrare accanto all'indicatore
 * - container-class: (opzionale) classe CSS da applicare al container
 *
 * Events:
 * Questo componente non emette eventi.
 *
 * Usage:
 * <typing-indicator text="Loading..."></typing-indicator>
 *
 * // O senza testo:
 * <typing-indicator></typing-indicator>
 */
class TypingIndicator extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  /**
   * Lifecycle callback chiamato quando il componente viene aggiunto al DOM
   */
  connectedCallback() {
    this.render();
  }

  /**
   * Definisce gli attributi che devono essere osservati per cambiamenti
   */
  static get observedAttributes() {
    return ["text", "container-class"];
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
   * Renderizza il componente
   */
  render() {
    // Ottiene il testo e la classe del container dagli attributi
    const text = this.getAttribute("text");
    const containerClass = this.getAttribute("container-class");

    this.shadowRoot.innerHTML = `
          <style>
              :host {
                  display: inline-block;
              }
              
              /* Container principale che riutilizza le variabili CSS esistenti */
              .typing-indicator-container {
                  display: flex;
                  justify-content: flex-start;
                  margin: 0.5rem 0;
              }
              
              .typing-indicator {
                  display: inline-flex;
                  align-items: center;
                  gap: var(--layout-spacing-sm, 0.5rem);
                  padding: 0.75rem 1.25rem;
                  background-color: var(--typing-indicator-bg);
                  border-radius: 16px;
                  box-shadow: var(--shadow-sm);
              }

              /* Punti animati che utilizzano le variabili CSS dell'app */
              .dot {
                  width: var(--typing-dot-size);
                  height: var(--typing-dot-size);
                  background-color: var(--typing-dot-color);
                  border-radius: 50%;
                  opacity: 0.6;
                  animation: bounce 1.4s infinite ease-in-out;
              }

              .dot:nth-child(1) { animation-delay: -0.32s; }
              .dot:nth-child(2) { animation-delay: -0.16s; }

              @keyframes bounce {
                  0%, 80%, 100% { 
                      transform: translateY(0); 
                  }
                  40% { 
                      transform: translateY(-6px); 
                  }
              }

              /* Testo di caricamento che utilizza le variabili CSS dell'app */
              .loading-text {
                  margin-left: var(--layout-spacing-sm, 0.5rem);
                  font-size: 0.875rem;
                  color: var(--text-muted);
              }
          </style>

          <div class="typing-indicator-container ${containerClass || ""}">
              <div class="typing-indicator">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                  ${
                    text
                      ? `
                      <span class="loading-text">${text}</span>
                  `
                      : ""
                  }
              </div>
          </div>
      `;
  }
}

// Registra il componente
customElements.define("typing-indicator", TypingIndicator);
