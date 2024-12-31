import { createGraphElements } from "./utils/graphUtils.js";
import { schemaStyles } from "./config/styles.js";
import { SchemaSearch } from "./features/search.js";
import { TableDetails } from "./features/details.js";
import { SchemaControls } from "./features/controls.js";
import { applyLayout } from "./utils/layoutUtils.js";

/**
 * SchemaViewer è la classe principale che gestisce la visualizzazione
 * e l'interazione con il grafo dello schema del database.
 * Coordina tutti i moduli e le funzionalità dell'applicazione.
 */
class SchemaViewer {
  /**
   * Costruttore della classe
   * Avvia immediatamente l'inizializzazione dell'applicazione
   */
  constructor() {
    this.init();
  }

  /**
   * Inizializza l'applicazione in modo asincrono
   * Gestisce il caricamento dei dati e l'inizializzazione dei componenti
   */
  async init() {
    // Mostra l'indicatore di caricamento
    const loadingIndicator = document.getElementById("loadingIndicator");
    loadingIndicator.style.display = "flex";

    try {
      // Recupera i dati dello schema dal server
      const data = await this.fetchSchemaData();

      // Inizializza Cytoscape con i dati recuperati
      this.initializeCytoscape(data);

      // Inizializza le funzionalità aggiuntive
      this.initializeFeatures(data);

      // Nasconde l'indicatore di caricamento al completamento
      loadingIndicator.style.display = "none";
    } catch (error) {
      // Gestisce eventuali errori durante l'inizializzazione
      this.handleError(error);
    }
  }

  /**
   * Recupera i dati dello schema dal server
   * @returns {Promise<Object>} I dati dello schema del database
   * @throws {Error} Se il caricamento dei dati fallisce
   */
  async fetchSchemaData() {
    const response = await fetch("/schema/api/metadata");
    if (!response.ok) {
      throw new Error(`Failed to load schema data: ${response.statusText}`);
    }
    return (await response.json()).data;
  }

  /**
   * Inizializza l'istanza di Cytoscape.js con i dati dello schema
   * Configura il layout iniziale e le impostazioni di base
   * @param {Object} data - I dati dello schema del database
   */
  initializeCytoscape(data) {
    // Crea l'istanza di Cytoscape con le configurazioni base
    this.cy = cytoscape({
      container: document.getElementById("schemaViewer"), // Elemento DOM contenitore
      style: schemaStyles, // Stili del grafo
      elements: createGraphElements(data), // Nodi e archi
      wheelSensitivity: 0.2, // Sensibilità dello zoom con rotella
    });

    // Applica il layout gerarchico iniziale
    applyLayout(this.cy, "dagre");

    // Adatta la vista a tutti gli elementi con padding
    this.cy.fit(50);

    // Centra il grafo nel viewport
    this.cy.center();
  }

  /**
   * Inizializza tutte le funzionalità aggiuntive del visualizzatore
   * Crea le istanze dei vari moduli funzionali
   * @param {Object} data - I dati dello schema del database
   */
  initializeFeatures(data) {
    // Inizializza il modulo di ricerca
    this.search = new SchemaSearch(this.cy);

    // Inizializza il pannello dei dettagli
    this.details = new TableDetails(data);

    // Inizializza i controlli dell'interfaccia
    this.controls = new SchemaControls(this.cy);

    // Configura le interazioni con il grafo
    this.setupInteractions();
  }

  /**
   * Configura le interazioni dell'utente con il grafo
   * Gestisce eventi come hover e click sui nodi
   */
  setupInteractions() {
    // Gestisce l'hover sui nodi
    this.cy.on("mouseover", "node", (e) => {
      const node = e.target;
      const connectedEdges = node.connectedEdges(); // Archi collegati
      const connectedNodes = connectedEdges.connectedNodes(); // Nodi collegati

      // Applica l'effetto "sbiadito" agli elementi non correlati
      this.cy
        .elements()
        .difference(connectedEdges.union(connectedNodes).union(node))
        .addClass("faded");

      // Evidenzia gli elementi correlati
      connectedEdges.addClass("highlighted");
      connectedNodes.addClass("highlighted");
    });

    // Ripristina lo stato normale al termine dell'hover
    this.cy.on("mouseout", "node", () => {
      this.cy.elements().removeClass("faded highlighted");
    });

    // Gestisce il click sui nodi mostrando i dettagli
    this.cy.on("click", "node", (e) => {
      this.details.updateDetails(e.target);
    });
  }

  /**
   * Gestisce gli errori durante l'inizializzazione
   * Mostra un messaggio di errore appropriato all'utente
   * @param {Error} error - L'errore da gestire
   */
  handleError(error) {
    // Logga l'errore nella console per debug
    console.error("Error initializing schema viewer:", error);

    // Mostra un messaggio di errore user-friendly
    const loadingIndicator = document.getElementById("loadingIndicator");
    if (loadingIndicator) {
      loadingIndicator.innerHTML = `
                <div class="error-message">
                    Failed to load schema: ${error.message}
                </div>
            `;
    }
  }
}

/**
 * Inizializza l'applicazione quando il DOM è completamente caricato
 * Crea una nuova istanza del visualizzatore
 */
window.addEventListener("DOMContentLoaded", () => {
  new SchemaViewer();
});
