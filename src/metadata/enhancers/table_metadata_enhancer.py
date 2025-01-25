from typing import Optional
import logging

from src.models.metadata import TableMetadata, EnhancedTableMetadata
from src.llm_handler.llm_handler import LLMHandler
from src.keywords.YAKE_keywords_finder import YAKEKeywordsFinder

logger = logging.getLogger("hey-database")


class TableMetadataEnhancer:
    """Enhancer responsabile dell'arricchimento dei metadati delle tabelle con:
    - Descrizione semantica generata via LLM
    - Keywords estratte dalla descrizione
    - Score di importanza calcolato
    """

    def __init__(self, llm_handler: LLMHandler):
        self.keywords_finder = YAKEKeywordsFinder()  # potremmo usare anche quello LLM based che è più robusto, ma rallenteremmo il processo che già è lento
        # TODO valutare se usare LLM based extractor per keywords per le tabelle,
        # TODO che sono meno rispetto alle colonne (andrebbe generalizzato il prompt che ora parla di query, qui verrebbe passata la descrizione)
        self.llm_handler = llm_handler

    def enhance(self, base_metadata: TableMetadata) -> EnhancedTableMetadata:
        """Arricchisce i metadati di una tabella

        Args:
            base_metadata: Metadati base della tabella

        Returns:
            EnhancerResponse con i metadati arricchiti o errore
        """
        try:
            # Genera descrizione usando LLM
            description = self._generate_description(base_metadata)
            # description = "placeholder"
            if not description:
                return EnhancedTableMetadata(
                    base_metadata=base_metadata,
                    description="No description available",
                    keywords=[],
                    importance_score=0.0,
                )

            # Estrae keywords dalla descrizione
            keywords_response = self.keywords_finder.find_keywords(description)
            if not keywords_response.success:
                return EnhancedTableMetadata(
                    base_metadata=base_metadata,
                    description=description,
                    keywords=[],
                    importance_score=0.0,
                )

            importance_score = self._calculate_importance_score(base_metadata)

            return EnhancedTableMetadata(
                base_metadata=base_metadata,
                description=description,
                keywords=keywords_response.keywords,
                importance_score=importance_score,
            )

        except Exception as e:
            logger.exception(f"Error enhancing table metadata: {str(e)}")
            return EnhancedTableMetadata(
                base_metadata=base_metadata,
                description="Error enhancing metadata",
                keywords=[],
                importance_score=0.0,
            )

    def build_prompt(self, metadata: TableMetadata) -> str:
        """Costruisce il prompt per la generazione della descrizione"""

        foreign_keys_info = []
        for fk in metadata.foreign_keys:
            from_cols = ", ".join(fk["constrained_columns"])
            to_table = fk["referred_table"]
            to_cols = ", ".join(fk["referred_columns"])
            foreign_keys_info.append(f"- {from_cols} -> {to_table}({to_cols})")

        prompt = f"""Descrivi il significato business dei dati contenuti in questa tabella di database.

Table: {metadata.name}
Number of records: {metadata.row_count}

Columns:
{metadata.columns}

Primary Keys: {", ".join(metadata.primary_keys)}

Foreign Keys:
{chr(10).join(foreign_keys_info) if foreign_keys_info else "No foreign keys"}

La descrizione deve focalizzarsi sul significato semantico del dato, non sugli aspetti tecnici o relazionali.
Esempi di descrizioni efficaci:
Table: customers -> "Contiene i dati anagrafici e di contatto dei clienti, incluse informazioni su residenza e preferenze di comunicazione"
Table: orders -> "Raccoglie tutti gli ordini effettuati dai clienti, con dettagli su importi, date di acquisto e stato di elaborazione"
Table: products -> "Archivio dei prodotti in vendita con relative caratteristiche tecniche, prezzi e disponibilità in magazzino"

Non includere ragionamenti, ipotesi o assunzioni nella descrizione. Descrivi SOLO ciò che è oggettivamente presente nei dati/metadati forniti.
La descrizione deve essere chiara e concisa (massimo due frasi), in lingua italiana"""

        return prompt

    def _generate_description(self, metadata: TableMetadata) -> Optional[str]:
        """Genera una descrizione semantica della tabella usando il LLM"""
        prompt = self.build_prompt(metadata)

        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert providing concise table descriptions.",
            temperature=0.1,
        )

        return description.strip() if description else None

    def _calculate_importance_score(self, metadata: TableMetadata) -> float:
        """Calcola uno score di importanza per la tabella
        La logica è che una tabella è più importante se ha più relazioni, colonne e chiavi primarie
        """
        score = 0.0

        # peso per le relazioni
        relations_weight = len(metadata.foreign_keys) * 0.2
        # peso per le colonne
        columns_weight = len(metadata.columns) * 0.1
        # peso per chiavi primarie
        pk_weight = 0.3 if metadata.primary_keys else 0
        # normalizza e combina gli score
        score = min(1.0, relations_weight + columns_weight + pk_weight)

        return round(score, 2)
