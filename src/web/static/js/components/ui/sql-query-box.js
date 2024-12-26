/**
 * SqlQueryBox Web Component
 *
 * Questo componente visualizza una query SQL con funzionalità di copia e feedback.
 * Include una toolbar con pulsanti per le azioni e supporta la formattazione del codice SQL.
 *
 * Attributes:
 * - query: la query SQL da visualizzare
 * - original-question: la domanda originale che ha generato la query
 * - explanation: la spiegazione della query
 * - show-feedback: (opzionale) se mostrare o meno il pulsante di feedback
 *
 * Events:
 * - copyQuery: emesso quando la query viene copiata
 * - feedback: emesso quando viene dato feedback positivo
 *
 * Usage:
 * <sql-query-box
 *   query="SELECT * FROM users"
 *   explanation="Questa query seleziona tutti gli utenti"
 *   show-feedback="true">
 * </sql-query-box>
 */
class SqlQueryBox extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.handleCopy = this.handleCopy.bind(this);
    this.handleFeedback = this.handleFeedback.bind(this);
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  static get observedAttributes() {
    return ["query", "original-question", "explanation", "show-feedback"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  setupEventListeners() {
    const copyButton = this.shadowRoot.querySelector(".copy-button");
    const feedbackButton = this.shadowRoot.querySelector(".feedback-button");

    if (copyButton) {
      copyButton.addEventListener("click", this.handleCopy);
    }

    if (feedbackButton) {
      feedbackButton.addEventListener("click", this.handleFeedback);
    }
  }

  async handleCopy() {
    const query = this.getAttribute("query");
    try {
      await navigator.clipboard.writeText(query);
      this.updateCopyButton(true);

      this.dispatchEvent(
        new CustomEvent("copyQuery", {
          detail: { query },
          bubbles: true,
          composed: true,
        })
      );
    } catch (err) {
      console.error("Errore durante la copia:", err);
      this.updateCopyButton(false);
    }
  }

  updateCopyButton(success) {
    const copyButton = this.shadowRoot.querySelector(".copy-button");
    const icon = success ? "fa-check" : "fa-times";
    copyButton.innerHTML = `<i class="fas ${icon}"></i>`;
    copyButton.classList.toggle("copied", success);

    setTimeout(() => {
      copyButton.innerHTML = '<i class="fas fa-copy"></i>';
      copyButton.classList.remove("copied");
    }, 2000);
  }

  handleFeedback() {
    const feedbackButton = this.shadowRoot.querySelector(".feedback-button");
    feedbackButton.classList.add("voted");
    feedbackButton.disabled = true;

    this.dispatchEvent(
      new CustomEvent("feedback", {
        detail: {
          query: this.getAttribute("query"),
          originalQuestion: this.getAttribute("original-question"),
          explanation: this.getAttribute("explanation"),
        },
        bubbles: true,
        composed: true,
      })
    );
  }

  render() {
    this.shadowRoot.innerHTML = `
          <style>
              :host {
                  display: block;
                  margin: var(--layout-spacing-md) 0;
              }

              .sql-query-container {
                  background-color: var(--sql-box-bg);
                  border-radius: var(--btn-border-radius);
                  overflow: hidden;
                  position: relative;
                  margin: 0.5rem 0;
              }

              .sql-query-toolbar {
                  display: flex;
                  justify-content: flex-end;
                  gap: var(--layout-spacing-sm);
                  padding: var(--layout-spacing-sm);
                  background-color: var(--sql-box-toolbar-bg);
                  min-height: 2.5rem;
              }

              .toolbar-button {
                  background: none;
                  border: none;
                  color: var(--sql-button-color);
                  cursor: pointer;
                  padding: var(--layout-spacing-xs) var(--layout-spacing-sm);
                  border-radius: var(--btn-border-radius);
                  transition: all var(--transition-fast);
                  opacity: 0.7;
              }

              .toolbar-button:hover {
                  opacity: 1;
                  background-color: var(--sql-button-hover-bg);
              }

              .toolbar-button.copied {
                  color: var(--success-base);
              }

              .toolbar-button.voted {
                  color: var(--success-base);
                  cursor: default;
              }

              .sql-query {
                  padding: var(--layout-spacing-lg);
                  margin: 0;
                  color: var(--sql-text-color);
                  font-family: 'JetBrains Mono', monospace;
                  font-size: 0.9rem;
                  white-space: pre-wrap;
              }

              .sql-label {
                  position: absolute;
                  top: var(--layout-spacing-sm);
                  left: var(--layout-spacing-lg);
                  color: var(--sql-label-color);
                  font-size: 0.8rem;
                  font-weight: 500;
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
              }

              .explanation {
                  margin: var(--layout-spacing-md) 0;
                  color: var(--text-secondary);
                  font-style: italic;
              }
          </style>

          <div class="sql-query-container">
              <span class="sql-label">SQL</span>
              <div class="sql-query-toolbar">
                  <button class="toolbar-button copy-button" title="Copia query">
                      <i class="fas fa-copy"></i>
                  </button>
                  ${
                    this.getAttribute("show-feedback") !== "false"
                      ? `
                      <button class="toolbar-button feedback-button" title="Segna come corretta">
                          <i class="fas fa-thumbs-up"></i>
                      </button>
                  `
                      : ""
                  }
              </div>
              <div class="sql-query">${this.getAttribute("query") || ""}</div>
          </div>
          ${
            this.getAttribute("explanation")
              ? `
              <div class="explanation">${this.getAttribute("explanation")}</div>
          `
              : ""
          }
      `;
  }
}

customElements.define("sql-query-box", SqlQueryBox);
