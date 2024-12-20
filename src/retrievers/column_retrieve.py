import json
from typing import List, Dict, Tuple
import string
from collections import defaultdict
from difflib import SequenceMatcher
from src.agents.keywords_agent import KeywordExtractionAgent

class ColumnRetriever:
    def __init__(self, cache_file: str):
        """Inizializza il matcher caricando i metadati dal file di cache"""

        with open(cache_file, 'r') as f:
            self.metadata = json.load(f)

        # preprocessa i valori distinti per ogni colonna
        self.column_values = self._preprocess_column_values()
        self.agent = KeywordExtractionAgent()

    def _preprocess_column_values(self) -> Dict[str, Dict[str, set]]:
        """Preprocessa i valori distinti per ogni colonna di ogni tabella"""
        processed = defaultdict(lambda: defaultdict(set))

        for table_name, table_data in self.metadata.items():
            for column in table_data['columns']:
                if 'distinct_values' in column and column['distinct_values']:
                    # normalizza e tokenizza ogni valore
                    normalized_values = {
                        self._normalize_value(str(val))
                        for val in column['distinct_values']
                        if val is not None
                    }
                    processed[table_name][column['name']] = normalized_values

        return processed

    def _normalize_value(self, value: str) -> str:
        """Normalizza un valore per il matching"""
        # Converti in lowercase e rimuovi punteggiatura
        value = value.lower()
        value = value.translate(str.maketrans("", "", string.punctuation))

        # Gestisci spazi e caratteri speciali
        value = value.replace(" ", "")
        return value

    def _extract_keywords(self, query: str) -> List[str]:
        """Estrae keyword dalla query"""
        keywords = self.agent.run(query)
        return keywords.keywords

    def _calculate_similarity(self, query_term: str, column_value: str) -> float:
        """Calcola la similarità tra un termine della query e un valore della colonna"""
        # match esatto
        if query_term in column_value:
            return 1.0

        # partial match usando SequenceMatcher
        return SequenceMatcher(None, query_term, column_value).ratio()


    def find_matching_columns(self, query: str,
                              min_similarity: float = 0.8,
                              max_results: int = 5) -> List[Tuple[str, str, float]]:
        """Trova le colonne più rilevanti per la query

        Returns:
            List di tuple (table_name, column_name, score)
        """
        keywords = self._extract_keywords(query)
        print(f"Keywords: {keywords}")
        matches = []

        for table_name, columns in self.column_values.items():
            #print(f"Matching per la tabella {table_name}")
            for column_name, values in columns.items():
                max_score = 0
                #print(f"Matching per la colonna {column_name} di {table_name}")
                # per ogni keyword, cerca il miglior match nei valori della colonna
                for keyword in keywords:
                    #print(f"Matching per la keyword {keyword}")
                    for value in values:
                        similarity = self._calculate_similarity(keyword, value)
                        max_score = max(max_score, similarity)

                        if similarity >= min_similarity:
                            matches.append((table_name, column_name, max_score))
                            break

        # Ordina per score e rimuovi duplicati
        matches.sort(key=lambda x: x[2], reverse=True)
        unique_matches = []
        seen = set()

        for match in matches:
            key = (match[0], match[1])
            if key not in seen and len(unique_matches) < max_results:
                seen.add(key)
                unique_matches.append(match)

        return unique_matches