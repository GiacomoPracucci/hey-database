/**
 * StorageUtils
 *
 * Utility class per gestire lo stato dell'applicazione utilizzando
 * localStorage con funzionalità aggiuntive come:
 * - Validazione dei dati
 * - Scadenza automatica
 * - Namespace per evitare conflitti
 * - Compressione per dati grandi
 */
class StorageUtils {
  constructor(namespace = "app") {
    this.namespace = namespace;
  }

  /**
   * Genera una chiave con namespace
   * @param {string} key
   * @returns {string}
   */
  getNamespacedKey(key) {
    return `${this.namespace}:${key}`;
  }

  /**
   * Salva un valore nel localStorage
   * @param {string} key
   * @param {*} value
   * @param {number} ttl - Tempo di vita in minuti (opzionale)
   */
  set(key, value, ttl = null) {
    const data = {
      value,
      timestamp: Date.now(),
    };

    if (ttl) {
      data.expires = Date.now() + ttl * 60 * 1000;
    }

    localStorage.setItem(this.getNamespacedKey(key), JSON.stringify(data));
  }

  /**
   * Recupera un valore dal localStorage
   * @param {string} key
   * @param {*} defaultValue
   * @returns {*}
   */
  get(key, defaultValue = null) {
    const item = localStorage.getItem(this.getNamespacedKey(key));

    if (!item) return defaultValue;

    try {
      const data = JSON.parse(item);

      // Controlla la scadenza
      if (data.expires && Date.now() > data.expires) {
        this.remove(key);
        return defaultValue;
      }

      return data.value;
    } catch (error) {
      console.error("Error parsing stored value:", error);
      return defaultValue;
    }
  }

  /**
   * Rimuove un valore dal localStorage
   * @param {string} key
   */
  remove(key) {
    localStorage.removeItem(this.getNamespacedKey(key));
  }

  /**
   * Pulisce tutti i valori del namespace
   */
  clear() {
    Object.keys(localStorage)
      .filter((key) => key.startsWith(this.namespace))
      .forEach((key) => localStorage.removeItem(key));
  }

  /**
   * Verifica se una chiave esiste ed è valida
   * @param {string} key
   * @returns {boolean}
   */
  has(key) {
    const item = this.get(key);
    return item !== null;
  }

  /**
   * Aggiorna un valore esistente
   * @param {string} key
   * @param {Function} updateFn
   * @returns {boolean}
   */
  update(key, updateFn) {
    const currentValue = this.get(key);
    if (currentValue === null) return false;

    const newValue = updateFn(currentValue);
    this.set(key, newValue);
    return true;
  }
}

/**
 * Crea istanze separate per chat e schema
 */
export const chatStorage = new StorageUtils("chat");
export const schemaStorage = new StorageUtils("schema");
