import { TableSqlAssistant } from "./tableSqlAssistant.js";
import { TablePreview } from "./tablePreview.js";

/**
 * TableDetails gestisce la visualizzazione e l'interazione con il pannello dei dettagli
 * delle tabelle del database. Mostra informazioni su colonne, relazioni e query di esempio.
 */
export class TableDetails {
  /**
   * Inizializza il gestore dei dettagli delle tabelle
   * @param {Object} schemaData - I dati completi dello schema del database
   */
  constructor(schemaData, cy) {
    // Memorizza i dati dello schema per riferimenti futuri
    this.schemaData = schemaData;

    // Memorizza l'istanza di Cytoscape
    this.cy = cy;

    // Inizializza lo stack della cronologia
    this.history = null;

    // Inizializza l'overlay
    this.createOverlay();
    // Inizializza gli event listener
    this.setupEventListeners();
    // Inizializza i listener per le relazioni
    this.setupRelationshipListeners();
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
   * Gestisce la chiusura del panel e la navigazione back
   * @private
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

    // Gestione del pulsante back
    const backButton = document.querySelector(".details-back-button");
    if (backButton) {
      backButton.addEventListener("click", () => {
        this.handleBackClick();
      });
    }
  }

  /**
   * Nasconde il panel dei dettagli
   */
  /**
   * Nasconde il panel dei dettagli
   */
  hideDetailsPanel() {
    const detailsPanel = document.getElementById("tableDetails");
    const overlay = document.querySelector(".panel-overlay");
    if (detailsPanel) {
      detailsPanel.classList.remove("visible");
      detailsPanel.classList.add("hidden");

      // Reset della cronologia quando si chiude il panel
      this.history = null;
    }
    if (overlay) {
      overlay.classList.remove("active");
    }
  }

  /**
   * Aggiorna e mostra il panel con i dettagli della tabella
   * @param {Object} node - Il nodo Cytoscape selezionato
   * @param {boolean} [addToHistory=true] - Se true, aggiunge la tabella alla cronologia
   */
  async updateDetails(node, addToHistory = true) {
    const table = node.data("tableData");
    // Salva il riferimento alla tabella corrente
    this.currentTable = table;

    const detailsPanel = document.getElementById("tableDetails");
    if (!detailsPanel) return;

    const detailsContent = detailsPanel.querySelector(".details-content");
    // Animazione di transizione
    detailsContent.classList.add("transitioning");

    // Gestione della cronologia
    if (this.history === null) {
      // Prima apertura del panel
      this.history = [node];
    } else if (addToHistory) {
      // Evita duplicati consecutivi
      const lastNode = this.history[this.history.length - 1];
      if (lastNode.id() !== node.id()) {
        this.history.push(node);
      }
    }

    // Aggiorna il pulsante Back
    this.updateBackButton();

    // Attendi la fine dell'animazione di fade out
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Aggiorna il contenuto
    const detailsTitle = detailsPanel.querySelector(".details-title");
    detailsTitle.textContent = table.name;
    detailsContent.innerHTML = this.generateDetailsContent(table);

    // Setup dei listener per le tab
    this.setupTabsListeners();

    // Mostra il panel e rimuovi la classe di transizione
    detailsPanel.classList.remove("hidden");
    requestAnimationFrame(() => {
      detailsPanel.classList.add("visible");
      detailsContent.classList.remove("transitioning");
      document.querySelector(".panel-overlay").classList.add("active");
    });
  }

  /**
   * Aggiorna la visibilità e lo stato del pulsante Back
   * @private
   */
  updateBackButton() {
    const backButton = document.querySelector(".details-back-button");
    if (backButton) {
      // Mostra il pulsante solo se c'è più di un elemento nella cronologia
      const shouldShow = this.history && this.history.length > 1;
      backButton.style.display = shouldShow ? "flex" : "none";
    }
  }

  /**
   * Gestisce il click sul pulsante Back
   * @private
   */
  handleBackClick() {
    if (this.history && this.history.length > 1) {
      // Rimuovi l'ultimo elemento
      this.history.pop();

      // Prendi l'ultima tabella della cronologia
      const previousNode = this.history[this.history.length - 1];

      // Verifica che il nodo esista ancora nel grafo
      if (previousNode && this.cy.$(`#${previousNode.id()}`).length) {
        this.updateDetails(previousNode, false);
      } else {
        // Se il nodo non esiste più, resetta la cronologia
        this.history = null;
        this.hideDetailsPanel();
      }
    }
  }

  /**
   * Genera il contenuto HTML completo per il pannello dei dettagli
   * @param {Object} table - I dati della tabella
   * @returns {string} HTML formattato per il pannello dei dettagli
   */
  generateDetailsContent(table) {
    // Recupera le relazioni per la tabella corrente
    const relationships = this.getTableRelationships(table.name);

    // Overview tab content
    const overviewContent = `
      <div class="section">
          <h3 class="section-title">TABLE SUMMARY</h3>
          <p class="table-description">
              ${table.description || "No description available for this table."}
          </p>
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
                  <span class="stat-value">
                      ${table.columns.filter((col) => col.isPrimaryKey).length}
                  </span>
              </div>
              <div class="stat-item">
                  <span class="stat-label">Foreign Keys</span>
                  <span class="stat-value">
                      ${table.columns.filter((col) => col.isForeignKey).length}
                  </span>
              </div>
          </div>
      </div>
  `;

    // Columns tab content
    const columnsContent = `
      <div class="section">
          <h4>Columns</h4>
          ${this.generateColumnsTable(table.columns)}
      </div>
  `;

    // Relationships tab content
    const relationshipsContent = `
      <div class="section">
          <h4>Relationships</h4>
          ${this.generateRelationshipsList(relationships)}
      </div>
  `;

    // Data Preview tab content
    const dataPreviewContent = `
      <div class="section">
          <h4>Data Preview</h4>
          <div id="previewContainer"></div>
      </div>
  `;

    // Sample Queries tab content
    const queriesContent = `
      <div class="section">
          <h4>Sample Queries</h4>
          ${this.generateSampleQuery(table.name, table.columns)}
      </div>
  `;

    // SQL Assistant tab content
    const sqlAssistantContent = `
      <div class="section">
          <h4>SQL Assistant</h4>
          <div id="sqlAssistantContainer"></div>
      </div>
  `;

    // Definisce il contenuto completo di tutte le tab
    const tabsContent = {
      overview: overviewContent,
      columns: columnsContent,
      relationships: relationshipsContent,
      dataPreview: dataPreviewContent,
      queries: queriesContent,
      askSql: sqlAssistantContent,
    };

    // Genera l'header delle tab con i bottoni
    const tabButtons = `
      <div class="tabs-header">
          <button class="tab-button active" data-tab="overview">
              <i class="fas fa-info-circle"></i>
              Overview
          </button>
          <button class="tab-button" data-tab="columns">
              <i class="fas fa-table"></i>
              Columns <span class="tab-counter">${table.columns.length}</span>
          </button>
          <button class="tab-button" data-tab="relationships">
              <i class="fas fa-project-diagram"></i>
              Relations <span class="tab-counter">${relationships.length}</span>
          </button>
          <button class="tab-button" data-tab="dataPreview">
              <i class="fas fa-eye"></i>
              Preview
          </button>
          <button class="tab-button" data-tab="queries">
              <i class="fas fa-database"></i>
              Queries
          </button>
          <button class="tab-button" data-tab="askSql">
              <i class="fas fa-magic"></i>
              Ask SQL
          </button>
      </div>
  `;

    // Genera il contenuto delle tab
    const tabPanes = Object.entries(tabsContent)
      .map(
        ([key, content]) => `
          <div class="tab-pane ${key === "overview" ? "active" : ""}" 
               data-tab="${key}">
              ${content}
          </div>
      `
      )
      .join("");

    // Assembla il contenitore finale delle tab
    return `
      <div class="tabs-container">
          ${tabButtons}
          <div class="tabs-content">
              ${tabPanes}
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

      // Se la tab è dataPreview, inizializza la preview
      if (tabId === "dataPreview") {
        const container = tabsContainer.querySelector("#previewContainer");
        // Verifica se la preview è già stata inizializzata
        if (container && !container.hasChildNodes()) {
          const preview = new TablePreview(this.currentTable.name);
          container.appendChild(preview.createPreviewElement());
        }
      }

      // Se la tab è askSql, inizializza l'assistente
      if (tabId === "askSql") {
        const container = tabsContainer.querySelector("#sqlAssistantContainer");
        // Verifica se l'assistente è già stato inizializzato
        if (container && !container.hasChildNodes()) {
          const assistant = new TableSqlAssistant(this.currentTable.name);
          container.appendChild(assistant.createAssistantElement());
        }
      }
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
    const targetTable = rel.type === "outgoing" ? rel.to : rel.from;

    return `
        <div class="relationship-item">
            <div class="relationship-header">
                <a href="#" class="relationship-link" data-table="${targetTable}">
                    ${rel.from} ${arrow} ${rel.to}
                </a>
            </div>
            <div class="relationship-details">
                <small class="columns">
                    ${rel.fromColumns.join(", ")} → ${rel.toColumns.join(", ")}
                </small>
                <small class="type">Type: N-1</small>
            </div>
        </div>
    `;
  }

  setupRelationshipListeners() {
    const detailsPanel = document.getElementById("tableDetails");
    if (!detailsPanel) return;

    detailsPanel.addEventListener("click", (e) => {
      const link = e.target.closest(".relationship-link");
      if (!link) return;

      e.preventDefault();
      const targetTable = link.dataset.table;
      const targetNode = this.cy.$(`node[id = "${targetTable}"]`);

      if (targetNode.length) {
        this.updateDetails(targetNode[0]);
      }
    });
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
