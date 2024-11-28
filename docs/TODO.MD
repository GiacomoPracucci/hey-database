# TODO LIST

## Chatbot SQL

1. FATTO - BASELINE - La composizione del prompt va resa dinamica:
    - attualmente, il prompt è costruito in maniera statica inserendo sample data da tutte le tabelle e tutti i metadati associati ad esse
    - TODO il prompt deve essere generato dinamicamente, inserendo solo sample data e metadati delle tabelle semanticamente simili alla user query (ricerca nel vectorstore per cosine similarity)

2. Una volta completata la baseline bisogna raffinare la ricerca di tabelle e query già in memoria da inserire nel prompt:
    - non possiamo affidarci alla sola ricerca per cosine similarity
    - qui si possono approfondire e testare n cose (ricerca ibrida embedding + full text, per parola chiave, usando reranker...)
    - liberi di testare qualsiasi soluzione, in tal senso molto interessante il discorso ontologie/knowledge graph per una costruzione di un contesto più ricco e navigabile, da cui estrarre informazioni da inserire a prompt

## Dashboarding

1. Definizione di una baseline - progettare da 0 una baseline di features che vogliamo sviluppare sia lato backend che lato frontend
2. Iniziare lo sviluppo

## Miglioramenti codice

- La classe vectorstore ha troppe responsabilità, vanno creati servizi associati ai vectorstore e strutturarli in classi:
    - connessione al client e metodi di base come creazione di una collezion ecc...
    - ricerca di documenti all'interno dello store
    - metodi per la gestione del feedback utente (non dovrebbe forse essere responsabilità sua?)

- Inserire nella codebase il concetto di agente e iniziare a creare le classi. L'idea è di avere:
    - un agente per la generazione delle query sql
    - un agente per l'enhancing dei metadati
    - un agente "analyst" per l'estrazione di insights dai dati/grafici in dashboard
    - ecc...

- Rimuovere sovraenginerizzazione di alcune dataclass/modelli? forse si potrebbe semplificare

# Bug

- Mi sembra che le foreign keys non vengano caricate correttamente nel diagramma ER sulla webapp. Testare meglio e fixare