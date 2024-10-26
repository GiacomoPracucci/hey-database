document.addEventListener('DOMContentLoaded', () => {
    // Elementi DOM
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');

    // Gestisce l'altezza dinamica della textarea
    function adjustTextareaHeight() {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    }

    // Aggiunge un messaggio alla chat
    function addMessage(content, type = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (type === 'bot' && typeof content === 'object') {
            // Gestisce la risposta strutturata del bot
            if (content.success) {
                // Aggiunge la query SQL se presente
                if (content.query) {
                    const queryDiv = document.createElement('div');
                    queryDiv.className = 'sql-query';
                    queryDiv.innerHTML = `<pre><code>${content.query}</code></pre>`;
                    contentDiv.appendChild(queryDiv);
                }

                // Aggiunge la spiegazione se presente
                if (content.explanation) {
                    const explanationDiv = document.createElement('div');
                    explanationDiv.className = 'explanation';
                    explanationDiv.textContent = content.explanation;
                    contentDiv.appendChild(explanationDiv);
                }

                // Aggiunge i risultati in una tabella se presenti
                if (content.results && content.results.length > 0) {
                    const tableDiv = document.createElement('div');
                    tableDiv.className = 'results-container';
                    
                    const table = document.createElement('table');
                    table.className = 'results-table';
                    
                    // Header
                    const thead = document.createElement('thead');
                    const headerRow = document.createElement('tr');
                    Object.keys(content.results[0]).forEach(key => {
                        const th = document.createElement('th');
                        th.textContent = key;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);
                    table.appendChild(thead);
                    
                    // Body
                    const tbody = document.createElement('tbody');
                    content.results.forEach(row => {
                        const tr = document.createElement('tr');
                        Object.values(row).forEach(value => {
                            const td = document.createElement('td');
                            td.textContent = value;
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });
                    table.appendChild(tbody);
                    
                    tableDiv.appendChild(table);
                    contentDiv.appendChild(tableDiv);
                }
            } else {
                // Mostra l'errore
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = `Errore: ${content.error}`;
                contentDiv.appendChild(errorDiv);
            }
        } else {
            // Messaggio semplice (testo)
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Mostra/nasconde l'indicatore di digitazione
    function toggleTypingIndicator(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
    }

    // Invia il messaggio al server
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Disabilita input e bottone durante l'invio
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Aggiunge il messaggio dell'utente
        addMessage(message, 'user');
        userInput.value = '';
        adjustTextareaHeight();
        
        // Mostra l'indicatore di digitazione
        toggleTypingIndicator(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            addMessage(data, 'bot');
            
        } catch (error) {
            addMessage({
                success: false,
                error: 'Errore di comunicazione con il server'
            }, 'bot');
        } finally {
            // Riabilita input e bottone
            userInput.disabled = false;
            sendButton.disabled = false;
            toggleTypingIndicator(false);
            userInput.focus();
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userInput.addEventListener('input', adjustTextareaHeight);

    // Imposta l'altezza iniziale della textarea
    adjustTextareaHeight();
});