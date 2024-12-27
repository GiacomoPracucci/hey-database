/**
 * Utils per la creazione e manipolazione degli elementi del grafo dello schema del database.
 * Questo modulo si occupa di trasformare i dati dello schema in elementi Cytoscape.
 */

/**
 * Crea gli elementi del grafo (nodi e archi) a partire dai dati dello schema
 * @param {Object} schemaData - I dati dello schema del database
 * @param {Array} schemaData.tables - Array delle tabelle del database
 * @returns {Array} Array di elementi Cytoscape (nodi e archi)
 * @throws {Error} Se la struttura dei dati dello schema non è valida
 *
 * Esempio di schemaData atteso:
 * {
 *   tables: [
 *     {
 *       name: "users",
 *       columns: [
 *         { name: "id", type: "INTEGER", isPrimaryKey: true },
 *         { name: "email", type: "VARCHAR" }
 *       ],
 *       relationships: [
 *         {
 *           fromColumns: ["role_id"],
 *           toTable: "roles",
 *           toColumns: ["id"]
 *         }
 *       ]
 *     }
 *   ]
 * }
 */
export const createGraphElements = (schemaData) => {
  // Validazione dei dati di input
  if (!schemaData || !Array.isArray(schemaData.tables)) {
    throw new Error("Invalid schema data structure");
  }

  // Array che conterrà tutti gli elementi del grafo (nodi e archi)
  const elements = [];

  // Set per tenere traccia delle foreign key
  // Usa un Set per evitare duplicati e per performance di lookup O(1)
  const foreignKeys = new Set();

  /**
   * Prima fase: Pre-processamento delle foreign key
   * Identifica tutte le colonne che sono foreign key nelle relazioni
   * e le memorizza nel Set per un accesso rapido successivo
   */
  schemaData.tables.forEach((table) => {
    if (Array.isArray(table.relationships)) {
      table.relationships.forEach((rel) => {
        // Per ogni colonna nella relazione, crea un identificatore univoco
        // nel formato "nometabella.nomecolonna"
        rel.fromColumns.forEach((col) => {
          foreignKeys.add(`${table.name}.${col}`);
        });
      });
    }
  });

  /**
   * Seconda fase: Creazione dei nodi e degli archi
   * Itera su tutte le tabelle per creare:
   * 1. I nodi che rappresentano le tabelle
   * 2. Gli archi che rappresentano le relazioni tra le tabelle
   */
  schemaData.tables.forEach((table) => {
    // Prepara i dati della tabella arricchendoli con l'informazione sulle foreign key
    const tableData = {
      ...table,
      // Mappa le colonne aggiungendo il flag isForeignKey
      columns: table.columns?.map((col) => ({
        ...col,
        // Verifica se la colonna è una foreign key usando il Set creato prima
        isForeignKey: foreignKeys.has(`${table.name}.${col.name}`),
      })),
    };

    // Crea il nodo per la tabella
    elements.push({
      group: "nodes", // Tipo di elemento Cytoscape
      data: {
        id: table.name, // ID univoco del nodo
        tableData, // Dati completi della tabella per riferimento
      },
      classes: ["table-node"], // Classi CSS per lo styling
    });

    // Se la tabella ha relazioni, crea gli archi corrispondenti
    if (Array.isArray(table.relationships)) {
      table.relationships.forEach((rel, index) => {
        // Crea un arco per ogni relazione
        elements.push({
          group: "edges", // Tipo di elemento Cytoscape
          data: {
            // Crea un ID univoco per l'arco combinando tabella sorgente,
            // tabella destinazione e indice della relazione
            id: `edge-${table.name}-${rel.toTable}-${index}`,
            source: table.name, // Tabella di origine
            target: rel.toTable, // Tabella di destinazione
            relationship: rel.type, // Tipo di relazione (se specificato)
            fromColumns: rel.fromColumns, // Colonne chiave esterna
            toColumns: rel.toColumns, // Colonne chiave referenziata
          },
        });
      });
    }
  });

  // Restituisce l'array completo di elementi pronti per essere
  // utilizzati da Cytoscape per renderizzare il grafo
  return elements;
};

/**
 * NOTA SULLA STRUTTURA DATI GENERATA:
 *
 * Gli elementi restituiti seguono questa struttura:
 *
 * Nodi (Tabelle):
 * {
 *   group: 'nodes',
 *   data: {
 *     id: String,          // Nome della tabella
 *     tableData: {         // Dati completi della tabella
 *       name: String,
 *       columns: Array,    // Colonne con flag isPrimaryKey e isForeignKey
 *       relationships: Array
 *     }
 *   },
 *   classes: ['table-node']
 * }
 *
 * Archi (Relazioni):
 * {
 *   group: 'edges',
 *   data: {
 *     id: String,          // ID univoco dell'arco
 *     source: String,      // Tabella di origine
 *     target: String,      // Tabella di destinazione
 *     relationship: String, // Tipo di relazione
 *     fromColumns: Array,  // Colonne chiave esterna
 *     toColumns: Array     // Colonne chiave referenziata
 *   }
 * }
 */
