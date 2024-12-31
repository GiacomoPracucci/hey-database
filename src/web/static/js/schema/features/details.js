/**
 * TableDetails gestisce la visualizzazione e l'interazione con il pannello dei dettagli
 * delle tabelle del database. Mostra informazioni su colonne, relazioni e query di esempio.
 */
export class TableDetails {
  /**
   * Inizializza il gestore dei dettagli delle tabelle
   * @param {Object} schemaData - I dati completi dello schema del database
   */
  constructor(schemaData) {
    // Memorizza i dati dello schema per riferimenti futuri
    this.schemaData = schemaData;

    // Inizializza l'overlay
    this.createOverlay();
    // Inizializza gli event listener
    this.setupEventListeners();
  }

  /**
   * Crea l'overlay di sfondo se non esiste
   */
  createOverlay() {
    if (!document.querySelector(".panel-overlay")) {
      const overlay = document.createElement("div");
      overlay.className = "panel-overlay";
      document.body.appendChild(overlay);

      // Chiude il panel al click sull'overlay
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          this.hideDetailsPanel();
        }
      });
    }
  }

  /**
   * Configura gli event listener per il pannello dei dettagli
   * Principalmente gestisce la chiusura del pannello
   */
  setupEventListeners() {
    // Gestione chiusura con pulsante
    const closeButton = document.querySelector(".table-details .close-button");
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        this.hideDetailsPanel();
      });
    }

    // Gestione chiusura con tasto ESC
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.hideDetailsPanel();
      }
    });
  }

  /**
   * Nasconde il panel dei dettagli
   */
  hideDetailsPanel() {
    const detailsPanel = document.getElementById("tableDetails");
    const overlay = document.querySelector(".panel-overlay");
    if (detailsPanel) {
      detailsPanel.classList.remove("visible");
      detailsPanel.classList.add("hidden");
    }
    if (overlay) {
      overlay.classList.remove("active");
    }
  }

  /**
   * Aggiorna e mostra il panel con i dettagli della tabella
   * @param {Object} node - Il nodo Cytoscape selezionato
   */
  updateDetails(node) {
    const table = node.data("tableData");
    const detailsPanel = document.getElementById("tableDetails");
    if (!detailsPanel) return;

    const detailsTitle = detailsPanel.querySelector(".details-title");
    const detailsContent = detailsPanel.querySelector(".details-content");

    // Aggiorna il contenuto
    detailsTitle.textContent = table.name;
    detailsContent.innerHTML = this.generateDetailsContent(table);
    this.setupTabsListeners();

    // Mostra il panel con animazione
    const overlay = document.querySelector(".panel-overlay");
    detailsPanel.classList.remove("hidden");
    requestAnimationFrame(() => {
      detailsPanel.classList.add("visible");
      overlay.classList.add("active");
    });
  }

  /**
   * Genera il contenuto HTML completo per il pannello dei dettagli
   * @param {Object} table - I dati della tabella
   * @returns {string} HTML formattato per il pannello dei dettagli
   */
  generateDetailsContent(table) {
    const relationships = this.getTableRelationships(table.name);

    // Genera il contenuto delle tab
    const tabsContent = {
      overview: `
      <div class="section">
          <h3 class="section-title">TABLE SUMMARY</h3>
          <p class="table-description">${
            table.description || "No description available for this table."
          }</p>
      </div>
      
      <div class="section">
          <h3 class="section-title">QUICK STATS</h3>
          <div class="quick-stats">
              <div class="stat-item">
                  <span class="stat-label">Columns</span>
                  <span class="stat-value">${table.columns.length}</span>
              </div>
              <div class="stat-item">
                  <span class="stat-label">Primary Keys</span>
                  <span class="stat-value">${
                    table.columns.filter((col) => col.isPrimaryKey).length
                  }</span>
              </div>
              <div class="stat-item">
                  <span class="stat-label">Foreign Keys</span>
                  <span class="stat-value">${
                    table.columns.filter((col) => col.isForeignKey).length
                  }</span>
              </div>
          </div>
      </div>`,

      columns: `
          <div class="section">
              <h4>Columns</h4>
              ${this.generateColumnsTable(table.columns)}
          </div>`,

      relationships: `
          <div class="section">
              <h4>Relationships</h4>
              ${this.generateRelationshipsList(relationships)}
          </div>`,

      queries: `
          <div class="section">
              <h4>Sample Queries</h4>
              ${this.generateSampleQuery(table.name, table.columns)}
          </div>`,
    };

    // Genera il markup delle tab
    return `
      <div class="tabs-container">
          <div class="tabs-header">
              <button class="tab-button active" data-tab="overview">
                  <i class="fas fa-info-circle"></i>
                  Overview
              </button>
              <button class="tab-button" data-tab="columns">
                  <i class="fas fa-table"></i>
                  Columns <span class="tab-counter">${
                    table.columns.length
                  }</span>
              </button>
              <button class="tab-button" data-tab="relationships">
                  <i class="fas fa-project-diagram"></i>
                  Relations <span class="tab-counter">${
                    relationships.length
                  }</span>
              </button>
              <button class="tab-button" data-tab="queries">
                  <i class="fas fa-database"></i>
                  Queries
              </button>
          </div>
          <div class="tabs-content">
              ${Object.entries(tabsContent)
                .map(
                  ([key, content]) => `
                  <div class="tab-pane ${
                    key === "overview" ? "active" : ""
                  }" data-tab="${key}">
                      ${content}
                  </div>
              `
                )
                .join("")}
          </div>
      </div>
  `;
  }

  /**
   * Configura gli event listener per le tab
   * @private
   */
  setupTabsListeners() {
    const detailsPanel = document.getElementById("tableDetails");
    if (!detailsPanel) return;

    detailsPanel.addEventListener("click", (e) => {
      const tabButton = e.target.closest(".tab-button");
      if (!tabButton) return;

      const tabId = tabButton.dataset.tab;
      const tabsContainer = tabButton.closest(".tabs-container");

      // Aggiorna i pulsanti attivi
      tabsContainer.querySelectorAll(".tab-button").forEach((btn) => {
        btn.classList.toggle("active", btn === tabButton);
      });

      // Aggiorna i contenuti attivi
      tabsContainer.querySelectorAll(".tab-pane").forEach((pane) => {
        pane.classList.toggle("active", pane.dataset.tab === tabId);
      });
    });
  }

  /**
   * Genera la tabella HTML delle colonne
   * @param {Array} columns - Array delle colonne della tabella
   * @returns {string} HTML della tabella delle colonne
   */
  generateColumnsTable(columns) {
    return `
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Properties</th>
                    </tr>
                </thead>
                <tbody>
                    ${columns
                      .map(
                        (col) => `
                        <tr class="${this.getColumnRowClass(col)}">
                            <td>${col.name}</td>
                            <td><code>${col.type}</code></td>
                            <td>${this.generateColumnProperties(col)}</td>
                        </tr>
                    `
                      )
                      .join("")}
                </tbody>
            </table>
        `;
  }

  /**
   * Determina la classe CSS per la riga della colonna
   * @param {Object} column - Dati della colonna
   * @returns {string} Classe CSS per la riga
   */
  getColumnRowClass(column) {
    return column.isPrimaryKey || column.isForeignKey ? "key-column" : "";
  }

  /**
   * Genera i badge delle proprietà per una colonna
   * @param {Object} column - Dati della colonna
   * @returns {string} HTML dei badge delle proprietà
   */
  generateColumnProperties(column) {
    const properties = [];

    if (column.isPrimaryKey) {
      properties.push('<span class="badge pk">PK</span>');
    }
    if (column.isForeignKey) {
      properties.push('<span class="badge fk">FK</span>');
    }
    if (!column.nullable) {
      properties.push('<span class="badge required">Required</span>');
    }

    return properties.join(" ");
  }

  /**
   * Recupera tutte le relazioni per una tabella specifica
   * Include sia le relazioni in entrata che in uscita
   * @param {string} tableName - Nome della tabella
   * @returns {Array} Array delle relazioni
   */
  getTableRelationships(tableName) {
    const relationships = [];

    // Cerca relazioni in uscita
    const currentTable = this.schemaData.tables.find(
      (t) => t.name === tableName
    );
    if (currentTable?.relationships) {
      currentTable.relationships.forEach((rel) => {
        relationships.push({
          type: "outgoing",
          from: tableName,
          to: rel.toTable,
          fromColumns: rel.fromColumns,
          toColumns: rel.toColumns,
        });
      });
    }

    // Cerca relazioni in entrata
    this.schemaData.tables.forEach((table) => {
      if (table.relationships) {
        table.relationships.forEach((rel) => {
          if (rel.toTable === tableName) {
            relationships.push({
              type: "incoming",
              from: table.name,
              to: tableName,
              fromColumns: rel.fromColumns,
              toColumns: rel.toColumns,
            });
          }
        });
      }
    });

    return relationships;
  }

  /**
   * Genera la lista HTML delle relazioni
   * @param {Array} relationships - Array delle relazioni
   * @returns {string} HTML della lista delle relazioni
   */
  generateRelationshipsList(relationships) {
    if (relationships.length === 0) {
      return `
                <div class="relationship-item">
                    <div class="text-muted">No relationships found</div>
                </div>
            `;
    }

    return relationships.map((rel) => this.formatRelationship(rel)).join("");
  }

  /**
   * Formatta una singola relazione in HTML
   * @param {Object} rel - Dati della relazione
   * @returns {string} HTML formattato della relazione
   */
  formatRelationship(rel) {
    const arrow = rel.type === "outgoing" ? "→" : "←";
    const direction =
      rel.type === "outgoing"
        ? `${rel.from} ${arrow} ${rel.to}`
        : `${rel.from} ${arrow} ${rel.to}`;

    return `
            <div class="relationship-item">
                <div class="relationship-header">
                    <span class="relationship-direction">${direction}</span>
                </div>
                <div class="relationship-details">
                    <small class="columns">
                        ${rel.fromColumns.join(", ")} → ${rel.toColumns.join(
      ", "
    )}
                    </small>
                    <small class="type">Type: N-1</small>
                </div>
            </div>
        `;
  }

  /**
   * Genera una query SQL di esempio per la tabella
   * @param {string} tableName - Nome della tabella
   * @param {Array} columns - Array delle colonne della tabella
   * @returns {string} HTML del container della query
   */
  generateSampleQuery(tableName, columns) {
    // Seleziona le colonne più significative per l'esempio
    const significantColumns = this.getSignificantColumns(columns);
    const columnsList = significantColumns.map((col) => col.name).join(", ");

    const query = `SELECT ${columnsList}
FROM ${tableName}
WHERE ${this.generateWhereClause(significantColumns)}
LIMIT 5;`;

    return `
            <div class="query-container">
                <pre><code>${query}</code></pre>
            </div>
        `;
  }

  /**
   * Seleziona le colonne più significative per la query di esempio
   * @param {Array} columns - Tutte le colonne della tabella
   * @returns {Array} Colonne selezionate per l'esempio
   */
  getSignificantColumns(columns) {
    // Prendi prima le chiavi primarie e foreign key
    let significant = columns.filter(
      (col) => col.isPrimaryKey || col.isForeignKey
    );

    // Aggiungi alcune colonne non-chiave se ce ne sono
    const nonKeyColumns = columns
      .filter((col) => !col.isPrimaryKey && !col.isForeignKey)
      .slice(0, 2);

    return [...significant, ...nonKeyColumns];
  }

  /**
   * Genera la clausola WHERE per la query di esempio
   * @param {Array} columns - Colonne da utilizzare nella clausola WHERE
   * @returns {string} Clausola WHERE formattata
   */
  generateWhereClause(columns) {
    // Usa la prima chiave primaria o la prima colonna disponibile
    const column = columns.find((col) => col.isPrimaryKey) || columns[0];

    if (this.isNumericType(column.type)) {
      return `${column.name} > 0`;
    } else {
      return `${column.name} IS NOT NULL`;
    }
  }

  /**
   * Verifica se un tipo di colonna è numerico
   * @param {string} type - Tipo SQL della colonna
   * @returns {boolean} True se il tipo è numerico
   */
  isNumericType(type) {
    const numericTypes = [
      "int",
      "integer",
      "decimal",
      "numeric",
      "float",
      "double",
    ];
    return numericTypes.some((t) => type.toLowerCase().includes(t));
  }
}
