/**
 * SchemaSearch gestisce tutte le funzionalità di ricerca all'interno del grafo dello schema.
 * Permette di cercare tabelle e colonne e di evidenziare i risultati nel grafo.
 */
export class SchemaSearch {
  /**
   * Inizializza il modulo di ricerca
   * @param {Object} cy - Istanza di Cytoscape.js per manipolare il grafo
   */
  constructor(cy) {
    // Memorizza il riferimento all'istanza di Cytoscape
    this.cy = cy;
    // Configura il campo di ricerca
    this.setupSearchField();
  }

  /**
   * Configura il campo di ricerca e i suoi event listener
   * Implementa il debouncing per ottimizzare le performance durante la digitazione
   */
  setupSearchField() {
    // Recupera il campo di ricerca dal DOM
    const searchInput = document.getElementById("schemaSearch");
    if (!searchInput) return;

    // Timer per il debouncing della ricerca
    let debounceTimer;

    // Listener per l'input dell'utente
    searchInput.addEventListener("input", (e) => {
      // Cancella il timer precedente se esiste
      clearTimeout(debounceTimer);
      // Imposta un nuovo timer per ritardare la ricerca
      // Questo previene troppe ricerche durante la digitazione veloce
      debounceTimer = setTimeout(() => {
        this.searchTables(e.target.value.trim());
      }, 300); // Ritardo di 300ms
    });

    // Listener per il tasto ESC
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        // Resetta il campo di ricerca
        searchInput.value = "";
        // Resetta i risultati della ricerca
        this.searchTables("");
        // Rimuovi il focus dal campo
        searchInput.blur();
      }
    });
  }

  /**
   * Esegue la ricerca nelle tabelle e nelle colonne
   * @param {string} searchTerm - Il termine di ricerca inserito dall'utente
   */
  searchTables(searchTerm) {
    // Se non c'è un termine di ricerca, ripristina lo stato originale
    if (!searchTerm) {
      // Rimuove tutte le classi di stile aggiunte durante la ricerca
      this.cy.elements().removeClass("faded highlighted search-match");
      // Ripristina l'opacità normale
      this.cy.elements().style("opacity", 1);
      return;
    }

    // Converti il termine di ricerca in minuscolo per un confronto case-insensitive
    searchTerm = searchTerm.toLowerCase();

    // Trova i nodi che corrispondono al termine di ricerca
    const matchingNodes = this.cy
      .nodes()
      .filter(this.createSearchFilter(searchTerm));

    // Evidenzia i risultati trovati
    this.highlightSearchResults(matchingNodes);
  }

  /**
   * Crea una funzione di filtro per la ricerca
   * @param {string} searchTerm - Il termine di ricerca
   * @returns {Function} Funzione di filtro che verifica se un nodo corrisponde al termine di ricerca
   */
  createSearchFilter(searchTerm) {
    return (node) => {
      // Recupera i dati della tabella dal nodo
      const tableData = node.data("tableData");
      if (!tableData) return false;

      // Verifica se il nome della tabella contiene il termine di ricerca
      // o se una qualsiasi colonna (nome o tipo) contiene il termine
      return (
        tableData.name.toLowerCase().includes(searchTerm) ||
        tableData.columns.some(
          (col) =>
            col.name.toLowerCase().includes(searchTerm) ||
            col.type.toLowerCase().includes(searchTerm)
        )
      );
    };
  }

  /**
   * Evidenzia i nodi che corrispondono ai risultati della ricerca
   * e anima il grafo per mostrare i risultati
   * @param {Object} matchingNodes - Collezione di nodi Cytoscape che corrispondono alla ricerca
   */
  highlightSearchResults(matchingNodes) {
    // Procedi solo se sono stati trovati risultati
    if (matchingNodes.length > 0) {
      // Applica l'effetto "sbiadito" a tutti gli elementi
      this.cy.elements().addClass("faded").style("opacity", 0.2);

      // Evidenzia i nodi che corrispondono alla ricerca
      matchingNodes
        .removeClass("faded") // Rimuove l'effetto sbiadito
        .addClass("search-match") // Aggiunge la classe per l'evidenziazione
        .style("opacity", 1); // Ripristina l'opacità piena

      // Evidenzia anche gli archi tra i nodi trovati
      const connectedEdges = matchingNodes.edgesWith(matchingNodes);
      connectedEdges.removeClass("faded").style("opacity", 1);

      // Anima il grafo per centrare la vista sui risultati
      this.cy.animate({
        fit: {
          eles: matchingNodes, // Elementi da inquadrare
          padding: 50, // Padding intorno agli elementi
        },
        duration: 500, // Durata dell'animazione in ms
        easing: "ease-out", // Tipo di easing per un'animazione fluida
      });
    }
  }
}
