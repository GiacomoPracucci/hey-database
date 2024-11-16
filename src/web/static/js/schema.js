document.addEventListener('DOMContentLoaded', () => {
    const schemaViewer = document.getElementById('schemaViewer');
    
    const cy = cytoscape({
        container: schemaViewer,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#f8f9fa',
                    'border-width': 2,
                    'border-color': '#2c3e50',
                    'width': '250px',
                    'shape': 'rectangle',
                    'content': 'data(label)',
                    'text-wrap': 'wrap',
                    'text-max-width': '230px',
                    'font-family': 'monospace',
                    'font-size': '12px',
                    'padding': '15px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                }
            },
            {
                // Stile per i nodi quando ci passi sopra il mouse
                selector: 'node:hover',
                style: {
                    'border-width': 3,
                    'border-color': '#3498db',
                    'background-color': '#ecf0f1'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#95a5a6',
                    'target-arrow-color': '#95a5a6',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.5
                }
            },
            {
                // Stile per le relazioni quando ci passi sopra il mouse
                selector: 'edge:hover',
                style: {
                    'width': 4,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db'
                }
            },
            {
                // Stile per evidenziare elementi connessi
                selector: '.highlighted',
                style: {
                    'border-color': '#3498db',
                    'border-width': 3,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db'
                }
            },
            {
                // Stile per elementi non evidenziati
                selector: '.faded',
                style: {
                    'opacity': 0.4
                }
            }
        ]
    });

    function formatTableLabel(table) {
        const lines = [];
        
        // Nome della tabella in maiuscolo
        lines.push(table.name.toUpperCase());
        lines.push('═'.repeat(30)); // Separatore più evidente
        
        // Aggiunge le colonne con dettagli
        table.columns.forEach(col => {
            const flags = [];
            if (col.isPrimaryKey) flags.push('🔑');  // Chiave primaria
            if (col.isForeignKey) flags.push('🔗');  // Foreign key
            if (!col.isNullable) flags.push('*');   // Required
            
            // Formatta: nome [tipo] flags
            const type = col.type.replace(/\([^)]*\)/g, ''); // Rimuove dimensioni dal tipo (es. VARCHAR(50) -> VARCHAR)
            const flagText = flags.length ? ` ${flags.join(' ')}` : '';
            lines.push(`${col.name} [${type}]${flagText}`);
        });
        
        return lines.join('\n');
    }

    function setupInteractivity(cy) {
        // Evidenzia le relazioni al passaggio del mouse su un nodo
        cy.on('mouseover', 'node', function(e) {
            const node = e.target;
            const connectedEdges = node.connectedEdges();
            const connectedNodes = connectedEdges.connectedNodes();
            
            // Fade out elementi non connessi
            cy.elements()
              .difference(connectedEdges.union(connectedNodes).union(node))
              .addClass('faded');
            
            // Evidenzia elementi connessi
            connectedEdges.addClass('highlighted');
            connectedNodes.addClass('highlighted');
        });

        // Rimuove l'evidenziazione quando il mouse esce dal nodo
        cy.on('mouseout', 'node', function(e) {
            cy.elements().removeClass('faded highlighted');
        });

        // Click su un edge per vedere i dettagli della relazione
        cy.on('click', 'edge', function(e) {
            const edge = e.target;
            const rel = edge.data();
            console.log('Relationship:', {
                from: rel.source,
                to: rel.target,
                type: rel.relationship
            });
            // In futuro qui mostreremo un tooltip con i dettagli della relazione
        });
    }

    async function loadSchemaData() {
        try {
            const response = await fetch('/schema/api/metadata');
            if (!response.ok) {
                throw new Error(`Failed to load schema data: ${response.statusText}`);
            }
            const result = await response.json();
            return result.data;
        } catch (error) {
            console.error('Error loading schema:', error);
            throw error;
        }
    }

    function createGraphElements(schemaData) {
        if (!schemaData || !Array.isArray(schemaData.tables)) {
            throw new Error('Invalid schema data structure');
        }

        const elements = [];

        // Nodi (tabelle)
        schemaData.tables.forEach(table => {
            elements.push({
                group: 'nodes',
                data: {
                    id: table.name,
                    label: formatTableLabel(table),
                    tableData: table // Manteniamo i dati originali per riferimento futuro
                }
            });
        });

        // Archi (relazioni)
        if (Array.isArray(schemaData.relationships)) {
            schemaData.relationships.forEach((rel, index) => {
                elements.push({
                    group: 'edges',
                    data: {
                        id: `edge-${index}`,
                        source: rel.fromTable,
                        target: rel.toTable,
                        relationship: rel.type
                    }
                });
            });
        }

        return elements;
    }

    async function initializeGraph() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'flex';
        
        try {
            const schemaData = await loadSchemaData();
            const elements = createGraphElements(schemaData);
            
            cy.elements().remove();
            cy.add(elements);
            
            // Applica il layout
            const layout = cy.layout({
                name: 'dagre',
                rankDir: 'TB',
                rankSep: 80,
                nodeSep: 50,
                padding: 50,
                animate: false,
                nodeDimensionsIncludeLabels: true
            });
            
            layout.run();
            
            // Configura l'interattività
            setupInteractivity(cy);
            
            // Centra e adatta la vista
            setTimeout(() => {
                cy.fit(50);
                cy.center();
            }, 100);
            
        } catch (error) {
            console.error('Error in graph initialization:', error);
            loadingIndicator.innerHTML = `
                <div class="error-message">
                    Failed to load schema: ${error.message}
                </div>
            `;
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // Inizializzazione
    initializeGraph();
});