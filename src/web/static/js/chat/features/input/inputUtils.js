/**
 * Utility per la gestione e manipolazione dell'input nella chat.
 * Fornisce funzioni helper per validazione, formattazione e manipolazione del testo.
 */

/**
 * Funzioni di validazione dell'input
 */
export const InputValidator = {
  /**
   * Verifica se una stringa è vuota o contiene solo spazi
   * @param {string} text - Testo da validare
   * @returns {boolean} true se il testo è vuoto o solo spazi
   */
  isEmpty(text) {
    return !text || text.trim().length === 0;
  },

  /**
   * Verifica se un testo supera la lunghezza massima
   * @param {string} text - Testo da validare
   * @param {number} maxLength - Lunghezza massima consentita
   * @returns {boolean} true se il testo è troppo lungo
   */
  isOverMaxLength(text, maxLength) {
    return text.length > maxLength;
  },

  /**
   * Verifica se un testo contiene caratteri non consentiti
   * @param {string} text - Testo da validare
   * @returns {boolean} true se sono presenti caratteri non validi
   */
  hasInvalidCharacters(text) {
    // Esempio: caratteri di controllo non stampabili
    const invalidCharsRegex = /[\x00-\x08\x0B-\x0C\x0E-\x1F]/;
    return invalidCharsRegex.test(text);
  },

  /**
   * Valida una query SQL basilare
   * @param {string} text - Testo da validare
   * @returns {boolean} true se il testo sembra una query SQL
   */
  looksLikeSQL(text) {
    const sqlKeywords = /\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN)\b/i;
    return sqlKeywords.test(text);
  },
};

/**
 * Funzioni di formattazione del testo
 */
export const TextFormatter = {
  /**
   * Rimuove gli spazi extra da una stringa
   * @param {string} text - Testo da formattare
   * @returns {string} Testo formattato
   */
  normalizeSpaces(text) {
    return text.replace(/\s+/g, " ").trim();
  },

  /**
   * Capitalizza la prima lettera di ogni frase
   * @param {string} text - Testo da formattare
   * @returns {string} Testo formattato
   */
  capitalizeSentences(text) {
    return text.replace(
      /(^|\.\s+)([a-z])/g,
      (match, separator, letter) => separator + letter.toUpperCase()
    );
  },

  /**
   * Formatta il testo come query SQL (basilare)
   * @param {string} text - Testo da formattare
   * @returns {string} Query SQL formattata
   */
  formatAsSQL(text) {
    return text
      .replace(/\s+/g, " ")
      .replace(/\s*(,)\s*/g, "$1 ")
      .replace(/\s*(=)\s*/g, " $1 ")
      .trim();
  },

  /**
   * Converte markdown basilare in HTML
   * @param {string} text - Testo markdown
   * @returns {string} HTML formattato
   */
  markdownToHtml(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
      .replace(/\n/g, "<br>");
  },
};

/**
 * Funzioni di manipolazione del testo
 */
export const TextManipulator = {
  /**
   * Inserisce testo in una posizione specifica
   * @param {string} originalText - Testo originale
   * @param {string} insertText - Testo da inserire
   * @param {number} position - Posizione di inserimento
   * @returns {string} Nuovo testo
   */
  insertAt(originalText, insertText, position) {
    return (
      originalText.slice(0, position) +
      insertText +
      originalText.slice(position)
    );
  },

  /**
   * Sostituisce una porzione di testo
   * @param {string} originalText - Testo originale
   * @param {number} start - Inizio selezione
   * @param {number} end - Fine selezione
   * @param {string} replacementText - Testo sostitutivo
   * @returns {string} Nuovo testo
   */
  replaceRange(originalText, start, end, replacementText) {
    return (
      originalText.slice(0, start) + replacementText + originalText.slice(end)
    );
  },

  /**
   * Avvolge il testo selezionato con stringhe di apertura e chiusura
   * @param {string} text - Testo originale
   * @param {number} start - Inizio selezione
   * @param {number} end - Fine selezione
   * @param {string} openTag - Stringa di apertura
   * @param {string} closeTag - Stringa di chiusura
   * @returns {string} Nuovo testo
   */
  wrapSelection(text, start, end, openTag, closeTag) {
    return (
      text.slice(0, start) +
      openTag +
      text.slice(start, end) +
      closeTag +
      text.slice(end)
    );
  },
};

/**
 * Funzioni di analisi del testo
 */
export const TextAnalyzer = {
  /**
   * Conta le parole in un testo
   * @param {string} text - Testo da analizzare
   * @returns {number} Numero di parole
   */
  wordCount(text) {
    return text.trim().split(/\s+/).length;
  },

  /**
   * Conta i caratteri in un testo
   * @param {string} text - Testo da analizzare
   * @param {boolean} [countSpaces=true] - Se contare gli spazi
   * @returns {number} Numero di caratteri
   */
  charCount(text, countSpaces = true) {
    return countSpaces ? text.length : text.replace(/\s/g, "").length;
  },

  /**
   * Ottiene le statistiche del testo
   * @param {string} text - Testo da analizzare
   * @returns {Object} Statistiche del testo
   */
  getTextStats(text) {
    return {
      characters: this.charCount(text),
      words: this.wordCount(text),
      lines: text.split("\n").length,
      spaces: text.split(" ").length - 1,
    };
  },

  /**
   * Calcola la posizione relativa del cursore
   * @param {string} text - Testo completo
   * @param {number} cursorPos - Posizione del cursore
   * @returns {Object} Informazioni sulla posizione
   */
  getCursorContext(text, cursorPos) {
    const textBefore = text.substring(0, cursorPos);
    const currentLine = textBefore.split("\n").length;
    const currentCol = textBefore.split("\n").pop().length + 1;

    return {
      line: currentLine,
      column: currentCol,
      wordIndex: this.wordCount(textBefore),
    };
  },
};

/**
 * Cache per ottimizzare le operazioni ricorrenti
 */
export class TextCache {
  constructor() {
    this.cache = new Map();
  }

  /**
   * Memorizza un risultato in cache
   * @param {string} key - Chiave di cache
   * @param {*} value - Valore da memorizzare
   * @param {number} [ttl=60000] - Tempo di vita in ms (default 1 minuto)
   */
  set(key, value, ttl = 60000) {
    const expiresAt = Date.now() + ttl;
    this.cache.set(key, { value, expiresAt });
  }

  /**
   * Recupera un valore dalla cache
   * @param {string} key - Chiave di cache
   * @returns {*|null} Valore memorizzato o null se scaduto/non trovato
   */
  get(key) {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.value;
  }

  /**
   * Pulisce le entry scadute dalla cache
   */
  cleanup() {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
      }
    }
  }
}

// Esporta un'istanza della cache per uso condiviso
export const textCache = new TextCache();
