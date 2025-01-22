from dataclasses import dataclass

@dataclass
class PromptConfig:
    include_sample_data: bool = True
    max_sample_rows: int = 3 