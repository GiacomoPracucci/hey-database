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

    // Funzione helper per il bottone di copia
    function createCopyButton(textToCopy) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = '<i class="fas fa-copy"></i>';
        button.title = 'Copia query';
        
        button.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(textToCopy);
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('copied');
                
                // Ripristina l'icona dopo 2 secondi
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-copy"></i>';
                    button.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Errore nella copia:', err);
                button.innerHTML = '<i class="fas fa-times"></i>';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            }
        });
        
        return button;
    }

    function addMessage(content, type = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
    
        if (type === 'bot') {
            if (!content.success) {
                // Visualizzazione dell'errore
                contentDiv.innerHTML = `
                    <div class="error-container">
                        <div class="error-icon">❌</div>
                        <div class="error-message">
                            <div class="error-title">Si è verificato un errore:</div>
                            <div class="error-details">${content.error}</div>
                            ${content.query ? `
                                <div class="error-query">
                                    <div class="error-query-label">Query tentata:</div>
                                    <pre><code>${content.query}</code></pre>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            } else {
                // Visualizzazione normale della risposta
                if (content.query) {
                    const queryContainer = document.createElement('div');
                    queryContainer.className = 'sql-query-container';
                    
                    // Toolbar per i bottoni
                    const toolbar = document.createElement('div');
                    toolbar.className = 'sql-query-toolbar';
                    
                    // Bottone di copia
                    toolbar.appendChild(createCopyButton(content.query));
                    
                    // Bottone di feedback
                    const feedbackButton = document.createElement('button');
                    feedbackButton.className = 'feedback-button';
                    feedbackButton.innerHTML = '<i class="fas fa-thumbs-up"></i>';
                    feedbackButton.title = 'Segnala risposta corretta';
                    
                    feedbackButton.addEventListener('click', async () => {
                        try {
                            const response = await fetch('/api/feedback', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    question: userInput.value,  // Prendiamo la domanda dall'input utente
                                    sql_query: content.query,
                                    explanation: content.explanation
                                })
                            });
    
                            if (response.ok) {
                                // Disabilita il bottone e cambia stile
                                feedbackButton.classList.add('voted');
                                feedbackButton.disabled = true;
                                feedbackButton.title = 'Risposta segnalata come corretta';
                                
                                // Toast di conferma
                                const toast = document.createElement('div');
                                toast.className = 'toast success';
                                toast.textContent = 'Grazie per il feedback!';
                                document.body.appendChild(toast);
                                
                                // Rimuovi il toast dopo 3 secondi
                                setTimeout(() => {
                                    toast.remove();
                                }, 3000);
                            }
                        } catch (err) {
                            console.error('Errore nell\'invio del feedback:', err);
                            
                            // Toast di errore
                            const toast = document.createElement('div');
                            toast.className = 'toast error';
                            toast.textContent = 'Errore nell\'invio del feedback';
                            document.body.appendChild(toast);
                            
                            setTimeout(() => {
                                toast.remove();
                            }, 3000);
                        }
                    });
                    
                    toolbar.appendChild(feedbackButton);
                    queryContainer.appendChild(toolbar);
                    
                    // Box della query
                    const queryDiv = document.createElement('div');
                    queryDiv.className = 'sql-query';
                    queryDiv.innerHTML = `<pre><code>${content.query}</code></pre>`;
                    queryContainer.appendChild(queryDiv);
                    
                    contentDiv.appendChild(queryContainer);
                }
    
                if (content.explanation) {
                    const explanationDiv = document.createElement('div');
                    explanationDiv.className = 'explanation';
                    explanationDiv.textContent = content.explanation;
                    contentDiv.appendChild(explanationDiv);
                }
    
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
            }
        } else {
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

    // Funzione per aggiungere l'indicatore di caricamento nella chat
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'typing-indicator-container';
        loadingDiv.id = 'typingIndicator';
        
        loadingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Funzione per rimuovere l'indicatore di caricamento
    function removeLoadingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Invia il messaggio al server
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Disabilita input e bottone
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Aggiunge il messaggio dell'utente
        addMessage(message, 'user');
        userInput.value = '';
        adjustTextareaHeight();
        
        // Aggiunge l'indicatore di caricamento
        addLoadingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            // Rimuove l'indicatore di caricamento
            removeLoadingIndicator();
            
            // Aggiunge la risposta del bot
            addMessage(data, 'bot');
            
        } catch (error) {
            // Rimuove l'indicatore di caricamento
            removeLoadingIndicator();
            
            addMessage({
                success: false,
                error: 'Errore di comunicazione con il server'
            }, 'bot');
        } finally {
            // Riabilita input e bottone
            userInput.disabled = false;
            sendButton.disabled = false;
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