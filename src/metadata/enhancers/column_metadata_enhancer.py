from typing import Optional
import logging

from src.models.metadata import ColumnMetadata, EnhancedColumnMetadata
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.YAKE_keywords_finder import YAKEKeywordsFinder

logger = logging.getLogger("hey-database")


class ColumnMetadataEnhancer:
    """Enhancer responsabile dell'arricchimento dei metadati delle colonne con:
    - Descrizione semantica generata via LLM
    - Keywords estratte dalla descrizione
    """

    def __init__(self, llm_handler: LLMHandler):
        self.keywords_finder = YAKEKeywordsFinder()
        self.llm_handler = llm_handler

    def enhance(self, base_metadata: ColumnMetadata) -> EnhancedColumnMetadata:
        """Arricchisce i metadati di una colonna

        Args:
            base_metadata: Metadati base della colonna

        Returns:
            EnhancerResponse con i metadati arricchiti o errore
        """
        try:
            description = self._generate_description(base_metadata)

            if not description:
                return EnhancedColumnMetadata(
                    base_metadata=base_metadata,
                    ai_name="placeholder",
                    description="No description available",
                    keywords=[],
                )

            # estrae keywords dalla descrizione generata usando l'agent dedicato
            keywords_response = self.keywords_finder.find_keywords(description)
            if not keywords_response.success:
                return EnhancedColumnMetadata(
                    base_metadata=base_metadata,
                    ai_name="placeholder",
                    description=description,
                    keywords=[],
                )

            # Crea i metadati arricchiti
            return EnhancedColumnMetadata(
                base_metadata=base_metadata,
                ai_name="placeholder",
                description=description,
                keywords=keywords_response.keywords,
            )

        except Exception as e:
            logger.exception(f"Error enhancing column metadata: {str(e)}")
            return EnhancedColumnMetadata(
                base_metadata=base_metadata,
                ai_name="placeholder",
                description="Error enhancing column metadata",
                keywords=[],
            )

    def build_prompt(self, metadata: ColumnMetadata) -> str:
        """Costruisce il prompt per la generazione della descrizione della colonna
        TODO per questa responsabilità andrebbe creata una classe a parte
        """
        prompt_parts = [
            f"""Fornisci una descrizione semantica di questa colonna di database, concentrandoti sul significato dei dati che contiene.
    
    Contesto:
    - Tabella: {metadata.table}
    - Nome Colonna: {metadata.name}
    - Tipo Dato: {metadata.data_type}
    - Nullable: {"Si" if metadata.nullable else "No"}
    - Primary Key: {"Si" if metadata.is_primary_key else "No"}
    - Foreign Key: {"Si" if metadata.is_foreign_key else "No"}"""
        ]

        if metadata.distinct_values:
            sample_values = metadata.distinct_values[:10]
            prompt_parts.append(
                f"- Esempi di valori presenti: {', '.join(map(str, sample_values))}"
            )

        prompt_parts.append("""
    Fornisci una descrizione estremamemente concisa (max 1 frase e corta) che spieghi il significato del dato contenuto nella colonna.
    La descrizione deve focalizzarsi sul significato semantico del dato, non sugli aspetti tecnici o relazionali.
    Esempio 1:
    Contesto:
    - Tabella: products
    - Nome Colonna: last_modified
    - Tipo Dato: TIMESTAMP
    - Nullable: Si
    - Primary Key: No
    - Esempi di valori presenti: 2024-01-15 14:30:00, 2024-01-16 09:45:22
    ❌ NON CORRETTO: "Timestamp che viene automaticamente aggiornato ogni volta che un record viene modificato, utile per il tracciamento"
    ✅ CORRETTO: "Data e ora dell'ultima modifica del prodotto"
                            
    Esempio 2:
    Contesto:
    - Tabella: users
    - Nome Colonna: is_active
    - Tipo Dato: CHAR(1)
    - Nullable: No
    - Primary Key: No
    - Esempi di valori presenti: Y, N
    ❌ NON CORRETTO: "Flag booleano che indica se l'utente è attualmente attivo nel sistema e può effettuare operazioni"
    ✅ CORRETTO: "Indicatore Y/N dello stato di attività dell'utente"            
             
    Non includere ragionamenti, ipotesi o assunzioni nella descrizione. Descrivi SOLO ciò che è oggettivamente presente nei dati forniti.
    IMPORTANTE: Basa la descrizione esclusivamente sui valori distinti effettivamente presenti nella colonna, senza fare inferenze su altri possibili valori.
    Esempio errato: per una colonna flag con il solo valore distinto "-", NON scrivere "Flag che può assumere valori S/N", dato che non è quello che osservi dai dati, ma limitati a descrivere il dato osservato.
         """)

        return "\n".join(prompt_parts)

    def _generate_description(self, metadata: ColumnMetadata) -> Optional[str]:
        """Genera una descrizione semantica della colonna usando il LLM"""
        prompt = self.build_prompt(metadata)

        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="Sei un esperto di database che fornisce descrizioni dettagliate e tecnicamente accurate delle colonne",
            temperature=0.05,
        )

        return description.strip() if description else None
