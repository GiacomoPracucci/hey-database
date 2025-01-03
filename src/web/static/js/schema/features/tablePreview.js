/**
 * TablePreview gestisce il caricamento e la visualizzazione
 * di una preview dei dati della tabella
 */
export class TablePreview {
  /**
   * @param {string} tableName - Nome della tabella
   */
  constructor(tableName) {
    this.tableName = tableName;
    this.container = null;
    this.isLoading = false;
  }

  /**
   * Crea e restituisce l'elemento DOM della preview
   * @returns {HTMLElement}
   */
  createPreviewElement() {
    const container = document.createElement("div");
    container.className = "table-preview-container";

    // Aggiungi il contenitore del loader e dei dati
    container.innerHTML = `
          <div class="preview-loader" style="display: none;">
              <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
              </div>
              <div class="loading-text">Loading preview...</div>
          </div>
          <div class="preview-content"></div>
      `;

    this.container = container;
    this.loadPreviewData();

    return container;
  }

  /**
   * Carica i dati di preview dal server
   * @private
   */
  async loadPreviewData() {
    if (this.isLoading) return;

    this.showLoader();

    try {
      const response = await fetch(
        `/preview/api/tables/${this.tableName}/preview`
      );
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Failed to load preview data");
      }

      this.renderPreview(data.data);
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.hideLoader();
    }
  }

  /**
   * Renderizza i dati della preview
   * @param {Array} data - Dati da visualizzare
   * @private
   */
  renderPreview(data) {
    if (!data || data.length === 0) {
      this.showEmpty();
      return;
    }

    const previewContent = this.container.querySelector(".preview-content");

    // Crea il container per la tabella con scroll
    const tableWrapper = document.createElement("div");
    tableWrapper.className = "table-wrapper";

    // Container per la tabella con header fisso
    const tableContainer = document.createElement("div");
    tableContainer.className = "preview-table-container";

    // Crea la tabella
    tableContainer.innerHTML = `
      <table class="details-table preview-table">
          <thead>
              <tr>
                  ${Object.keys(data[0])
                    .map(
                      (key) => `
                      <th>${this.formatColumnHeader(key)}</th>
                  `
                    )
                    .join("")}
              </tr>
          </thead>
          <tbody>
              ${data
                .map(
                  (row) => `
                  <tr>
                      ${Object.values(row)
                        .map(
                          (value) => `
                          <td title="${this.formatTooltip(
                            value
                          )}">${this.formatValue(value)}</td>
                      `
                        )
                        .join("")}
                  </tr>
              `
                )
                .join("")}
          </tbody>
      </table>
  `;

    // Assembla la struttura
    tableWrapper.appendChild(tableContainer);
    previewContent.innerHTML = "";
    previewContent.appendChild(tableWrapper);
  }

  /**
   * Formatta l'header della colonna
   * @param {string} header - Nome della colonna
   * @returns {string} Header formattato
   * @private
   */
  formatColumnHeader(header) {
    // Capitalizza e sostituisce underscore con spazi
    return header
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ");
  }

  /**
   * Formatta il tooltip per i valori lunghi
   * @param {*} value - Valore da formattare
   * @returns {string} Tooltip formattato
   * @private
   */
  formatTooltip(value) {
    if (value === null || value === undefined) {
      return "NULL";
    }
    if (typeof value === "object") {
      return JSON.stringify(value);
    }
    return value.toString();
  }

  /**
   * Formatta un valore per la visualizzazione
   * @param {*} value - Valore da formattare
   * @returns {string} Valore formattato
   * @private
   */
  formatValue(value) {
    if (value === null || value === undefined) {
      return '<span class="text-muted">NULL</span>';
    }
    if (typeof value === "object") {
      return `<span title='${JSON.stringify(value)}'>${JSON.stringify(
        value,
        null,
        2
      )}</span>`;
    }
    const stringValue = value.toString();
    if (stringValue.length > 100) {
      return `${stringValue.substring(0, 100)}...`;
    }
    return stringValue;
  }

  /**
   * Mostra un messaggio di errore
   * @param {string} message - Messaggio di errore
   * @private
   */
  showError(message) {
    const previewContent = this.container.querySelector(".preview-content");
    previewContent.innerHTML = `
          <div class="error-container">
              <div class="error-icon">❌</div>
              <div class="error-message">
                  <div class="error-title">Error loading preview:</div>
                  <div class="error-details">${message}</div>
              </div>
          </div>
      `;
  }

  /**
   * Mostra un messaggio quando non ci sono dati
   * @private
   */
  showEmpty() {
    const previewContent = this.container.querySelector(".preview-content");
    previewContent.innerHTML = `
          <div class="preview-empty">
              <i class="fas fa-database"></i>
              <p>No data available for preview</p>
          </div>
      `;
  }

  /**
   * Mostra il loader
   * @private
   */
  showLoader() {
    this.isLoading = true;
    const loader = this.container.querySelector(".preview-loader");
    loader.style.display = "flex";
  }

  /**
   * Nasconde il loader
   * @private
   */
  hideLoader() {
    this.isLoading = false;
    const loader = this.container.querySelector(".preview-loader");
    loader.style.display = "none";
  }
}
