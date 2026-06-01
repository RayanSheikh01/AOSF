from typing import Protocol
from ollama import AsyncClient
from pydantic.dataclasses import dataclass

    
@dataclass
class LLMResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    
class LLMProvider(Protocol):
    name: str
    description: str
    
    async def chat(self, messages: list[dict[str, str]], model) -> LLMResponse:
        ...

class OllamaProvider(LLMProvider):
    name = "ollama"
    description = "Ollama LLM provider"
    
    async def chat(self, messages: list[dict[str, str]], model) -> LLMResponse:
        client = AsyncClient()
        response = await client.chat(model=model, messages=messages)
        return LLMResponse(
            text=response.message.content,
            prompt_tokens=response.prompt_eval_count,
            completion_tokens=response.eval_count
        )
        
        
class FakeProvider(LLMProvider):
    name = "fake"
    description = "Fake LLM provider for testing"
    
    async def chat(self, messages: list[dict[str, str]], model) -> LLMResponse:
        return LLMResponse(
            text="This is a fake response.",
            prompt_tokens=10,
            completion_tokens=5
        )
        