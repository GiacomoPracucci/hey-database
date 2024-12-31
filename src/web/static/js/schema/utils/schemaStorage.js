// ancora inutilizzato perchè non funziona a dovere

/**
 * Gestisce la persistenza dello stato del grafo dello schema
 * Memorizza e recupera le informazioni di layout, zoom, elementi evidenziati, ecc.
 */
export class SchemaStorage {
  constructor() {
    this.STORAGE_KEY = "schema_state";
  }

  /**
   * Salva lo stato corrente del grafo
   * @param {Object} state Stato da salvare
   */
  saveState(state) {
    try {
      const stateData = {
        ...state,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(stateData));
      return true;
    } catch (error) {
      console.error("Error saving schema state:", error);
      return false;
    }
  }

  /**
   * Recupera lo stato salvato
   * @returns {Object|null} Stato salvato o null se non presente
   */
  loadState() {
    try {
      const savedState = localStorage.getItem(this.STORAGE_KEY);
      return savedState ? JSON.parse(savedState) : null;
    } catch (error) {
      console.error("Error loading schema state:", error);
      return null;
    }
  }

  /**
   * Cancella lo stato salvato
   */
  clearState() {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      return true;
    } catch (error) {
      console.error("Error clearing schema state:", error);
      return false;
    }
  }

  /**
   * Verifica se esiste uno stato salvato
   * @returns {boolean}
   */
  hasState() {
    return !!localStorage.getItem(this.STORAGE_KEY);
  }
}

// Creiamo un'istanza singola del servizio
export const schemaStorage = new SchemaStorage();
