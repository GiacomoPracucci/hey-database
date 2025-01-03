import {
  CSS_CLASSES,
  ICONS,
  UI_TEXTS,
  DOM_ELEMENTS,
} from "../config/constants.js";

/**
 * ChatDomService gestisce tutte le manipolazioni del DOM per l'interfaccia chat.
 * Fornisce metodi per creare, manipolare e gestire elementi dell'interfaccia.
 */
export class ChatDomService {
  /**
   * Inizializza il servizio DOM
   * Recupera e memorizza i riferimenti agli elementi DOM principali
   */
  constructor() {
    this.chatMessages = document.getElementById(DOM_ELEMENTS.CHAT_MESSAGES);
    this.userInput = document.getElementById(DOM_ELEMENTS.USER_INPUT);
    this.sendButton = document.getElementById(DOM_ELEMENTS.SEND_BUTTON);

    if (!this.chatMessages || !this.userInput || !this.sendButton) {
      throw new Error("Required DOM elements not found");
    }
  }

  /**
   * Aggiunge un nuovo messaggio alla chat
   * @param {string|Object} content - Contenuto del messaggio
   * @param {string} type - Tipo di messaggio ('user' o 'bot')
   * @returns {HTMLElement} L'elemento messaggio creato
   */
  addMessage(content, type = "user") {
    const messageDiv = document.createElement("div");
    messageDiv.className = `${CSS_CLASSES.MESSAGE.CONTAINER} ${type}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = CSS_CLASSES.MESSAGE.CONTENT;

    if (type === "bot") {
      this.populateBotMessage(contentDiv, content);
    } else {
      contentDiv.textContent = content;
    }

    messageDiv.appendChild(contentDiv);
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();

    return messageDiv;
  }

  /**
   * Popola il contenuto di un messaggio bot
   * @param {HTMLElement} contentDiv - Elemento contenitore del messaggio
   * @param {Object} content - Contenuto del messaggio
   * @private
   */
  populateBotMessage(contentDiv, content) {
    if (!content.success) {
      this.createErrorMessage(contentDiv, content);
    } else {
      if (content.query) {
        contentDiv.appendChild(this.createQueryContainer(content));
      }
      if (content.explanation) {
        contentDiv.appendChild(this.createExplanation(content.explanation));
      }
      if (content.results?.length > 0) {
        contentDiv.appendChild(this.createResultsTable(content.results));
      }
    }
  }

  /**
   * Crea un contenitore di errore
   * @param {HTMLElement} container - Contenitore dove inserire l'errore
   * @param {Object} content - Contenuto dell'errore
   * @private
   */
  createErrorMessage(container, content) {
    const errorHtml = `
            <div class="${CSS_CLASSES.ERROR.CONTAINER}">
                <div class="error-icon">❌</div>
                <div class="error-message">
                    <div class="error-title">Si è verificato un errore:</div>
                    <div class="${CSS_CLASSES.ERROR.DETAILS}">${
      content.error
    }</div>
                    ${
                      content.query
                        ? `
                        <div class="${CSS_CLASSES.ERROR.QUERY}">
                            <div class="error-query-label">Query tentata:</div>
                            <pre><code>${content.query}</code></pre>
                        </div>
                    `
                        : ""
                    }
                </div>
            </div>
        `;
    container.innerHTML = errorHtml;
  }

  /**
   * Crea un contenitore per la query SQL
   * @param {Object} content - Contenuto del messaggio
   * @returns {HTMLElement} Contenitore della query
   * @private
   */
  createQueryContainer(content) {
    const queryContainer = document.createElement("div");
    queryContainer.className = CSS_CLASSES.SQL.CONTAINER;
    queryContainer.dataset.originalQuestion = content.original_question;

    const sqlLabel = document.createElement("span");
    sqlLabel.className = CSS_CLASSES.SQL.LABEL;
    sqlLabel.textContent = "SQL";
    queryContainer.appendChild(sqlLabel);

    const toolbar = this.createQueryToolbar(content);
    queryContainer.appendChild(toolbar);

    const queryDiv = document.createElement("div");
    queryDiv.className = CSS_CLASSES.SQL.QUERY;
    queryDiv.innerHTML = `<pre><code>${content.query}</code></pre>`;
    queryContainer.appendChild(queryDiv);

    return queryContainer;
  }

  /**
   * Crea la toolbar per una query SQL
   * @param {Object} content - Contenuto del messaggio
   * @returns {HTMLElement} Toolbar della query
   * @private
   */
  createQueryToolbar(content) {
    const toolbar = document.createElement("div");
    toolbar.className = CSS_CLASSES.SQL.TOOLBAR;

    toolbar.appendChild(this.createCopyButton(content.query));
    //toolbar.appendChild(this.createFeedbackButton(content));

    return toolbar;
  }

  /**
   * Crea un pulsante di copia
   * @param {string} textToCopy - Testo da copiare
   * @returns {HTMLButtonElement} Pulsante di copia
   * @private
   */
  createCopyButton(textToCopy) {
    const button = document.createElement("button");
    button.className = "copy-button";
    button.innerHTML = `<i class="fas ${ICONS.COPY}"></i>`;
    button.title = UI_TEXTS.COPY_BUTTON;

    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(textToCopy);
        button.innerHTML = `<i class="fas ${ICONS.CHECK}"></i>`;
        button.classList.add("copied");

        setTimeout(() => {
          button.innerHTML = `<i class="fas ${ICONS.COPY}"></i>`;
          button.classList.remove("copied");
        }, 2000);
      } catch (err) {
        console.error("Copy error:", err);
        button.innerHTML = `<i class="fas ${ICONS.TIMES}"></i>`;
        setTimeout(() => {
          button.innerHTML = `<i class="fas ${ICONS.COPY}"></i>`;
        }, 2000);
      }
    });

    return button;
  }

  /**
   * Crea un pulsante di feedback
   * @param {Object} content - Contenuto del messaggio
   * @returns {HTMLButtonElement} Pulsante di feedback
   * @private
   */
  createFeedbackButton(content) {
    const button = document.createElement("button");
    button.className = CSS_CLASSES.FEEDBACK.BUTTON;
    button.innerHTML = `<i class="fas ${ICONS.THUMBS_UP}"></i>`;
    button.title = UI_TEXTS.FEEDBACK_BUTTON;

    // Il listener verrà aggiunto dal FeedbackService
    button.dataset.feedbackData = JSON.stringify({
      question: content.original_question,
      sql_query: content.query,
      explanation: content.explanation,
    });

    return button;
  }

  /**
   * Crea un elemento di spiegazione
   * @param {string} explanation - Testo della spiegazione
   * @returns {HTMLElement} Elemento di spiegazione
   * @private
   */
  createExplanation(explanation) {
    const div = document.createElement("div");
    div.className = "explanation";
    div.textContent = explanation;
    return div;
  }

  /**
   * Crea una tabella dei risultati
   * @param {Array} results - Array dei risultati
   * @returns {HTMLElement} Contenitore della tabella
   * @private
   */
  createResultsTable(results) {
    const container = document.createElement("div");
    container.className = "results-container";

    const table = document.createElement("table");
    table.className = "results-table";

    // Intestazioni
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    Object.keys(results[0]).forEach((key) => {
      const th = document.createElement("th");
      th.textContent = key;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Dati
    const tbody = document.createElement("tbody");
    results.forEach((row) => {
      const tr = document.createElement("tr");
      Object.values(row).forEach((value) => {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    container.appendChild(table);
    return container;
  }

  /**
   * Aggiunge l'indicatore di digitazione
   * @returns {HTMLElement} L'elemento indicatore aggiunto
   */
  addLoadingIndicator() {
    const loadingDiv = document.createElement("div");
    loadingDiv.className = CSS_CLASSES.LOADING.CONTAINER;
    loadingDiv.id = DOM_ELEMENTS.TYPING_INDICATOR;

    loadingDiv.innerHTML = `
            <div class="${CSS_CLASSES.LOADING.INDICATOR}">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

    this.chatMessages.appendChild(loadingDiv);
    this.scrollToBottom();

    return loadingDiv;
  }

  /**
   * Rimuove l'indicatore di digitazione
   */
  removeLoadingIndicator() {
    const indicator = document.getElementById(DOM_ELEMENTS.TYPING_INDICATOR);
    if (indicator) {
      indicator.remove();
    }
  }

  /**
   * Gestisce l'altezza dinamica della textarea
   */
  adjustInputHeight() {
    this.userInput.style.height = "auto";
    this.userInput.style.height = `${this.userInput.scrollHeight}px`;
  }

  /**
   * Scorre la chat fino in fondo
   */
  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  /**
   * Pulisce l'input utente
   */
  clearInput() {
    this.userInput.value = "";
    this.adjustInputHeight();
  }

  /**
   * Disabilita l'interfaccia durante l'invio
   * @param {boolean} disabled - Stato di disabilitazione
   */
  setInterfaceDisabled(disabled) {
    this.userInput.disabled = disabled;
    this.sendButton.disabled = disabled;
  }

  /**
   * Imposta il focus sull'input
   */
  focusInput() {
    this.userInput.focus();
  }
}

// Creiamo un'istanza singola del servizio per l'applicazione
export const chatDomService = new ChatDomService();
