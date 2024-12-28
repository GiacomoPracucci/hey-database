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

    // Inizializza gli event listener
    this.setupEventListeners();
  }

  /**
   * Configura gli event listener per il pannello dei dettagli
   * Principalmente gestisce la chiusura del pannello
   */
  setupEventListeners() {
    const closeButton = document.querySelector(".table-details .close-button");
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        this.hideDetailsPanel();
      });
    }

    // Aggiungi listener per la chiusura con il tasto ESC
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.hideDetailsPanel();
      }
    });
  }

  /**
   * Nasconde il pannello dei dettagli
   */
  hideDetailsPanel() {
    const detailsPanel = document.getElementById("tableDetails");
    if (detailsPanel) {
      detailsPanel.classList.add("hidden");
    }
  }

  /**
   * Aggiorna il pannello dei dettagli con le informazioni della tabella selezionata
   * @param {Object} node - Il nodo Cytoscape selezionato
   */
  updateDetails(node) {
    const table = node.data("tableData");
    const detailsPanel = document.getElementById("tableDetails");
    if (!detailsPanel) return;

    const detailsTitle = detailsPanel.querySelector(".details-title");
    const detailsContent = detailsPanel.querySelector(".details-content");

    // Aggiorna il titolo e il contenuto
    detailsTitle.textContent = table.name;
    detailsContent.innerHTML = this.generateDetailsContent(table);

    // Mostra il pannello
    detailsPanel.classList.remove("hidden");
  }

  /**
   * Genera il contenuto HTML completo per il pannello dei dettagli
   * @param {Object} table - I dati della tabella
   * @returns {string} HTML formattato per il pannello dei dettagli
   */
  generateDetailsContent(table) {
    const relationships = this.getTableRelationships(table.name);

    return `
            <div class="section">
                <h4>Columns</h4>
                ${this.generateColumnsTable(table.columns)}
            </div>
            
            <div class="section">
                <h4>Relationships</h4>
                ${this.generateRelationshipsList(relationships)}
            </div>
            
            <div class="section">
                <h4>Sample Query</h4>
                ${this.generateSampleQuery(table.name, table.columns)}
            </div>
        `;
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
