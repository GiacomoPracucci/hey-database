// ancora inutilizzato perchè non funziona a dovere

import { schemaStorage } from "./schemaStorage.js";

export class SchemaState {
  constructor(cy) {
    this.cy = cy;
    this.setupAutoSave();
  }

  setupAutoSave() {
    // Utilizziamo un debounce per evitare troppi salvataggi
    let saveTimeout;
    const debouncedSave = () => {
      clearTimeout(saveTimeout);
      saveTimeout = setTimeout(() => this.saveState(), 500);
    };

    this.cy.on("layoutstop", debouncedSave);
    // Salviamo il viewport solo quando lo zoom/pan è finito
    this.cy.on("viewportChanged", debouncedSave);
  }

  saveState() {
    // Salviamo solo le informazioni essenziali
    const state = {
      viewport: {
        zoom: this.cy.zoom(),
        pan: this.cy.pan(),
      },
      layout: document.getElementById("layoutSelect")?.value || "dagre",
      // Salviamo solo gli ID dei nodi evidenziati invece che tutti gli stili
      highlightedNodes: this.cy.nodes(".highlighted").map((n) => n.id()),
      // Salviamo la posizione solo se è stata modificata manualmente
      positions: this.cy.nodes().reduce((acc, node) => {
        if (node.scratch("manuallyMoved")) {
          acc[node.id()] = node.position();
        }
        return acc;
      }, {}),
    };

    schemaStorage.saveState(state);
  }

  restoreState() {
    const state = schemaStorage.loadState();
    if (!state) return false;

    try {
      // Batch delle operazioni per migliori performance
      this.cy.batch(() => {
        // Ripristina le posizioni solo dei nodi mossi manualmente
        if (state.positions) {
          Object.entries(state.positions).forEach(([id, position]) => {
            const node = this.cy.getElementById(id);
            if (node) {
              node.position(position);
              node.scratch("manuallyMoved", true);
            }
          });
        }

        // Ripristina i nodi evidenziati
        if (state.highlightedNodes) {
          this.cy.nodes().removeClass("highlighted");
          state.highlightedNodes.forEach((id) => {
            this.cy.getElementById(id).addClass("highlighted");
          });
        }
      });

      // Ripristina il viewport
      if (state.viewport) {
        this.cy.viewport(state.viewport);
      }

      // Ripristina il layout selezionato
      const layoutSelect = document.getElementById("layoutSelect");
      if (layoutSelect && state.layout) {
        layoutSelect.value = state.layout;
      }

      return true;
    } catch (error) {
      console.error("Error restoring schema state:", error);
      return false;
    }
  }

  // Metodo per marcare un nodo come spostato manualmente
  markNodeAsMoved(nodeId) {
    const node = this.cy.getElementById(nodeId);
    if (node) {
      node.scratch("manuallyMoved", true);
    }
  }

  clearState() {
    schemaStorage.clearState();
    this.cy.nodes().forEach((node) => {
      node.removeScratch("manuallyMoved");
    });
  }
}
