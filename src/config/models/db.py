from typing import Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    type: str # tipo di database (postgres, snowflake, ecc.)
    host: str
    port: str
    database: str
    user: str
    password: str
    schema: str
    warehouse: Optional[str] = None # parametro opzionale di snowflake
    account: Optional[str] = None # parametro opzionale di snowflake
    role: Optional[str] = None # parametro opzionale di snowflake