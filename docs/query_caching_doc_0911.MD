# Vector Store per Query Verification

## Panoramica
È stata introdotta una nuova funzionalità che permette di salvare e riutilizzare le query SQL validate dagli utenti. Il sistema ora può:

- Memorizzare coppie domanda-risposta verificate
- Recuperare risposte precedentemente validate
- Gestire feedback positivi dagli utenti
- Ridurre il carico sul modello LLM riutilizzando risposte esistenti

## Componenti Principali

1. Vector Store

    - Implementata interfaccia base VectorStore  
    - Implementato QdrantStore come prima implementazione  
    - Supporto per storage locale dei dati  
    - Gestione automatica della creazione delle collezioni  

2. Configurazione  
    ```yaml
    vector_store:
        enabled: true              # Abilita/disabilita la feature
        type: qdrant              # Tipo di vector store
        collection_name: ${db_schema}_store  # Nome dinamico della collezione
        path: ./data/${db_schema}_store     # Path per storage locale
        batch_size: 100           # Configurazione opzionale
    ```
3. UI/UX

    - Aggiunto bottone di feedback accanto alla query SQL  
    - Implementata animazione di conferma (toast)  
    - Feedback visivo per risposte già validate  
    - Gestione degli stati del bottone (attivo/disattivo)  

4. Struttura Dati
    Ogni entry nel vector store contiene:  
    ```python
    class QueryStorePayload:
        question: str          # Domanda originale
        sql_query: str         # Query SQL validata
        explanation: str       # Spiegazione in linguaggio naturale
        positive_votes: int    # Contatore feedback positivi
        created_at: datetime   # Data creazione
        last_used: datetime    # Ultimo utilizzo
    ```

## Flusso Operativo

1. Input Utente

    - L'utente inserisce una domanda  
    - Il sistema cerca match esatti nel vector store  
    - Se non trova match, procede con la generazione LLM  


2. Feedback Utente

    - L'utente può validare una risposta con il bottone di feedback  
    - La risposta viene salvata nel vector store  
    - Il contatore di voti positivi viene incrementato per match esistenti  


3. Riutilizzo

    - Per domande identiche, il sistema recupera la risposta salvata
    - Vengono aggiornati i timestamp di ultimo utilizzo
    - Viene mostrata un'animazione di caricamento realistica

## Note Tecniche
**Persistenza Dati** 

- I dati vengono salvati localmente nella directory specificata  
- La struttura delle directory viene creata automaticamente  
- Necessario use_reloader=False in Flask per evitare conflitti di accesso    

**Performance**

- Match esatto per le domande invece di similarità semantica
- Riutilizzo delle risposte validate riduce il carico sul LLM
- Storage locale per accesso veloce ai dati

**Limitazioni Note**
- Il reloader di Flask deve essere disabilitato
- Attualmente supporta solo match esatti delle domande
- Necessaria una directory locale per lo storage

**Sviluppi Futuri Possibili**
- Supporto per altri vector store
- Match approssimato per domande simili
- Interfaccia di amministrazione per gestire le entry salvate
- Migrazione a storage remoto per deployment distribuiti