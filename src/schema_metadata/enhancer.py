from typing import Dict, List
import re
import logging

from src.config.models.metadata import TableMetadata, EnhancedTableMetadata
from src.llm_handler.base_llm_handler import LLMHandler

logger = logging.getLogger('hey-database')


class MetadataEnhancer:
    """Classe responsabile dell'arricchimento dei metadati delle tabelle con descrizioni e keywords"""
    
    def __init__(self, llm_handler: LLMHandler):
        """
        Args:
            llm_handler: Handler per il modello di linguaggio da usare per generare descrizioni
        """
        self.llm_handler = llm_handler
        
    def enhance_table_metadata(self, table_metadata: TableMetadata) -> EnhancedTableMetadata:
        """Arricchisce i metadati di una tabella con descrizione e keywords
        
        Args:
            table_metadata: Metadati originali della tabella
            
        Returns:
            EnhancedTableMetadata: Metadati arricchiti
        """
        try:
            description = self._generate_table_description(table_metadata)
            keywords = self._extract_keywords(table_metadata)
            importance_score = self._calculate_importance_score(table_metadata)
            
            return EnhancedTableMetadata(
                base_metadata=table_metadata,
                description=description,
                keywords=keywords,
                importance_score=importance_score
            )
            
        except Exception as e:
            logger.error(f"Errore nell'enhancement dei metadati per la tabella {table_metadata.name}: {str(e)}")
            raise
        
    def enhance_all_metadata(self, metadata: Dict[str, TableMetadata]) -> Dict[str, EnhancedTableMetadata]:
        """Arricchisce i metadati di tutte le tabelle
        
        Args:
            metadata: Dizionario dei metadati originali
            
        Returns:
            Dict[str, EnhancedTableMetadata]: Dizionario dei metadati arricchiti
        """
        enhanced = {}
        for table_name, table_metadata in metadata.items():
            try:
                enhanced[table_name] = self.enhance_table_metadata(table_metadata)
                logger.debug(f"Metadati arricchiti per la tabella {table_name}")
            except Exception as e:
                logger.error(f"Errore nell'enhancement dei metadati per {table_name}: {str(e)}")
                continue
        return enhanced
    
    def _generate_table_description(self, table_metadata: TableMetadata) -> str:
        """Genera una descrizione della tabella usando LLM
        
        Args:
            table_metadata: Metadati della tabella
            
        Returns:
            str: Descrizione generata
        """
        prompt = self._build_description_prompt(table_metadata)
        description = self.llm_handler.get_completion(
            prompt=prompt,
            system_prompt="You are a database expert providing concise table descriptions.",
            temperature=0.2
        )
        return description.strip() if description else ""

    def _build_description_prompt(self, table_metadata: TableMetadata) -> str:
        """Costruisce il prompt per la generazione della descrizione
        
        Args:
            table_metadata: Metadati della tabella
            
        Returns:
            str: Prompt formattato
        """
        columns_info = [
            f"- {col['name']} ({col['type']}) {'NOT NULL' if not col['nullable'] else ''}"
            for col in table_metadata.columns
        ]
        
        foreign_keys_info = []
        for fk in table_metadata.foreign_keys:
            from_cols = ', '.join(fk['constrained_columns'])
            to_table = fk['referred_table']
            to_cols = ', '.join(fk['referred_columns'])
            foreign_keys_info.append(f"- {from_cols} -> {to_table}({to_cols})")
            
        prompt = f"""Analyze this database table and provide a concise description of its purpose and content.

Table: {table_metadata.name}
Number of records: {table_metadata.row_count}

Columns:
{chr(10).join(columns_info)}

Primary Keys: {', '.join(table_metadata.primary_keys)}

Foreign Keys:
{chr(10).join(foreign_keys_info) if foreign_keys_info else 'No foreign keys'}

Provide a clear and concise description in 2-3 sentences."""

        return prompt
    
    
    def _extract_keywords(self, table_metadata: TableMetadata) -> List[str]:
        """Estrae keywords dai metadati della tabella
        TODO valutare se sta logica è ok o è meglio metter un LLM ad estrarre le keywords
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
        
        # rimuovi parole comuni e converti in minuscolo TODO da ampliare
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
        """Calcola uno score di importanza per la tabella basato su:
        - Numero di relazioni (foreign keys)
        - Numero di colonne
        - Presenza di chiavi primarie
        - Volume dei dati
        
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