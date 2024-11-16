# questo script contiene i modelli per i metadati dello schema
# TODO essendo ormai molti i modelli dovremmo creare uno script per ogni categoria e non avere tutto in models.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ERColumn:
    """Rappresenta una colonna per la visualizzazione ER"""
    name: str
    type: str
    is_primary_key: bool
    is_foreign_key: bool
    is_nullable: bool

@dataclass
class ERRelationship:
    """Rappresenta una relazione tra tabelle nel diagramma ER"""
    from_table: str
    to_table: str
    from_column: str
    to_column: str
    relationship_type: str  # '1-1', '1-N', 'N-1', 'N-N'

@dataclass
class ERTable:
    """Rappresenta una tabella nel diagramma ER"""
    name: str
    columns: List[ERColumn]
    position_x: Optional[float] = None  # Per il layout del grafico
    position_y: Optional[float] = None  # Per il layout del grafico

@dataclass
class ERDiagram:
    """Rappresenta l'intero diagramma ER"""
    tables: List[ERTable]
    relationships: List[ERRelationship]