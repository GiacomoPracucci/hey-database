/**
 * Utility per la gestione dei layout del grafo dello schema.
 * Questo modulo fornisce configurazioni e funzioni per applicare
 * diversi tipi di layout al grafo Cytoscape.
 */

/**
 * Configurazioni dei diversi tipi di layout disponibili.
 * Ogni layout è ottimizzato per un caso d'uso specifico.
 */
const layoutConfigs = {
  /**
   * Layout Dagre (Gerarchico)
   * Ottimo per visualizzare relazioni gerarchiche e dipendenze
   * Dispone i nodi in livelli dall'alto verso il basso
   */
  dagre: {
    name: "dagre",
    rankDir: "TB", // Top to Bottom - direzione del layout
    rankSep: 100, // Separazione verticale tra i livelli
    nodeSep: 80, // Separazione orizzontale tra i nodi
    padding: 50, // Padding intorno al layout
  },

  /**
   * Layout CoSE (Compound Spring Embedder)
   * Layout basato su forze fisiche, ottimo per grafi complessi
   * Produce layouts organici e ben distribuiti
   */
  cose: {
    name: "cose",
    idealEdgeLength: 150, // Lunghezza ideale degli archi
    nodeOverlap: 20, // Spazio minimo tra i nodi
    padding: 30, // Padding intorno al layout
    componentSpacing: 150, // Spazio tra componenti disconnesse
    nodeRepulsion: 400000, // Forza di repulsione tra i nodi
    edgeElasticity: 100, // Elasticità degli archi
    nestingFactor: 5, // Fattore per gestire nodi nidificati
    gravity: 80, // Forza che tiene insieme il grafo
    numIter: 1000, // Numero di iterazioni per il layout
    initialTemp: 1000, // Temperatura iniziale per il layout
    coolingFactor: 0.99, // Raffreddamento più graduale
    minTemp: 1.0, // Temperatura minima
    randomize: false, // Disabilita il posizionamento iniziale random
    refresh: 30, // Frequenza di refresh durante l'animazione
  },

  /**
   * Layout Concentrico
   * Dispone i nodi in cerchi concentrici
   * Utile per evidenziare la centralità dei nodi
   */
  concentric: {
    name: "concentric",
    minNodeSpacing: 100, // Spazio minimo tra i nodi
    concentric: (node) => node.degree(), // Funzione per determinare il livello del nodo
    levelWidth: () => 1, // Larghezza di ogni livello
  },

  /**
   * Layout a Griglia
   * Dispone i nodi in una griglia ordinata
   * Utile per visualizzazioni semplici e ordinate
   */
  grid: {
    name: "grid",
    padding: 50, // Padding intorno alla griglia
  },
};

/**
 * Applica un layout specifico al grafo Cytoscape
 *
 * @param {Object} cy - Istanza di Cytoscape.js
 * @param {string} layoutName - Nome del layout da applicare ('dagre', 'cose', 'concentric', 'grid')
 *
 * @example
 * // Applica il layout gerarchico
 * applyLayout(cy, 'dagre');
 *
 * // Applica il layout organico
 * applyLayout(cy, 'cose');
 *
 * Casi d'uso consigliati:
 * - dagre: per grafi con chiare relazioni gerarchiche
 * - cose: per grafi complessi con molte interconnessioni
 * - concentric: per evidenziare nodi centrali/importanti
 * - grid: per visualizzazioni semplici e ordinate
 */
export const applyLayout = (cy, layoutName) => {
  // Crea una nuova istanza di layout combinando:
  // 1. La configurazione specifica del layout selezionato
  // 2. Le impostazioni di animazione comuni
  const layout = cy.layout({
    // Spread della configurazione specifica del layout
    ...layoutConfigs[layoutName],

    // Impostazioni di animazione comuni a tutti i layout
    animate: true, // Abilita l'animazione
    animationDuration: 500, // Durata dell'animazione in ms
    animationEasing: "ease-in-out", // Tipo di easing per un'animazione fluida
  });

  // Avvia il layout
  layout.run();
};

/**
 * NOTA SULLE PERFORMANCE:
 *
 * 1. Layout Dagre:
 *    - Performance: O(|V| + |E|) dove V sono i nodi ed E gli archi
 *    - Migliore per grafi fino a ~1000 nodi
 *
 * 2. Layout CoSE:
 *    - Performance: O(|V|²) nel caso peggiore
 *    - Consigliato per grafi fino a ~500 nodi
 *    - Il parametro numIter influenza significativamente le performance
 *
 * 3. Layout Concentrico:
 *    - Performance: O(|V| log |V|)
 *    - Eccellente per grafi di qualsiasi dimensione
 *
 * 4. Layout Grid:
 *    - Performance: O(|V|)
 *    - Il più veloce, ideale per qualsiasi dimensione
 */
