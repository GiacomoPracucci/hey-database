# Schema ER Viewer Documentation

## Overview 

Lo Schema ER Viewer è un modulo che permette la visualizzazione interattiva dello schema del database in formato Entity-Relationship. Il sistema recupera i metadati direttamente dal database (tabelle, colonne, relazioni) e li presenta in una interfaccia grafica interattiva basata su Cytoscape.js.

## Architettura

### Backend flow

1. `Metadata retrieval`
    ```plaintext
    Request → DatabaseMetadataRetriever → SQLAlchemy Inspector → Database
    ```
    - La classe DatabaseMetadataRetriever astrae l'accesso ai metadati
    - Utilizza SQLAlchemy Inspector per recuperare informazioni sullo schema

2. `Data Transformation`

    ```python
    # struttura dei metadati
    {
    "tables": [
        {
        "name": "table_name",
        "columns": [
            {
            "name": "column_name",
            "type": "data_type",
            "isPrimaryKey": boolean,
            "isForeignKey": boolean,
            "isNullable": boolean
            }
        ],
        "relationships": [
            {
            "fromColumns": ["column_name"],
            "toTable": "referenced_table",
            "toColumns": ["referenced_column"],
            "type": "N-1"
            }
        ]
        }
    ]
    }
    ```

3. `API endpoint`
    - Route: /schema/api/metadata
    - Method: GET
    - Response: JSON con la struttura completa dello schema

### Frontend Architecture

1. `Struttura` 

    ```plaintext
    Schema Viewer
    ├── Schema Header
    │   ├── Title
    │   └── Controls (zoom, search)
    ├── Graph Container
    │   ├── Cytoscape Instance
    │   └── Loading Indicator
    └── Details Panel
        ├── Table Information
        ├── Columns List
        └── Relationships
    ```

2. `Cytoscape.js Integration`
    - Layout: Dagre (ottimizzato per grafi diretti)
    - Nodi: Rappresentano le tabelle
    - Archi: Rappresentano le relazioni foreign key
    - Stili personalizzati per nodi e archi

3. `Interactivity flow`

    ```plaintext User Action → Event Handler → State Update → Visual Update ```

## Future Improvements

1. Technical
    - Implementazione caching metadati
    - Ottimizzazione performance per schemi molto grandi
    - Supporto per tipi di relazioni complesse
    - Mantenere lo stato quando passo a pagine diverse

2. UX/UI
    - Miglioramento estetico
    - Export schema in vari formati
    - Layout personalizzabili
    - Filtri avanzati

3. Features
    - Visualizzazione dati di esempio

## Dependencies

- Cytoscape.js: ^3.28.1
- Dagre: ^0.8.5
- Cytoscape-dagre: ^2.5.0

## Usage Example

```javascript 
// Initialize viewer
const viewer = new SchemaViewer('#schemaViewer');

// Load and display schema
viewer.loadSchema()
    .then(() => {
        viewer.render();
        viewer.fit();
    })
    .catch(err => {
        console.error('Failed to load schema:', err);
    });
```
