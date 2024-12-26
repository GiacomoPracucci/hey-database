/**
 * DOMUtils
 *
 * Utility functions per manipolazione DOM e gestione eventi
 */

/**
 * Crea un debounce function
 * @param {Function} func
 * @param {number} wait
 * @returns {Function}
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Aggiunge più event listener contemporaneamente
 * @param {Element} element
 * @param {Object} events
 */
export function addEventListeners(element, events) {
  Object.entries(events).forEach(([event, handler]) => {
    element.addEventListener(event, handler);
  });
}

/**
 * Rimuove più event listener contemporaneamente
 * @param {Element} element
 * @param {Object} events
 */
export function removeEventListeners(element, events) {
  Object.entries(events).forEach(([event, handler]) => {
    element.removeEventListener(event, handler);
  });
}

/**
 * Crea un elemento con attributi e children
 * @param {string} tag
 * @param {Object} attributes
 * @param {Array} children
 * @returns {Element}
 */
export function createElement(tag, attributes = {}, children = []) {
  const element = document.createElement(tag);

  Object.entries(attributes).forEach(([key, value]) => {
    if (key === "className") {
      element.className = value;
    } else {
      element.setAttribute(key, value);
    }
  });

  children.forEach((child) => {
    if (typeof child === "string") {
      element.appendChild(document.createTextNode(child));
    } else {
      element.appendChild(child);
    }
  });

  return element;
}
