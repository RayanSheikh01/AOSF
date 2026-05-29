from pydantic.dataclasses import dataclass


@dataclass
class KernelConfig:
    cores: int = 4
    quantum_steps: int = 1
    priority_level: int = 3
    boost_interval: int = 20
    total_token_budget: int = 200_000
    default_model: str = "llama3.2"
    ollama_host: str = "http://localhost:11434"