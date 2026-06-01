
from enum import Enum

from agentos.process import StepResult

from agentos.process import StepResult
from agentos.providers import LLMProvider, LLMResponse

    

class MockAgent:
    State = Enum("State", "READY RUNNING WAITING TERMINATED")
    results = [State.READY, State.RUNNING, State.WAITING, State.READY, State.RUNNING, State.TERMINATED]
    
    def __init__(self):
        self.step_count = 0
        
    async def step(self) -> StepResult:
        result = self.results[self.step_count]
        self.step_count += 1
        if result == self.State.READY:
            return StepResult(kind="continue")
        elif result == self.State.RUNNING:
            return StepResult(kind="continue")
        elif result == self.State.WAITING:
            return StepResult(kind="block")
        elif result == self.State.TERMINATED:
            return StepResult(kind="done")
        return StepResult(kind="continue")
        
    
    
class LLMAgent(LLMProvider):
    name = "llm_agent"
    description = "LLM Agent for testing"
    
    async def chat(self, messages: list[dict[str, str]], model) -> LLMResponse:
        return LLMResponse(
            text="This is a response from the LLM agent.",
            prompt_tokens=15,
            completion_tokens=10
        )