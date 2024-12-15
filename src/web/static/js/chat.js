document.addEventListener('DOMContentLoaded', () => {
    // Elementi DOM
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');

    // Costante per la chiave di storage
    const CHAT_STORAGE_KEY = 'chat_messages';

    // Funzione per salvare i messaggi nel localStorage
    function saveChatMessages() {
        const messages = Array.from(chatMessages.children)
            .filter(msg => !msg.classList.contains('welcome') && !msg.classList.contains('typing-indicator-container'))
            .map(msg => {
                const isUser = msg.classList.contains('user');
                const content = msg.querySelector('.message-content');
                
                if (isUser) {
                    return {
                        type: 'user',
                        content: content.textContent
                    };
                } else {
                    // Per i messaggi del bot, dobbiamo verificare se è un errore o una risposta normale
                    const errorContainer = content.querySelector('.error-container');
                    if (errorContainer) {
                        // È un messaggio di errore
                        return {
                            type: 'bot',
                            isError: true,
                            error: content.querySelector('.error-details').textContent,
                            query: content.querySelector('.error-query code')?.textContent || null
                        };
                    } else {
                        // È una risposta normale del bot
                        const queryContainer = content.querySelector('.sql-query-container');
                        return {
                            type: 'bot',
                            isError: false,
                            query: queryContainer?.querySelector('.sql-query code')?.textContent || null,
                            explanation: content.querySelector('.explanation')?.textContent || null,
                            originalQuestion: queryContainer?.dataset.originalQuestion || null,
                            results: extractTableData(content.querySelector('.results-table'))
                        };
                    }
                }
            });
        
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
    }

    // Helper per estrarre i dati della tabella
    function extractTableData(table) {
        if (!table) return null;
        
        const results = [];
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
        
        table.querySelectorAll('tbody tr').forEach(tr => {
            const row = {};
            Array.from(tr.children).forEach((td, index) => {
                row[headers[index]] = td.textContent;
            });
            results.push(row);
        });
        
        return results;
    }

    // Funzione per ripristinare i messaggi dal localStorage
    function restoreChatMessages() {
        const savedMessages = localStorage.getItem(CHAT_STORAGE_KEY);
        if (!savedMessages) return;

        try {
            const messages = JSON.parse(savedMessages);
            messages.forEach(msg => {
                if (msg.type === 'user') {
                    addMessage(msg.content, 'user');
                } else if (msg.isError) {
                    addMessage({
                        success: false,
                        error: msg.error,
                        query: msg.query
                    }, 'bot');
                } else {
                    addMessage({
                        success: true,
                        query: msg.query,
                        explanation: msg.explanation,
                        original_question: msg.originalQuestion,
                        results: msg.results
                    }, 'bot');
                }
            });
        } catch (error) {
            console.error('Error restoring chat messages:', error);
            localStorage.removeItem(CHAT_STORAGE_KEY);
        }
    }

    // Funzione per resettare la chat
    function clearChat() {
        // Rimuove tutti i messaggi tranne il messaggio di benvenuto
        const welcomeMessage = chatMessages.querySelector('.message.bot.welcome');
        const typingIndicator = chatMessages.querySelector('.typing-indicator-container');
        
        // Salva i riferimenti ai messaggi da preservare
        const preservedElements = [];
        if (welcomeMessage) preservedElements.push(welcomeMessage);
        if (typingIndicator) preservedElements.push(typingIndicator);
        
        // Pulisce il contenitore dei messaggi
        chatMessages.innerHTML = '';
        
        // Ripristina gli elementi preservati
        preservedElements.forEach(element => {
            chatMessages.appendChild(element);
        });
        
        // Pulisce il localStorage
        localStorage.removeItem(CHAT_STORAGE_KEY);
        
        // Resetta l'input utente
        if (userInput) {
            userInput.value = '';
            adjustTextareaHeight();
        }
        
        // Mostra un toast di conferma
        showToast('success', 'Chat cleared successfully', 'fa-check');
    }

    // Aggiungiamo l'event listener per il pulsante clear
    const clearButton = document.querySelector('.navbar-actions button');
    if (clearButton) {
        clearButton.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Disabilita temporaneamente il pulsante per evitare click multipli
            clearButton.disabled = true;
            
            // Esegue il clear
            clearChat();
            
            // Riabilita il pulsante dopo un breve delay
            setTimeout(() => {
                clearButton.disabled = false;
            }, 500);
        });
    }

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

    function showToast(type, message, icon = null) {
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let iconHtml = '';
        if (icon) {
            iconHtml = `<i class="fas ${icon}"></i>`;
        }
        
        toast.innerHTML = `${iconHtml}${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    async function handleFeedback(button, data) {
        try {
            const response = await fetch('/chat/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
    
            if (response.ok) {
                button.classList.add('voted');
                button.disabled = true;
                button.title = 'Response marked as correct';
                showToast('success', 'Thank you for your feedback!', 'fa-check');
            } else {
                const responseData = await response.json();
                if (responseData.error === 'vector_store_disabled') {
                    showToast('warning', 'Please, enable vectorstore in config.yaml to use this feature', 'fa-exclamation-triangle');
                } else {
                    showToast('error', 'Errore nell\'invio del feedback', 'fa-times');
                }
            }
        } catch (err) {
            console.error('Error submitting feedback:', err);
            showToast('error', 'Error submitting feedback', 'fa-times');
        }
    }

    function addMessage(content, type = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
    
        if (type === 'bot') {
            if (!content.success) {
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
                if (content.query) {
                    const queryContainer = document.createElement('div');
                    queryContainer.className = 'sql-query-container';

                    const sqlLabel = document.createElement('span');
                    sqlLabel.className = 'sql-label';
                    sqlLabel.textContent = 'SQL';
                    queryContainer.appendChild(sqlLabel);
                    
                    queryContainer.dataset.originalQuestion = content.original_question;
                    
                    const toolbar = document.createElement('div');
                    toolbar.className = 'sql-query-toolbar';
                    
                    toolbar.appendChild(createCopyButton(content.query));
                    
                    const feedbackButton = document.createElement('button');
                    feedbackButton.className = 'feedback-button';
                    feedbackButton.innerHTML = '<i class="fas fa-thumbs-up"></i>';
                    feedbackButton.title = 'Mark as correct answer';
                    
                    feedbackButton.addEventListener('click', async () => {
                        await handleFeedback(feedbackButton, {
                            question: content.original_question,
                            sql_query: content.query,
                            explanation: content.explanation
                        });
                    });
                    
                    toolbar.appendChild(feedbackButton);
                    queryContainer.appendChild(toolbar);
                    
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
                    
                    const thead = document.createElement('thead');
                    const headerRow = document.createElement('tr');
                    Object.keys(content.results[0]).forEach(key => {
                        const th = document.createElement('th');
                        th.textContent = key;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);
                    table.appendChild(thead);
                    
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
        
        // Salva i messaggi dopo ogni aggiunta
        saveChatMessages();
    }

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

    function removeLoadingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        userInput.disabled = true;
        sendButton.disabled = true;
        
        addMessage(message, 'user');
        userInput.value = '';
        adjustTextareaHeight();
        
        addLoadingIndicator();
        
        try {
            const response = await fetch('/chat/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (data.from_vector_store) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
            
            removeLoadingIndicator();
            addMessage(data, 'bot');
            
        } catch (error) {
            removeLoadingIndicator();
            addMessage({
                success: false,
                error: 'Errore di comunicazione con il server'
            }, 'bot');
        } finally {
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

    // Pulisci il localStorage al caricamento della pagina (non alla navigazione)
    if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
        localStorage.removeItem(CHAT_STORAGE_KEY);
    } else {
        // Ripristina i messaggi solo durante la navigazione SPA
        restoreChatMessages();
    }

    // Imposta l'altezza iniziale della textarea
    adjustTextareaHeight();
});