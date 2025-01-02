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
                  rows="1"
                  required
              ></textarea>
              <button type="button" class="sql-assistant-clear-input" title="Clear input">
                  <i class="fas fa-times"></i>
              </button>
              <button type="submit" class="sql-assistant-submit" disabled title="Send question">
                  <i class="fas fa-paper-plane"></i>
              </button>
          </div>
      </form>
      <div class="sql-assistant-response"></div>
  `;

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
    const clearBtn = container.querySelector(".sql-assistant-clear-input");

    // Gestione input e pulsanti
    input.addEventListener("input", () => {
      submitBtn.disabled = !input.value.trim();
      clearBtn.style.opacity = input.value.trim() ? "1" : "0";
    });

    // Clear input button
    clearBtn.addEventListener("click", () => {
      input.value = "";
      submitBtn.disabled = true;
      clearBtn.style.opacity = "0";
      input.focus();
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
   * Mostra la risposta dell'assistente nell'interfaccia
   * Gestisce la visualizzazione della query SQL, la sua spiegazione
   * e i controlli per copiare la query e fare nuove domande
   *
   * @param {Object} response - La risposta dall'API
   * @param {string} response.query - La query SQL generata
   * @param {string} response.explanation - La spiegazione in linguaggio naturale
   */
  showResponse(response) {
    // Recupera il container delle risposte
    const responseContainer = this.container.querySelector(
      ".sql-assistant-response"
    );

    // Inizia a costruire l'HTML della risposta
    let html = '<div class="sql-assistant-response-content">';

    // Sezione Query SQL (se presente)
    if (response.query) {
      html += `
          <div class="sql-query-container">
              <div class="sql-query-toolbar">
                  <span class="sql-label">Generated SQL Query</span>
                  <button class="copy-button" title="Copy to clipboard">
                      <i class="fas fa-copy"></i>
                  </button>
              </div>
              <div class="sql-query">
                  ${this.formatSQLQuery(response.query)}
              </div>
          </div>
      `;
    }

    // Sezione Spiegazione (se presente)
    if (response.explanation) {
      html += `
          <div class="explanation">
              <i class="fas fa-info-circle" style="color: var(--brand-accent);"></i>
              <div>
                  ${response.explanation}
              </div>
          </div>
      `;
    }

    // Aggiungi il pulsante per fare una nuova domanda
    html += `
      <button class="sql-assistant-new-question">
          <i class="fas fa-plus-circle"></i>
          Ask another question
      </button>
  `;

    html += "</div>";

    // Inserisce l'HTML nel container
    responseContainer.innerHTML = html;

    // Setup del pulsante di copia
    const copyBtn = responseContainer.querySelector(".copy-button");
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        try {
          // Copia la query negli appunti
          await navigator.clipboard.writeText(response.query);

          // Feedback visivo di successo
          copyBtn.innerHTML = '<i class="fas fa-check"></i>';
          copyBtn.style.backgroundColor = "rgba(34, 197, 94, 0.2)";

          // Ripristina il pulsante dopo 2 secondi
          setTimeout(() => {
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
          }, 2000);
        } catch (err) {
          // Feedback visivo di errore
          copyBtn.innerHTML = '<i class="fas fa-times"></i>';
          copyBtn.style.backgroundColor = "rgba(239, 68, 68, 0.2)";

          // Ripristina il pulsante dopo 2 secondi
          setTimeout(() => {
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
          }, 2000);

          console.error("Failed to copy:", err);
        }
      });
    }

    // Setup del pulsante "New Question"
    const newQuestionBtn = responseContainer.querySelector(
      ".sql-assistant-new-question"
    );
    if (newQuestionBtn) {
      newQuestionBtn.addEventListener("click", () => {
        // Pulisci l'area delle risposte
        responseContainer.innerHTML = "";

        // Recupera, pulisci e focalizza l'input
        const input = this.container.querySelector(".sql-assistant-input");
        input.value = "";
        input.focus();

        // Disabilita il pulsante di submit
        const submitBtn = this.container.querySelector(".sql-assistant-submit");
        if (submitBtn) {
          submitBtn.disabled = true;
        }
      });
    }
  }

  /**
   * Formatta una query SQL per la visualizzazione con layout strutturato
   * @param {string} query - Query SQL da formattare
   * @returns {string} Query formattata con sintassi evidenziata e layout strutturato
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

    // Prima rimuovi spazi extra e normalizza gli spazi bianchi
    let formattedQuery = query.trim().replace(/\s+/g, " ");

    // Aggiungi interruzioni di riga dopo le keyword principali
    const mainKeywords = [
      "SELECT",
      "FROM",
      "WHERE",
      "GROUP BY",
      "ORDER BY",
      "HAVING",
    ];
    mainKeywords.forEach((keyword) => {
      const regex = new RegExp(`\\b${keyword}\\b`, "gi");
      formattedQuery = formattedQuery.replace(regex, `\n${keyword}`);
    });

    // Indenta le linee dopo la prima
    formattedQuery = formattedQuery
      .split("\n")
      .map((line, index) => {
        if (index === 0) return line.trim();
        return "    " + line.trim(); // 4 spazi per l'indentazione
      })
      .join("\n");

    // Escape dei caratteri HTML
    formattedQuery = formattedQuery.replace(
      /[&<>]/g,
      (char) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
        }[char])
    );

    // Evidenzia tutte le keywords SQL
    keywords.forEach((keyword) => {
      const regex = new RegExp(`\\b${keyword}\\b`, "gi");
      formattedQuery = formattedQuery.replace(
        regex,
        (match) => `<span class="sql-keyword">${match.toUpperCase()}</span>`
      );
    });

    // Evidenzia le funzioni
    const functions = ["AVG", "COUNT", "SUM", "MAX", "MIN"];
    functions.forEach((func) => {
      const regex = new RegExp(`\\b${func}\\b\\s*\\(`, "gi");
      formattedQuery = formattedQuery.replace(
        regex,
        (match) => `<span class="sql-function">${match.slice(0, -1)}</span>(`
      );
    });

    // Aggiungi style per preservare gli spazi bianchi e le interruzioni di riga
    return `<pre style="margin: 0; white-space: pre-wrap;">${formattedQuery}</pre>`;
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
