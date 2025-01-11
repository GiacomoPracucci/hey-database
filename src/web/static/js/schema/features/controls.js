import { applyLayout } from "../utils/layoutUtils.js";

/**
 * Classe SchemaControls
 * Gestisce tutti i controlli dell'interfaccia utente per la visualizzazione dello schema
 * Include controlli per zoom, layout e analisi della rete
 */
export class SchemaControls {
  /**
   * Costruttore della classe
   * @param {Object} cy - Istanza di Cytoscape.js
   */
  constructor(cy) {
    // Salviamo il riferimento all'istanza di Cytoscape
    this.cy = cy;

    // Inizializziamo tutti i controlli
    this.setupZoomControls();
    this.setupLayoutControls();
    this.setupVisualizationControls();
  }

  /**
   * Configura i controlli dello zoom
   * Gestisce le funzionalità di zoom in, zoom out e fit to screen
   */
  setupZoomControls() {
    // Costante per il fattore di zoom (20% per click)
    const ZOOM_STEP = 1.2;

    // Zoom In
    const zoomInBtn = document.getElementById("zoomIn");
    if (zoomInBtn) {
      zoomInBtn.addEventListener("click", () => {
        this.cy.animate({
          zoom: this.cy.zoom() * ZOOM_STEP,
          duration: 200,
          easing: "ease-out",
        });
      });
    }

    // Zoom Out
    const zoomOutBtn = document.getElementById("zoomOut");
    if (zoomOutBtn) {
      zoomOutBtn.addEventListener("click", () => {
        this.cy.animate({
          zoom: this.cy.zoom() / ZOOM_STEP,
          duration: 200,
          easing: "ease-out",
        });
      });
    }

    // Fit to Screen (adatta la vista a tutti gli elementi)
    const zoomFitBtn = document.getElementById("zoomFit");
    if (zoomFitBtn) {
      zoomFitBtn.addEventListener("click", () => {
        this.cy.animate({
          fit: {
            padding: 50, // padding intorno agli elementi
          },
          duration: 300,
          easing: "ease-out",
        });
      });
    }
  }

  /**
   * Configura i controlli del layout
   * Gestisce la selezione e l'applicazione dei diversi tipi di layout
   */
  setupLayoutControls() {
    // Bottone per l'arrangiamento automatico
    const autoArrangeBtn = document.getElementById("autoArrangeBtn");
    if (autoArrangeBtn) {
      autoArrangeBtn.addEventListener("click", () => {
        this.applySmartLayout();
      });
    }

    // Selezione del tipo di layout
    const layoutSelect = document.getElementById("layoutSelect");
    if (layoutSelect) {
      layoutSelect.addEventListener("change", (e) => {
        applyLayout(this.cy, e.target.value);
      });
    }
  }

  /**
   * Analizza le metriche della rete e applica il layout più appropriato
   * Usa diverse metriche per determinare il miglior layout da utilizzare
   */
  applySmartLayout() {
    // Analizziamo prima le metriche della rete
    const metrics = this.analyzeNetworkMetrics();
    const components = metrics.components;

    // Resettiamo gli stili prima di applicare il nuovo layout
    this.cy.nodes().style({
      "border-width": 1,
      "border-color": "#e2e8f0",
    });

    // Scegliamo il layout appropriato basandoci sulla struttura della rete
    if (components.length === 1 && components[0].length > 10) {
      // Per grafi grandi e connessi, usiamo un layout gerarchico
      this.cy
        .layout({
          name: "dagre",
          rankDir: "TB",
          rankSep: 100,
          nodeSep: 80,
          padding: 50,
          animate: true,
          animationDuration: 500,
          fit: true,
        })
        .run();
    } else if (components.length > 1) {
      // Per multiple componenti, disponiamo ogni componente separatamente
      this.handleMultipleComponents(components);
    } else {
      // Per grafi piccoli usiamo il layout CoSE
      this.cy
        .layout({
          name: "cose",
          animate: true,
          animationDuration: 500,
          fit: true,
          padding: 50,
          nodeRepulsion: 400000,
        })
        .run();
    }

    // Evidenziamo i nodi più importanti
    this.highlightImportantNodes(metrics);
  }

  /**
   * Gestisce il layout per grafi con multiple componenti
   * @param {Array} components - Array delle componenti del grafo
   */
  handleMultipleComponents(components) {
    components.forEach((component) => {
      const componentCy = this.cy.collection(component);
      componentCy
        .layout({
          name: "cose",
          animate: true,
          animationDuration: 500,
          fit: false,
          padding: 50,
          nodeRepulsion: 400000,
          componentSpacing: 150,
        })
        .run();
    });

    // Fit alla vista dopo aver disposto le componenti
    setTimeout(() => {
      this.cy.fit(50);
    }, 600);
  }

  /**
   * Evidenzia i nodi importanti basandosi sulle metriche
   * @param {Object} metrics - Metriche della rete calcolate
   */
  highlightImportantNodes(metrics) {
    // Reset iniziale con transizione fluida
    this.cy.nodes().style({
      'background-color': '#ffffff',
      'border-width': 1,
      'border-color': '#3182ce',
      'transition-property': 'background-color, border-width, border-color',
      'transition-duration': '0.3s',
      'transition-timing-function': 'ease-in-out'
    });

    // Calcola il grado massimo
    let maxDegree = 0;
    this.cy.nodes().forEach(node => {
      const connections = node.connectedEdges().length;
      maxDegree = Math.max(maxDegree, connections);
    });

    // Applica gli stili in base alla centralità
    this.cy.nodes().forEach(node => {
      const connections = node.connectedEdges().length;
      const intensity = connections / maxDegree;

      if (intensity > 0.20) {
        // Normalizza l'intensità per i nodi sopra la soglia
        const normalizedIntensity = (intensity - 0.2) / 0.8;

        // Funzione per interpolare colori in HSL
        const getColor = (intensity) => {
          // Interpola da un blu chiaro a un blu scuro
          const h = 215;  // Tonalità blu
          const s = 40 + (intensity * 40);  // Saturazione da 40% a 80%
          const l = 90 - (intensity * 30);  // Luminosità da 90% a 60%
          return `hsl(${h}, ${s}%, ${l}%)`;
        };

        // Calcola dimensione del bordo con un limite massimo
        const borderWidth = Math.min(1 + (normalizedIntensity * 3), 4);

        // Applica gli stili migliorati
        node.style({
          'background-color': getColor(normalizedIntensity),
          'border-width': borderWidth,
          'border-color': '#2b6cb0', // Blu leggermente più scuro per il bordo
          'z-index': Math.floor(900 + (normalizedIntensity * 99)), // z-index progressivo
          // Aggiunge un sottile effetto di box shadow usando il filtro CSS
          'overlay-opacity': 0.1,
          'overlay-color': '#000000',
          'overlay-padding': normalizedIntensity * 5
        });

        // Aggiungi classe per stili CSS aggiuntivi
        node.addClass('highlighted');
      } else {
        // Rimuovi classe se il nodo non è più evidenziato
        node.removeClass('highlighted');
      }
    });
  }

  /**
   * Analizza le metriche della rete
   * Calcola varie metriche come centralità e componenti connesse
   * @returns {Object} Oggetto contenente le metriche calcolate
   */
  analyzeNetworkMetrics() {
    // Calcolo della degree centrality
    const degreeCentrality = {};
    this.cy.nodes().forEach((node) => {
      degreeCentrality[node.id()] = node.degree();
    });

    // Calcolo della betweenness centrality
    const betweennessCentrality = this.cy.elements().bc();

    // Identificazione delle componenti connesse
    const components = this.findConnectedComponents();

    return {
      degreeCentrality,
      betweennessCentrality,
      components,
    };
  }

  /**
   * Trova le componenti connesse nel grafo
   * @returns {Array} Array delle componenti connesse
   */
  findConnectedComponents() {
    const components = [];
    let unvisited = this.cy.nodes().toArray();

    while (unvisited.length > 0) {
      const component = [];
      const queue = [unvisited[0]];

      while (queue.length > 0) {
        const node = queue.shift();
        if (unvisited.includes(node)) {
          component.push(node);
          unvisited = unvisited.filter((n) => n !== node);

          node
            .neighborhood()
            .nodes()
            .forEach((neighbor) => {
              if (unvisited.includes(neighbor)) {
                queue.push(neighbor);
              }
            });
        }
      }

      components.push(component);
    }

    return components;
  }

  /**
   * Configura i controlli di visualizzazione aggiuntivi
   * Aggiunge controlli per la manipolazione visiva del grafo
   */
  setupVisualizationControls() {
    // Rimuoviamo l'aggiunta dinamica dei bottoni
    // this.addVisualizationControlsToUI();

    // aggiungiamo gli event listener per i controlli - ora sulla toolbar
    const toolbar = document.querySelector(".page-toolbar");
    if (toolbar) {
        toolbar.addEventListener("click", (e) => {
            const button = e.target.closest("[data-action]");
            if (button) {
                const action = button.dataset.action;
                this.handleVisualizationAction(action);
            }
        });
    }
  }

  /**
   * Gestisce le azioni di visualizzazione
   * @param {string} action - Nome dell'azione da eseguire
   */
  handleVisualizationAction(action) {
    switch (action) {
      case "highlight-central":
        const metrics = this.analyzeNetworkMetrics();
        this.highlightImportantNodes(metrics);
        break;
      case "reset":
        this.resetVisualization();
        break;
    }
  }

  /**
   * Resetta la visualizzazione allo stato iniziale
   * Rimuove tutti gli effetti di highlighting e riporta il grafo allo stato originale
   */
  resetVisualization() {
    // Ferma tutte le animazioni in corso
    this.cy.nodes().forEach((node) => {
      node.stop();
    });

    // Reset degli stili dei nodi allo stato originale
    this.cy.nodes().style({
      'background-color': '#ffffff',
      'border-width': 1,
      'border-color': '#3182ce',
      'z-index': 1,
      'overlay-opacity': 0,
      'overlay-color': '#ffffff',
      'overlay-padding': 0,
      'transition-property': 'none'  // Disabilita le transizioni per il reset
    });

    // Rimuove tutte le classi CSS aggiunte
    this.cy.nodes().removeClass('highlighted');

    // Reset della vista
    this.cy.animate({
      fit: {
        padding: 50
      },
      duration: 300,
      easing: 'ease-out'
    });
  }
}
