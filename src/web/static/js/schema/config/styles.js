/**
 * Configurazione degli stili per il grafo Cytoscape
 * Questo modulo definisce tutti gli stili visuali per nodi, archi e stati
 * del grafo dello schema del database.
 */

/**
 * Funzione helper per generare l'etichetta di un nodo
 * @param {Object} ele - Elemento Cytoscape (nodo)
 * @returns {string} Etichetta formattata del nodo
 */
const generateNodeLabel = (ele) => {
  const data = ele.data();
  if (!data.tableData) return "";

  const lines = [];

  // Intestazione della tabella
  lines.push(data.tableData.name.toUpperCase());

  // Linea separatrice
  const separatorLength = Math.min(data.tableData.name.length * 1.5, 30);
  lines.push("─".repeat(separatorLength));

  // Aggiungi le colonne chiave (PK e FK)
  if (data.tableData.columns) {
    const keyColumns = data.tableData.columns.filter(
      (col) => col.isPrimaryKey || col.isForeignKey
    );

    keyColumns.forEach((col) => {
      let line = col.name;

      // Aggiungi icone per PK e FK
      if (col.isPrimaryKey) line += " 🔑";
      if (col.isForeignKey) line += " 🔗";

      // Aggiungi il tipo pulito
      const cleanType = col.type.replace(/\([^)]*\)/g, "").toLowerCase();
      line += ` [${cleanType}]`;

      lines.push(line);
    });

    // Indica se ci sono altre colonne non mostrate
    const hiddenColumns = data.tableData.columns.length - keyColumns.length;
    if (hiddenColumns > 0) {
      lines.push(`... +${hiddenColumns} more columns`);
    }
  }

  return lines.join("\n");
};

/**
 * Array di configurazione degli stili Cytoscape
 * Definisce l'aspetto visivo di tutti gli elementi del grafo
 */
export const schemaStyles = [
  /**
   * Stile base per i nodi (tabelle)
   * Definisce l'aspetto generale dei nodi del grafo
   */
  {
    selector: "node",
    style: {
      // Stile del contenitore
      "background-color": "#ffffff",
      "border-width": 1,
      "border-color": "#e2e8f0",
      "border-opacity": 1,
      shape: "roundrectangle",

      // Dimensioni e padding
      width: "label",
      height: "label",
      padding: "20px",

      // Configurazione del testo
      "text-wrap": "wrap",
      "text-max-width": "280px",
      "text-valign": "center",
      "text-halign": "center",
      "font-family":
        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
      "font-size": "14px",
      color: "#2d3748",
      "text-margin-y": 5,

      // Dimensioni minime e arrotondamento
      "min-width": "200px",
      "min-height": "50px",
      "corner-radius": "8px",

      // Effetti visivi
      "background-opacity": 1,
      "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
      "compound-sizing-wrt-labels": "include",

      // Funzione per generare l'etichetta
      label: generateNodeLabel,
    },
  },

  /**
   * Stile per gli archi (relazioni)
   * Definisce l'aspetto delle connessioni tra i nodi
   */
  {
    selector: "edge",
    style: {
      // Stile della linea
      width: 1.5,
      "line-color": "#a0aec0",
      "line-style": "dashed",
      "curve-style": "bezier",

      // Stile della freccia
      "target-arrow-color": "#a0aec0",
      "target-arrow-shape": "triangle",
      "arrow-scale": 1,

      // Punti di connessione
      "source-endpoint": "outside-to-node",
      "target-endpoint": "outside-to-node",
    },
  },

  /**
   * Stile per i nodi evidenziati
   * Applicato quando un nodo è in stato di highlight
   */
  {
    selector: ".highlighted",
    style: {
      "border-color": "#3182ce",
      "border-width": 2,
      "border-opacity": 1,
      "background-color": "#ebf8ff",
      "transition-property": "all",
      "transition-duration": "0.2s",
    },
  },

  /**
   * Stile per i nodi selezionati
   * Applicato quando un nodo è selezionato dall'utente
   */
  {
    selector: ":selected",
    style: {
      "border-color": "#3182ce",
      "border-width": 2,
      "border-opacity": 1,
      "background-color": "#ebf8ff",
      "box-shadow": "0 0 0 3px rgba(49, 130, 206, 0.3)",
    },
  },

  /**
   * Stile per l'hover sui nodi
   * Applicato quando il mouse passa sopra un nodo
   */
  {
    selector: "node:hover",
    style: {
      "border-color": "#3182ce",
      "border-width": 1.5,
      "background-color": "#f7fafc",
      "transition-property": "all",
      "transition-duration": "0.2s",
    },
  },

  /**
   * Stile per gli elementi in stato "sbiadito"
   * Utilizzato per elementi non rilevanti nel contesto corrente
   */
  {
    selector: ".faded",
    style: {
      opacity: 0.25,
    },
  },

  /**
   * Stile per i nodi che corrispondono alla ricerca
   * Applicato ai nodi che matchano i criteri di ricerca
   */
  {
    selector: ".search-match",
    style: {
      "border-color": "#3182ce",
      "border-width": 2,
      "background-color": "#ebf8ff",
      "z-index": 999,
    },
  },

  /**
   * Stile per i nodi centrali/importanti
   * Applicato ai nodi identificati come hub o punti centrali del grafo
   */
  {
    selector: ".central-node",
    style: {
      "border-width": 3,
      "border-color": "#4299e1",
      "background-color": "#ebf8ff",
      "z-index": 900,
    },
  },

  /**
   * Stile per le relazioni evidenziate
   * Applicato agli archi quando sono parte di un percorso importante
   */
  {
    selector: ".highlighted-edge",
    style: {
      "line-color": "#4299e1",
      "target-arrow-color": "#4299e1",
      width: 2,
      "arrow-scale": 1.2,
      "z-index": 999,
    },
  },
];

/**
 * Configurazione delle animazioni per le transizioni degli stili
 * Definisce la durata e il timing delle animazioni
 */
export const animationConfig = {
  duration: 200, // Durata in millisecondi
  easing: "ease-in-out", // Funzione di easing
};

/**
 * Configurazione dei colori per gli stati dei nodi
 * Definisce la palette di colori per i vari stati
 */
export const nodeStateColors = {
  default: {
    border: "#e2e8f0",
    background: "#ffffff",
    text: "#2d3748",
  },
  highlighted: {
    border: "#3182ce",
    background: "#ebf8ff",
    text: "#2d3748",
  },
  selected: {
    border: "#3182ce",
    background: "#ebf8ff",
    text: "#2d3748",
  },
  faded: {
    opacity: 0.25,
  },
};

/**
 * Configurazione delle dimensioni e del layout
 * Definisce i valori di default per dimensioni e spaziature
 */
export const layoutConfig = {
  nodePadding: 20,
  minNodeWidth: 200,
  minNodeHeight: 50,
  textMaxWidth: 280,
  cornerRadius: 8,
  edgeWidth: 1.5,
};
