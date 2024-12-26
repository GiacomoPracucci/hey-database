/**
 * ResultsTable Web Component
 *
 * Componente per visualizzare i risultati di una query in formato tabellare.
 * Supporta la paginazione, l'ordinamento e il filtraggio dei dati.
 *
 * Attributes:
 * - data: array di oggetti JSON contenente i dati (deve essere settato via JavaScript)
 * - page-size: numero di righe per pagina (default: 10)
 * - show-pagination: se mostrare i controlli di paginazione (default: true)
 * - empty-message: messaggio da mostrare quando non ci sono risultati
 *
 * Events:
 * - pageChange: emesso quando cambia la pagina
 * - sort: emesso quando viene richiesto un ordinamento
 *
 * Usage:
 * <results-table page-size="15" empty-message="Nessun risultato trovato"></results-table>
 *
 * // Set data via JavaScript:
 * document.querySelector('results-table').data = [...];
 */
class ResultsTable extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    this._data = [];
    this._currentPage = 1;
    this._sortColumn = null;
    this._sortDirection = "asc";

    this.handleSort = this.handleSort.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
  }

  get data() {
    return this._data;
  }

  set data(newData) {
    this._data = Array.isArray(newData) ? newData : [];
    this._currentPage = 1;
    this.render();
  }

  connectedCallback() {
    this.render();
  }

  static get observedAttributes() {
    return ["page-size", "show-pagination", "empty-message"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  getCurrentPageData() {
    let data = [...this._data];

    if (this._sortColumn) {
      data.sort((a, b) => {
        const aValue = a[this._sortColumn];
        const bValue = b[this._sortColumn];

        if (typeof aValue === "number" && typeof bValue === "number") {
          return this._sortDirection === "asc"
            ? aValue - bValue
            : bValue - aValue;
        }

        return this._sortDirection === "asc"
          ? String(aValue).localeCompare(String(bValue))
          : String(bValue).localeCompare(String(aValue));
      });
    }

    const pageSize = parseInt(this.getAttribute("page-size")) || 10;
    const start = (this._currentPage - 1) * pageSize;
    return data.slice(start, start + pageSize);
  }

  handleSort(column) {
    if (this._sortColumn === column) {
      this._sortDirection = this._sortDirection === "asc" ? "desc" : "asc";
    } else {
      this._sortColumn = column;
      this._sortDirection = "asc";
    }

    this.dispatchEvent(
      new CustomEvent("sort", {
        detail: { column, direction: this._sortDirection },
        bubbles: true,
        composed: true,
      })
    );

    this.render();
  }

  handlePageChange(newPage) {
    this._currentPage = newPage;

    this.dispatchEvent(
      new CustomEvent("pageChange", {
        detail: { page: newPage },
        bubbles: true,
        composed: true,
      })
    );

    this.render();
  }

  render() {
    const pageData = this.getCurrentPageData();
    const columns = pageData.length > 0 ? Object.keys(pageData[0]) : [];
    const showPagination = this.getAttribute("show-pagination") !== "false";
    const emptyMessage =
      this.getAttribute("empty-message") || "Nessun risultato disponibile";

    this.shadowRoot.innerHTML = `
          <style>
              :host {
                  display: block;
                  margin: var(--layout-spacing-lg) 0;
              }

              .results-container {
                  background-color: var(--surface-white);
                  border-radius: var(--btn-border-radius);
                  box-shadow: var(--shadow-sm);
                  overflow: hidden;
              }

              .results-table {
                  width: 100%;
                  border-collapse: collapse;
                  font-size: var(--btn-font-size);
              }

              th, td {
                  padding: var(--layout-spacing-md) var(--layout-spacing-lg);
                  text-align: left;
                  border-bottom: 1px solid var(--results-table-border);
              }

              th {
                  background-color: var(--results-header-bg);
                  font-weight: var(--nav-font-weight);
                  color: var(--results-text-color);
                  cursor: pointer;
                  user-select: none;
                  position: relative;
                  transition: background-color var(--transition-fast);
              }

              th:hover {
                  background-color: var(--surface-lighter);
              }

              th.sorted::after {
                  content: '';
                  display: inline-block;
                  width: 0;
                  height: 0;
                  margin-left: var(--layout-spacing-sm);
                  vertical-align: middle;
                  border-left: 4px solid transparent;
                  border-right: 4px solid transparent;
              }

              th.sorted.asc::after {
                  border-bottom: 4px solid currentColor;
              }

              th.sorted.desc::after {
                  border-top: 4px solid currentColor;
              }

              tr:nth-child(even) {
                  background-color: var(--results-row-even);
              }

              .empty-message {
                  padding: var(--layout-spacing-xl);
                  text-align: center;
                  color: var(--text-muted);
                  font-style: italic;
              }

              .pagination {
                  display: flex;
                  align-items: center;
                  justify-content: space-between;
                  padding: var(--layout-spacing-md) var(--layout-spacing-lg);
                  background-color: var(--results-header-bg);
                  border-top: 1px solid var(--results-table-border);
              }

              .pagination button {
                  padding: var(--btn-padding-y) var(--btn-padding-x);
                  border: 1px solid var(--btn-border-color);
                  background: none;
                  border-radius: var(--btn-border-radius);
                  cursor: pointer;
                  color: var(--text-primary);
                  font-size: var(--btn-font-size);
                  transition: all var(--transition-fast);
              }

              .pagination button:disabled {
                  opacity: 0.5;
                  cursor: not-allowed;
              }

              .pagination button:not(:disabled):hover {
                  background-color: var(--surface-lighter);
                  border-color: var(--border-dark);
              }

              .pagination-info {
                  color: var(--text-muted);
                  font-size: var(--btn-font-size);
              }

              .pagination-controls {
                  display: flex;
                  gap: var(--layout-spacing-sm);
              }
          </style>

          <div class="results-container">
              ${
                this._data.length > 0
                  ? `
                  <table class="results-table">
                      <thead>
                          <tr>
                              ${columns
                                .map(
                                  (col) => `
                                  <th class="${
                                    this._sortColumn === col
                                      ? `sorted ${this._sortDirection}`
                                      : ""
                                  }"
                                      data-column="${col}">
                                      ${col}
                                  </th>
                              `
                                )
                                .join("")}
                          </tr>
                      </thead>
                      <tbody>
                          ${pageData
                            .map(
                              (row) => `
                              <tr>
                                  ${columns
                                    .map(
                                      (col) => `
                                      <td>${row[col]}</td>
                                  `
                                    )
                                    .join("")}
                              </tr>
                          `
                            )
                            .join("")}
                      </tbody>
                  </table>
                  ${showPagination ? this.renderPagination() : ""}
              `
                  : `
                  <div class="empty-message">${emptyMessage}</div>
              `
              }
          </div>
      `;

    if (this._data.length > 0) {
      this.shadowRoot.querySelectorAll("th").forEach((th) => {
        th.addEventListener("click", () => this.handleSort(th.dataset.column));
      });
    }
  }

  renderPagination() {
    const pageSize = parseInt(this.getAttribute("page-size")) || 10;
    const totalPages = Math.ceil(this._data.length / pageSize);

    if (totalPages <= 1) return "";

    const start = (this._currentPage - 1) * pageSize + 1;
    const end = Math.min(this._currentPage * pageSize, this._data.length);

    return `
          <div class="pagination">
              <span class="pagination-info">
                  Mostro ${start}-${end} di ${this._data.length} risultati
              </span>
              <div class="pagination-controls">
                  <button 
                      ${this._currentPage === 1 ? "disabled" : ""}
                      onclick="this.getRootNode().host.handlePageChange(${
                        this._currentPage - 1
                      })">
                      Precedente
                  </button>
                  <button 
                      ${this._currentPage === totalPages ? "disabled" : ""}
                      onclick="this.getRootNode().host.handlePageChange(${
                        this._currentPage + 1
                      })">
                      Successiva
                  </button>
              </div>
          </div>
      `;
  }
}

customElements.define("results-table", ResultsTable);
