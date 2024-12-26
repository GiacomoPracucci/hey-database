/**
 * SchemaService
 *
 * Gestisce la logica di business per la visualizzazione e interazione con lo schema del database.
 * Si occupa di:
 * - Recuperare e formattare i metadati dello schema
 * - Gestire le relazioni tra tabelle
 * - Organizzare il layout del grafo
 * - Gestire lo stato della visualizzazione
 */
import { apiService } from "./api-service.js";

class SchemaService {
  constructor() {
    this.endpoints = {
      metadata: "/schema/api/metadata",
    };

    // Cache per i metadati dello schema
    this._schemaMetadata = null;
  }

  /**
   * Recupera i metadati dello schema
   * @returns {Promise} Promise con i metadati formattati
   */
  async getSchemaMetadata() {
    // Usa la cache se disponibile
    if (this._schemaMetadata) {
      return this._schemaMetadata;
    }

    const response = await apiService.get(this.endpoints.metadata);

    if (response.success) {
      this._schemaMetadata = this.formatSchemaData(response.data);
      return this._schemaMetadata;
    }

    throw new Error("Errore nel recupero dei metadati dello schema");
  }

  /**
   * Formatta i dati dello schema per l'utilizzo nel grafo
   * @param {Object} rawData
   * @returns {Object} Dati formattati
   */
  formatSchemaData(rawData) {
    const elements = [];

    // Processa le tabelle
    rawData.tables.forEach((table) => {
      // Aggiunge informazioni FK alle colonne
      const tableData = { ...table };
      if (tableData.columns) {
        tableData.columns = tableData.columns.map((col) => ({
          ...col,
          isForeignKey: this.isColumnForeignKey(col.name, table.relationships),
        }));
      }

      // Crea il nodo per la tabella
      elements.push({
        group: "nodes",
        data: {
          id: table.name,
          tableData: tableData,
        },
        classes: ["table-node"],
      });

      // Crea gli archi per le relazioni
      if (Array.isArray(table.relationships)) {
        table.relationships.forEach((rel, index) => {
          elements.push({
            group: "edges",
            data: {
              id: `edge-${table.name}-${rel.toTable}-${index}`,
              source: table.name,
              target: rel.toTable,
              relationship: rel.type,
              fromColumns: rel.fromColumns,
              toColumns: rel.toColumns,
            },
          });
        });
      }
    });

    return { elements };
  }

  /**
   * Verifica se una colonna è una foreign key
   * @param {string} columnName
   * @param {Array} relationships
   * @returns {boolean}
   */
  isColumnForeignKey(columnName, relationships) {
    if (!Array.isArray(relationships)) return false;

    return relationships.some((rel) => rel.fromColumns.includes(columnName));
  }

  /**
   * Calcola il layout ottimale per il grafo
   * @param {Object} graphData
   * @returns {Object} Configurazione del layout
   */
  calculateOptimalLayout(graphData) {
    const nodeCount = graphData.elements.filter(
      (el) => el.group === "nodes"
    ).length;

    // Layout gerarchico per grafi grandi
    if (nodeCount > 10) {
      return {
        name: "dagre",
        rankDir: "TB",
        rankSep: 100,
        nodeSep: 80,
        padding: 50,
      };
    }

    // Layout organico per grafi piccoli
    return {
      name: "cose",
      idealEdgeLength: 150,
      nodeOverlap: 20,
      refresh: 20,
      padding: 30,
      randomize: false,
      componentSpacing: 150,
      nodeRepulsion: 400000,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
    };
  }

  /**
   * Recupera i dettagli di una tabella specifica
   * @param {string} tableName
   * @returns {Promise<Object>} Dettagli della tabella
   */
  async getTableDetails(tableName) {
    const schema = await this.getSchemaMetadata();
    const tableNode = schema.elements.find(
      (el) => el.group === "nodes" && el.data.id === tableName
    );

    if (!tableNode) {
      throw new Error(`Tabella ${tableName} non trovata`);
    }

    // Trova tutte le relazioni che coinvolgono questa tabella
    const relationships = schema.elements
      .filter(
        (el) =>
          el.group === "edges" &&
          (el.data.source === tableName || el.data.target === tableName)
      )
      .map((edge) => ({
        type: edge.data.source === tableName ? "outgoing" : "incoming",
        from: edge.data.source,
        to: edge.data.target,
        fromColumns: edge.data.fromColumns,
        toColumns: edge.data.toColumns,
      }));

    return {
      ...tableNode.data.tableData,
      relationships,
    };
  }

  /**
   * Trova i percorsi tra due tabelle
   * @param {string} sourceTable
   * @param {string} targetTable
   * @returns {Array} Array di percorsi possibili
   */
  async findTablePaths(sourceTable, targetTable) {
    const schema = await this.getSchemaMetadata();
    const paths = [];
    const visited = new Set();

    const findPaths = (current, path = []) => {
      if (current === targetTable) {
        paths.push([...path, current]);
        return;
      }

      visited.add(current);

      const edges = schema.elements.filter(
        (el) =>
          el.group === "edges" &&
          (el.data.source === current || el.data.target === current)
      );

      for (const edge of edges) {
        const next =
          edge.data.source === current ? edge.data.target : edge.data.source;

        if (!visited.has(next)) {
          findPaths(next, [...path, current]);
        }
      }

      visited.delete(current);
    };

    findPaths(sourceTable);
    return paths;
  }
}

// Esporta un'istanza singola del servizio
export const schemaService = new SchemaService();
