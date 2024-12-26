/**
 * SchemaDetailsPanel Web Component
 *
 * Componente per visualizzare i dettagli di una tabella del database,
 * incluse colonne, relazioni e query di esempio.
 *
 * Attributes:
 * - table-name: nome della tabella
 * - columns: array di colonne in formato JSON (settato via JavaScript)
 * - relationships: array di relazioni in formato JSON (settato via JavaScript)
 * - position: posizione del pannello ('right', 'left') default: 'right'
 *
 * Events:
 * - close: emesso quando il pannello viene chiuso
 * - relationClick: emesso quando viene cliccata una relazione
 *
 * Usage:
 * <schema-details-panel
 *   table-name="users"
 *   position="right">
 * </schema-details-panel>
 *
 * // Set data via JavaScript:
 * const panel = document.querySelector('schema-details-panel');
 * panel.columns = [...];
 * panel.relationships = [...];
 */
class SchemaDetailsPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    // Stato interno
    this._columns = [];
    this._relationships = [];

    // Binding dei metodi
    this.handleClose = this.handleClose.bind(this);
    this.handleRelationClick = this.handleRelationClick.bind(this);
  }

  /**
   * Getter e Setter per colonne e relazioni
   */
  get columns() {
    return this._columns;
  }

  set columns(newColumns) {
    this._columns = Array.isArray(newColumns) ? newColumns : [];
    this.render();
  }

  get relationships() {
    return this._relationships;
  }

  set relationships(newRelationships) {
    this._relationships = Array.isArray(newRelationships)
      ? newRelationships
      : [];
    this.render();
  }

  /**
   * Lifecycle callbacks
   */
  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  static get observedAttributes() {
    return ["table-name", "position"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  /**
   * Setup degli event listeners
   */
  setupEventListeners() {
    const closeButton = this.shadowRoot.querySelector(".close-button");
    if (closeButton) {
      closeButton.addEventListener("click", this.handleClose);
    }

    const relationLinks =
      this.shadowRoot.querySelectorAll(".relationship-item");
    relationLinks.forEach((link) => {
      link.addEventListener("click", () => {
        this.handleRelationClick(link.dataset.relation);
      });
    });
  }

  /**
   * Gestione degli eventi
   */
  handleClose() {
    this.dispatchEvent(
      new CustomEvent("close", {
        bubbles: true,
        composed: true,
      })
    );
  }

  handleRelationClick(relationData) {
    this.dispatchEvent(
      new CustomEvent("relationClick", {
        detail: JSON.parse(relationData),
        bubbles: true,
        composed: true,
      })
    );
  }

  /**
   * Formatta il tipo di una colonna per la visualizzazione
   */
  formatColumnType(type) {
    return type.replace(/\([^)]*\)/g, "").toLowerCase();
  }

  /**
   * Render del componente
   */
  render() {
    const tableName = this.getAttribute("table-name") || "";
    const position = this.getAttribute("position") || "right";

    this.shadowRoot.innerHTML = `
            <style>
                :host {
                    position: absolute;
                    top: var(--layout-spacing-xl);
                    ${position}: var(--layout-spacing-xl);
                    width: 400px;
                    z-index: 1000;
                    opacity: 1;
                    transform: translateX(0);
                    transition: all var(--transition-normal);
                }

                :host(.hidden) {
                    opacity: 0;
                    transform: translateX(${
                      position === "right" ? "100%" : "-100%"
                    });
                    pointer-events: none;
                }

                .panel {
                    background: var(--surface-white);
                    border-radius: var(--btn-border-radius);
                    box-shadow: var(--details-panel-shadow);
                    overflow: hidden;
                }

                .panel-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: var(--layout-spacing-lg);
                    background-color: var(--details-header-background);
                    border-bottom: 1px solid var(--details-header-border);
                }

                .panel-title {
                    margin: 0;
                    font-size: var(--page-title-font-size);
                    font-weight: var(--nav-font-weight);
                    color: var(--details-title-color);
                }

                .close-button {
                    background: none;
                    border: none;
                    color: var(--text-muted);
                    cursor: pointer;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: var(--btn-border-radius);
                    transition: all var(--transition-fast);
                }

                .close-button:hover {
                    background-color: var(--hover-color);
                    color: var(--error-base);
                }

                .panel-content {
                    padding: var(--layout-spacing-xl);
                    max-height: calc(100vh - 200px);
                    overflow-y: auto;
                }

                .section {
                    margin-bottom: var(--details-section-spacing);
                }

                .section:last-child {
                    margin-bottom: 0;
                }

                .section-title {
                    margin: 0 0 var(--layout-spacing-md);
                    color: var(--details-section-title-color);
                    font-size: 0.875rem;
                    font-weight: var(--nav-font-weight);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .column-table {
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    font-size: var(--btn-font-size);
                    border: 1px solid var(--border-default);
                    border-radius: var(--btn-border-radius);
                    overflow: hidden;
                }

                .column-table th,
                .column-table td {
                    padding: var(--layout-spacing-sm) var(--layout-spacing-md);
                    border-bottom: 1px solid var(--border-default);
                }

                .column-table th {
                    background-color: var(--surface-light);
                    font-weight: var(--nav-font-weight);
                    color: var(--text-primary);
                    text-align: left;
                }

                .column-table tr:nth-child(even) {
                    background-color: var(--surface-lighter);
                }

                .column-table tr:last-child td {
                    border-bottom: none;
                }

                .badge {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: var(--nav-font-weight);
                    margin-right: 0.25rem;
                }

                .badge.pk {
                    background-color: var(--badge-pk-background);
                    color: var(--badge-pk-text);
                    border: 1px solid var(--badge-pk-border);
                }

                .badge.fk {
                    background-color: var(--badge-fk-background);
                    color: var(--badge-fk-text);
                    border: 1px solid var(--badge-fk-border);
                }

                .badge.required {
                    background-color: var(--badge-required-background);
                    color: var(--badge-required-text);
                    border: 1px solid var(--badge-required-border);
                }

                .relationship-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--layout-spacing-sm);
                }

                .relationship-item {
                    padding: var(--layout-spacing-md);
                    background-color: var(--relationship-item-background);
                    border: 1px solid var(--relationship-item-border);
                    border-radius: var(--btn-border-radius);
                    cursor: pointer;
                    transition: all var(--transition-fast);
                }

                .relationship-item:hover {
                    background-color: var(--surface-lighter);
                    border-color: var(--border-dark);
                }

                .relationship-title {
                    font-weight: var(--nav-font-weight);
                    color: var(--relationship-title-color);
                    margin-bottom: var(--layout-spacing-xs);
                }

                .relationship-detail {
                    font-size: 0.8125rem;
                    color: var(--relationship-detail-color);
                }

                .query-container {
                    background-color: var(--query-container-background);
                    border-radius: var(--btn-border-radius);
                    overflow: hidden;
                }

                .query-container pre {
                    margin: 0;
                    padding: var(--layout-spacing-lg);
                    color: var(--query-container-text);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    line-height: 1.5;
                    white-space: pre-wrap;
                }
            </style>

            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">${tableName}</h3>
                    <button class="close-button" aria-label="Close details">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="panel-content">
                    <!-- Sezione Colonne -->
                    <div class="section">
                        <h4 class="section-title">Columns</h4>
                        <table class="column-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Properties</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this._columns
                                  .map(
                                    (col) => `
                                    <tr>
                                        <td>${col.name}</td>
                                        <td><code>${this.formatColumnType(
                                          col.type
                                        )}</code></td>
                                        <td>
                                            ${
                                              col.isPrimaryKey
                                                ? '<span class="badge pk">PK</span>'
                                                : ""
                                            }
                                            ${
                                              col.isForeignKey
                                                ? '<span class="badge fk">FK</span>'
                                                : ""
                                            }
                                            ${
                                              !col.nullable
                                                ? '<span class="badge required">Required</span>'
                                                : ""
                                            }
                                        </td>
                                    </tr>
                                `
                                  )
                                  .join("")}
                            </tbody>
                        </table>
                    </div>

                    <!-- Sezione Relazioni -->
                    ${
                      this._relationships.length > 0
                        ? `
                        <div class="section">
                            <h4 class="section-title">Relationships</h4>
                            <div class="relationship-list">
                                ${this._relationships
                                  .map(
                                    (rel) => `
                                    <div class="relationship-item" 
                                         data-relation='${JSON.stringify(rel)}'>
                                        <div class="relationship-title">
                                            ${
                                              rel.type === "outgoing"
                                                ? `${tableName} → ${rel.to}`
                                                : `${rel.from} → ${tableName}`
                                            }
                                        </div>
                                        <div class="relationship-detail">
                                            Columns: ${rel.fromColumns.join(
                                              ", "
                                            )} → ${rel.toColumns.join(", ")}
                                        </div>
                                    </div>
                                `
                                  )
                                  .join("")}
                            </div>
                        </div>
                    `
                        : ""
                    }

                    <!-- Sezione Query di Esempio -->
                    <div class="section">
                        <h4 class="section-title">Sample Query</h4>
                        <div class="query-container">
                            <pre><code>SELECT *
FROM ${tableName}
LIMIT 5;</code></pre>
                        </div>
                    </div>
                </div>
            </div>
        `;
  }
}

customElements.define("schema-details-panel", SchemaDetailsPanel);
