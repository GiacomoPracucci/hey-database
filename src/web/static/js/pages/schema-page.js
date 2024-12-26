/**
 * SchemaPage
 *
 * Gestisce la logica della pagina dello schema del database, coordinando:
 * - Visualizzazione del grafo delle relazioni
 * - Interazioni con lo schema
 * - Ricerca e filtri
 * - Zoom e navigazione
 * - Dettagli delle tabelle
 */

// Verifica che le dipendenze globali siano caricate
if (!window.cytoscape) {
  throw new Error("Cytoscape library not loaded");
}

if (!window.dagre) {
  throw new Error("Dagre library not loaded");
}

if (!customElements.get("schema-details-panel")) {
  throw new Error("Schema details panel component not registered");
}

import { schemaService } from "../services/schema-service.js";

class SchemaPage {
  constructor() {
    // Riferimenti agli elementi DOM
    this.schemaViewer = document.getElementById("schemaViewer");
    this.searchInput = document.getElementById("schemaSearch");
    this.zoomInBtn = document.getElementById("zoomIn");
    this.zoomOutBtn = document.getElementById("zoomOut");
    this.zoomFitBtn = document.getElementById("zoomFit");

    // Istanza del grafo Cytoscape
    this.cy = null;

    // Stato corrente
    this.currentTableDetails = null;

    // Binding dei metodi
    this.handleSearch = this.debounce(this.handleSearch.bind(this), 300);
    this.handleTableSelect = this.handleTableSelect.bind(this);
    this.handleDetailsClose = this.handleDetailsClose.bind(this);

    // Inizializza la pagina
    this.initialize();
  }

  /**
   * Inizializza la pagina dello schema
   */
  async initialize() {
    this.showLoadingIndicator();

    try {
      // Registra il plugin dagre per Cytoscape
      cytoscape.use(window.cytoscapeDagre);

      // Inizializza il grafo
      await this.initializeCytoscape();

      // Imposta gli event listeners
      this.setupEventListeners();

      // Carica i dati dello schema
      await this.loadSchemaData();
    } catch (error) {
      console.error("Error initializing schema page:", error);
      this.showError("Failed to load schema data");
    } finally {
      this.hideLoadingIndicator();
    }
  }

  /**
   * Inizializza Cytoscape con le configurazioni base
   */
  async initializeCytoscape() {
    this.cy = cytoscape({
      container: this.schemaViewer,
      style: this.getCytoscapeStyles(),
      wheelSensitivity: 0.2,
      minZoom: 0.2,
      maxZoom: 3,
    });
  }

  /**
   * Definisce gli stili per il grafo Cytoscape
   */
  getCytoscapeStyles() {
    return [
      {
        selector: "node",
        style: {
          "background-color": "#ffffff",
          "border-width": 1,
          "border-color": "#e2e8f0",
          "border-opacity": 1,
          shape: "roundrectangle",
          width: "label",
          height: "label",
          padding: "20px",
          "text-wrap": "wrap",
          "text-max-width": "280px",
          "text-valign": "center",
          "text-halign": "center",
          "font-family": "ui-monospace, monospace",
          "font-size": "14px",
          color: "#0f172a",
          "text-margin-y": 5,
          "compound-sizing-wrt-labels": "include",
          "min-width": "200px",
          "min-height": "50px",
          "corner-radius": "8px",
        },
      },
      {
        selector: "edge",
        style: {
          width: 1.5,
          "line-color": "#94a3b8",
          "line-style": "dashed",
          "curve-style": "bezier",
          "target-arrow-color": "#94a3b8",
          "target-arrow-shape": "triangle",
          "arrow-scale": 1,
        },
      },
      {
        selector: ".highlighted",
        style: {
          "border-color": "#3b82f6",
          "border-width": 2,
          "background-color": "#f8fafc",
        },
      },
    ];
  }

  /**
   * Configura tutti gli event listeners
   */
  setupEventListeners() {
    // Event listeners per la ricerca
    this.searchInput.addEventListener("input", this.handleSearch);
    this.searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.searchInput.value = "";
        this.handleSearch();
      }
    });

    // Event listeners per lo zoom
    this.zoomInBtn.addEventListener("click", () => this.handleZoom("in"));
    this.zoomOutBtn.addEventListener("click", () => this.handleZoom("out"));
    this.zoomFitBtn.addEventListener("click", () => this.handleZoom("fit"));

    // Event listeners per il grafo
    this.cy.on("tap", "node", (e) => this.handleTableSelect(e.target.id()));
    this.cy.on("mouseover", "node", (e) =>
      this.highlightRelatedNodes(e.target, true)
    );
    this.cy.on("mouseout", "node", (e) =>
      this.highlightRelatedNodes(e.target, false)
    );
  }

  /**
   * Carica e visualizza i dati dello schema
   */
  async loadSchemaData() {
    const data = await schemaService.getSchemaMetadata();

    // Aggiunge gli elementi al grafo
    this.cy.add(data.elements);

    // Applica il layout
    const layout = this.cy.layout({
      name: "dagre",
      rankDir: "TB",
      rankSep: 100,
      nodeSep: 80,
      padding: 50,
      animate: true,
      animationDuration: 500,
    });

    await layout.run();

    // Centra e adatta la vista
    this.cy.fit(50);
    this.cy.center();
  }

  /**
   * Gestisce la selezione di una tabella
   * @param {string} tableId - ID della tabella selezionata
   */
  async handleTableSelect(tableId) {
    try {
      const tableDetails = await schemaService.getTableDetails(tableId);

      // Se c'è già un pannello dettagli, lo rimuove
      if (this.currentTableDetails) {
        this.currentTableDetails.remove();
      }

      // Crea e aggiunge il nuovo pannello dettagli
      this.currentTableDetails = document.createElement("schema-details-panel");
      this.currentTableDetails.setAttribute("table-name", tableId);
      this.currentTableDetails.columns = tableDetails.columns;
      this.currentTableDetails.relationships = tableDetails.relationships;

      // Ascolta l'evento di chiusura
      this.currentTableDetails.addEventListener(
        "close",
        this.handleDetailsClose
      );

      document
        .querySelector(".schema-container")
        .appendChild(this.currentTableDetails);
    } catch (error) {
      console.error("Error loading table details:", error);
      this.showError("Failed to load table details");
    }
  }

  /**
   * Gestisce la chiusura del pannello dettagli
   */
  handleDetailsClose() {
    if (this.currentTableDetails) {
      this.currentTableDetails.remove();
      this.currentTableDetails = null;
    }
  }

  /**
   * Gestisce la ricerca nelle tabelle
   */
  handleSearch() {
    const searchTerm = this.searchInput.value.toLowerCase().trim();

    if (!searchTerm) {
      // Reset della visualizzazione
      this.cy.elements().removeClass("faded highlighted search-match");
      return;
    }

    // Trova i nodi che corrispondono alla ricerca
    const matchingNodes = this.cy.nodes().filter((node) => {
      const data = node.data("tableData");
      if (!data) return false;

      return (
        data.name.toLowerCase().includes(searchTerm) ||
        data.columns.some(
          (col) =>
            col.name.toLowerCase().includes(searchTerm) ||
            col.type.toLowerCase().includes(searchTerm)
        )
      );
    });

    if (matchingNodes.length > 0) {
      // Evidenzia i risultati della ricerca
      this.cy.elements().addClass("faded");
      matchingNodes.removeClass("faded").addClass("search-match");

      // Evidenzia anche le relazioni tra i nodi trovati
      const relatedEdges = matchingNodes.edgesWith(matchingNodes);
      relatedEdges.removeClass("faded");

      // Centra la vista sui risultati
      this.cy.animate({
        fit: {
          eles: matchingNodes,
          padding: 50,
        },
        duration: 500,
      });
    }
  }

  /**
   * Gestisce le operazioni di zoom
   * @param {string} action - Tipo di zoom ('in', 'out', 'fit')
   */
  handleZoom(action) {
    const ZOOM_FACTOR = 1.2;

    switch (action) {
      case "in":
        this.cy.animate({
          zoom: this.cy.zoom() * ZOOM_FACTOR,
          duration: 200,
        });
        break;

      case "out":
        this.cy.animate({
          zoom: this.cy.zoom() / ZOOM_FACTOR,
          duration: 200,
        });
        break;

      case "fit":
        this.cy.animate({
          fit: {
            padding: 50,
          },
          duration: 300,
        });
        break;
    }
  }

  /**
   * Evidenzia i nodi collegati quando si passa sopra a un nodo
   * @param {Object} node - Nodo Cytoscape
   * @param {boolean} highlight - Se evidenziare o rimuovere l'evidenziazione
   */
  highlightRelatedNodes(node, highlight) {
    const connectedEdges = node.connectedEdges();
    const connectedNodes = connectedEdges.connectedNodes();

    if (highlight) {
      this.cy
        .elements()
        .difference(connectedEdges.union(connectedNodes).union(node))
        .addClass("faded");
      connectedEdges.addClass("highlighted");
      connectedNodes.addClass("highlighted");
    } else {
      this.cy.elements().removeClass("faded highlighted");
    }
  }

  /**
   * Mostra l'indicatore di caricamento
   */
  showLoadingIndicator() {
    const loadingIndicator = document.getElementById("loadingIndicator");
    if (loadingIndicator) {
      loadingIndicator.style.display = "flex";
    }
  }

  /**
   * Nasconde l'indicatore di caricamento
   */
  hideLoadingIndicator() {
    const loadingIndicator = document.getElementById("loadingIndicator");
    if (loadingIndicator) {
      loadingIndicator.style.display = "none";
    }
  }

  /**
   * Mostra un messaggio di errore
   * @param {string} message - Messaggio di errore
   */
  showError(message) {
    // Verifica che il componente toast sia registrato
    if (!customElements.get("toast-notification")) {
      console.error("Toast notification component not registered");
      alert(message); // Fallback
      return;
    }

    const toast = document.createElement("toast-notification");
    toast.setAttribute("type", "error");
    toast.setAttribute("message", message);
    document.body.appendChild(toast);
  }

  /**
   * Utility per debounce delle funzioni
   * @param {Function} func - Funzione da debounce
   * @param {number} wait - Tempo di attesa in ms
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Inizializza la pagina quando il DOM è caricato
document.addEventListener("DOMContentLoaded", () => {
  new SchemaPage();
});
