# Aggiungere un Nuovo Agente

## 1. Creare la Classe Agente
```python
# In src/agents/new_agent.py
from src.agents.base import Agent

class NewAgent(Agent):
def __init__(self, required_dependencies):
self.dependencies = required_dependencies

    def run(self, input_data):
        # Implementa la logica principale
        pass
        
    def build_prompt(self):
        # Implementa la costruzione del prompt
        pass
```

## 2. Creare il Builder dell'Agente
```python
# In src/factories/builders/new_agent_builder.py
from src.factories.builders.base import AgentBuilder

class NewAgentBuilder(AgentBuilder[NewAgent]):
    def __init__(self, app_config):
        self.config = app_config
        # Inizializza stati necessari
        
    def build_database(self) -> 'NewAgentBuilder':
        # Implementa se necessario
        return self
        
    def build_llm(self) -> 'NewAgentBuilder':
        # Implementa se necessario
        return self
        
    def build(self) -> NewAgent:
        # Verifica componenti necessari
        # Costruisci e restituisci l'agente
```

## 3. Creare il Servizio (se necessario)
```python
# In src/services/new_service.py
from src.services.base import Service

class NewService(Service):
    def __init__(self, new_agent):
        self.agent = new_agent
        
    def process(self, input_data):
        return self.agent.run(input_data)
```

## 4. Aggiungere il Factory Method
```python
# In src/factories/__init__.py class ServiceFactory
@staticmethod
def create_new_service(app_config):
    new_agent = (NewAgentBuilder(app_config)
    .build_required_components()
    .build())
    return NewService(new_agent)
```

## 5.Aggiungere reoutes (se necessario)
```python
# In src/web/new_routes.py
def create_new_routes(app, service):
    new_bp = Blueprint('new', __name__)
    # Definisci routes
    app.register_blueprint(new_bp, url_prefix='/new')
```
## 6. Aggiungere il Servizio al main.py
```python
def create_app():
    # ...
    new_service = ServiceFactory.create_new_service(config)
    create_new_routes(app, new_service)
    # ...
```