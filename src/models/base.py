from dataclasses import dataclass
from src.config.languages import SupportedLanguage


@dataclass
class BaseConfig:
    language: SupportedLanguage = SupportedLanguage.get_default()
    debug: bool = True
