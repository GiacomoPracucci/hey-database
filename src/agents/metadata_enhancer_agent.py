from typing import Dict, List, Optional, Any
import re
import logging
from dataclasses import dataclass

from src.agents.base_agent import Agent
from src.config.models.metadata import TableMetadata, EnhancedTableMetadata
from src.llm_handler.base_llm_handler import LLMHandler

logger = logging.getLogger('hey-database')

@dataclass
class MetadataAgentResponse:
    """Classe che rappresenta la risposta dell'agente Metadata"""
    success: bool
    enhanced_metadata: Optional[Dict[str, EnhancedTableMetadata]] = None
    error: Optional[str] = None

class MetadataAgent(Agent):
    """Agente responsabile dell'arricchimento dei metadati delle tabelle"""

    def __init__(self, llm_handler: LLMHandler):
        """Args:
            llm_handler: Handler per il modello di linguaggio da usare per generare descrizioni
        """
        self.llm_handler = llm_handler

    def run(self, input_data: Dict[str, TableMetadata]) -> MetadataAgentResponse:
        """Esegue l'enhancement dei metadati
        Args:
            input_data: Dizionario dei metadati originali
        Returns:
            MetadataAgentResponse con i metadati arricchiti o errore
        """
        try:
            enhanced = {}
            for table_name, table_metadata in input_data.items():
                try:
                    enhanced[table_name] = self._enhance_table_metadata(table_metadata)
                    logger.debug(f"Metadati arricchiti per la tabella {table_name}")
                except Exception as e:
                    logger.error(f"Errore nell'enhancement dei metadati per {table_name}: {str(e)}")
                    continue

            return MetadataAgentResponse(
                success=True,
                enhanced_metadata=enhanced
            )

        except Exception as e:
            logger.exception(f"Error in metadata enhancement: {str(e)}")
            return MetadataAgentResponse(
                success=False,
                error=str(e)
            )

    def build_prompt(self, input_data: TableMetadata) -> str:
        """Costruisce il prompt per la generazione della descrizione

        Args:
            input_data: Metadati della tabella

        Returns:
            str: Prompt formattato
        """
        columns_info = [
            f"- {col['name']} ({col['type']}) {'NOT NULL' if not col['nullable'] else ''}"
            for col in input_data.columns
        ]

        foreign_keys_info = []
        for fk in input_data.foreign_keys:
            from_cols = ', '.join(fk['constrained_columns'])
            to_table = fk['referred_table']
            to_cols = ', '.join(fk['referred_columns'])
            foreign_keys_info.append(f"- {from_cols} -> {to_table}({to_cols})")

        prompt = f"""Analyze this database table and provide a concise description of its purpose and content.

Table: {input_data.name}
Number of records: {input_data.row_count}

Columns:
{chr(10).join(columns_info)}

Primary Keys: {', '.join(input_data.primary_keys)}

Foreign Keys:
{chr(10).join(foreign_keys_info) if foreign_keys_info else 'No foreign keys'}

Provide a clear and concise description in 2-3 sentences."""

        return prompt

    def _enhance_table_metadata(self, table_metadata: TableMetadata) -> EnhancedTableMetadata:
        """Arricchisce i metadati di una singola tabella"""
        # genera descrizione usando LLM
        prompt = self.build_prompt(table_metadata)
        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert providing concise table descriptions.",
            temperature=0.2
        )
        description = description.strip() if description else ""

        # estrae keywords e calcola importance score
        keywords = self._extract_keywords(table_metadata)
        importance_score = self._calculate_importance_score(table_metadata)

        return EnhancedTableMetadata(
            base_metadata=table_metadata,
            description=description,
            keywords=keywords,
            importance_score=importance_score
        )

    def _extract_keywords(self, table_metadata: TableMetadata) -> List[str]:
        """Estrae keywords dai metadati della tabella

        Args:
            table_metadata: Metadati della tabella

        Returns:
            List[str]: Lista di keywords uniche
        """
        keywords = set()

        # dal nome della tabella
        table_words = self._split_camel_case(table_metadata.name)
        keywords.update(table_words)

        # dai nomi delle colonne
        for col in table_metadata.columns:
            col_words = self._split_camel_case(col['name'])
            keywords.update(col_words)

        # dalle tabelle correlate
        for fk in table_metadata.foreign_keys:
            keywords.add(fk['referred_table'])

        # rimuovi parole comuni e converti in minuscolo
        common_words = {'id', 'code', 'type', 'name', 'date', 'created', 'modified', 'status'}
        keywords = {word.lower() for word in keywords if word.lower() not in common_words}

        return sorted(list(keywords))

    def _split_camel_case(self, s: str) -> List[str]:
        """Divide una stringa in camel case o snake case nelle sue parole componenti
        Args:
            s: Stringa da dividere
        Returns:
            List[str]: Lista di parole
        """
        words = s.split('_')
        result = []

        for word in words:
            matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', word)
            result.extend(match.group(0) for match in matches)

        return [w for w in result if w]

    def _calculate_importance_score(self, table_metadata: TableMetadata) -> float:
        """Calcola uno score di importanza per la tabella
        La logica è che una tabella è più importante se ha più relazioni, colonne e chiavi primarie
        Args:
            table_metadata: Metadati della tabella
        Returns:
            float: Score di importanza (0-1)
        """
        score = 0.0

        # peso per le relazioni
        relations_weight = len(table_metadata.foreign_keys) * 0.2
        # peso per le colonne
        columns_weight = len(table_metadata.columns) * 0.1
        # peso per chiavi primarie
        pk_weight = 0.3 if table_metadata.primary_keys else 0
        # normalizza e combina gli score
        score = min(1.0, relations_weight + columns_weight + pk_weight)

        return round(score, 2)