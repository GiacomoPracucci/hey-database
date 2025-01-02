/**
 * Gestisce l'interfaccia SQL Assistant nel pannello dei dettagli della tabella
 */
export class TableSqlAssistant {
  /**
   * @param {string} tableName - Nome della tabella corrente
   */
  constructor(tableName) {
    this.tableName = tableName;
    this.container = null;
    this.isLoading = false;
  }

  /**
   * Crea e restituisce l'elemento DOM dell'assistente
   * @returns {HTMLElement}
   */
  createAssistantElement() {
    const container = document.createElement("div");
    container.className = "sql-assistant-container";

    container.innerHTML = `
            <form class="sql-assistant-form">
                <div class="input-wrapper">
                    <textarea 
                        class="sql-assistant-input" 
                        placeholder="Ask a question about ${this.tableName} table..."
                        rows="3"
                    ></textarea>
                    <button type="submit" class="sql-assistant-submit" disabled>
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </form>
            <div class="sql-assistant-response"></div>
        `;

    // Setup degli event listeners
    this.setupEventListeners(container);

    this.container = container;
    return container;
  }

  /**
   * Configura gli event listeners per l'interfaccia
   * @param {HTMLElement} container
   */
  setupEventListeners(container) {
    const form = container.querySelector(".sql-assistant-form");
    const input = container.querySelector(".sql-assistant-input");
    const submitBtn = container.querySelector(".sql-assistant-submit");

    // Abilita/disabilita il pulsante in base all'input
    input.addEventListener("input", () => {
      submitBtn.disabled = !input.value.trim();
      // Reimposta l'altezza per gestire il contenuto cancellato
      input.style.height = "42px";
    });

    // Gestione dell'invio con Enter
    input.addEventListener("keydown", async (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const question = input.value.trim();
        if (question && !this.isLoading) {
          await this.handleQuestionSubmit(question);
          input.value = ""; // Reset input dopo l'invio
          submitBtn.disabled = true;
        }
      }
    });

    // Gestisce l'invio del form
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (this.isLoading) return;

      const question = input.value.trim();
      if (!question) return;

      await this.handleQuestionSubmit(question);
      input.value = ""; // Reset input dopo l'invio
      submitBtn.disabled = true;
    });
  }

  /**
   * Gestisce l'invio di una domanda
   * @param {string} question
   */
  async handleQuestionSubmit(question) {
    this.setLoading(true);
    this.clearResponse();

    try {
      const response = await fetch("/chat/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: `About table ${this.tableName}: ${question}`,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Failed to get response");
      }

      this.showResponse(data);
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Mostra la risposta nell'interfaccia con formattazione migliorata
   * @param {Object} response - Oggetto risposta dall'API
   */
  showResponse(response) {
    const responseContainer = this.container.querySelector(
      ".sql-assistant-response"
    );

    let html = '<div class="sql-assistant-response-content">';

    if (response.query) {
      html += `
          <div class="sql-query-container">
              <div class="sql-query-toolbar">
                  <span class="sql-label">Generated SQL Query</span>
                  <button class="copy-button" title="Copy to clipboard">
                      <i class="fas fa-copy"></i>
                  </button>
              </div>
              <div class="sql-query">${this.formatSQLQuery(
                response.query
              )}</div>
          </div>
      `;
    }

    if (response.explanation) {
      html += `
          <div class="explanation">
              <i class="fas fa-info-circle" style="color: var(--brand-accent);"></i>
              <div>${response.explanation}</div>
          </div>
      `;
    }

    html += "</div>";
    responseContainer.innerHTML = html;

    // Setup copy button
    const copyBtn = responseContainer.querySelector(".copy-button");
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(response.query);
          const originalIcon = copyBtn.innerHTML;
          copyBtn.innerHTML = '<i class="fas fa-check"></i>';

          setTimeout(() => {
            copyBtn.innerHTML = originalIcon;
          }, 2000);
        } catch (err) {
          console.error("Failed to copy:", err);
        }
      });
    }
  }

  /**
   * Formatta una query SQL con evidenziazione della sintassi
   * @param {string} query - Query SQL da formattare
   * @returns {string} Query formattata con keywords evidenziate
   * @private
   */
  formatSQLQuery(query) {
    const keywords = [
      "SELECT",
      "FROM",
      "WHERE",
      "GROUP BY",
      "ORDER BY",
      "HAVING",
      "JOIN",
      "LEFT JOIN",
      "RIGHT JOIN",
      "INNER JOIN",
      "ON",
      "AND",
      "OR",
      "IN",
      "NOT IN",
      "LIKE",
      "BETWEEN",
      "IS NULL",
      "IS NOT NULL",
      "COUNT",
      "SUM",
      "AVG",
      "MAX",
      "MIN",
      "DISTINCT",
      "AS",
    ];

    // Escape HTML special characters
    let formattedQuery = query.replace(
      /[&<>]/g,
      (char) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
        }[char])
    );

    // Replace SQL keywords with styled spans
    keywords.forEach((keyword) => {
      const regex = new RegExp(`\\b${keyword}\\b`, "gi");
      formattedQuery = formattedQuery.replace(
        regex,
        (match) => `<span class="sql-keyword">${match.toUpperCase()}</span>`
      );
    });

    return formattedQuery;
  }

  /**
   * Mostra un errore nell'interfaccia
   * @param {string} message
   */
  showError(message) {
    const responseContainer = this.container.querySelector(
      ".sql-assistant-response"
    );
    responseContainer.innerHTML = `
            <div class="error-container">
                <div class="error-icon">❌</div>
                <div class="error-message">
                    <div class="error-title">Error:</div>
                    <div class="error-details">${message}</div>
                </div>
            </div>
        `;
  }

  /**
   * Pulisce l'area della risposta
   */
  clearResponse() {
    const responseContainer = this.container.querySelector(
      ".sql-assistant-response"
    );
    responseContainer.innerHTML = "";
  }

  /**
   * Imposta lo stato di caricamento dell'interfaccia
   * @param {boolean} loading
   */
  setLoading(loading) {
    this.isLoading = loading;

    const submitBtn = this.container.querySelector(".sql-assistant-submit");
    const input = this.container.querySelector(".sql-assistant-input");

    submitBtn.disabled = loading;
    input.disabled = loading;

    submitBtn.innerHTML = loading
      ? '<i class="fas fa-spinner fa-spin"></i>'
      : '<i class="fas fa-paper-plane"></i>';
  }
}
