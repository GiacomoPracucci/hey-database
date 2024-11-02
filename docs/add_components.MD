# Adding Support for New Components

## 1. Adding a New Database Type

- Create a new connector class in src/connettori/:

```python
class NewDBConnector(DatabaseConnector):
    def connect(self) -> bool:
        # Implementation
        pass
```  

- Create a new metadata retriever in src/dbcontext/:  

```python
class NewDBMetadataRetriever(DatabaseMetadataRetriever):
    def _get_row_count(self, table_name: str) -> int:
        # Implementation
        pass
    ...
```  

- Update the ServiceFactory:

```python
@staticmethod
def create_db_connector(config: DatabaseConfig):
    db_types = {
        'postgres': PostgresManager,
        'mysql': MySQLManager,
        'newdb': NewDBConnector  # Add new type
    }
```  

## 2. Adding a new LLM Service

- Create a new handler class in a new directory (e.g., src/newllm_/):

```python
class NewLLMHandler:
    def get_completion(self, prompt: str) -> str:
        # Implementation
        pass
```  

- Update the ServiceFactory:

```python
@staticmethod
def create_llm_handler(config: LLMConfig):
    if config.type == 'newllm':
        return NewLLMHandler(
            api_key=config.api_key,
            model=config.model
        )
```  

- Update configuration data classes if needed (models.py):

```python
@dataclass
class LLMConfig:
    type: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    new_parameter: Optional[str] = None  # Add new parameters
```  