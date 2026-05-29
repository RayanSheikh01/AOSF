
from enum import Enum

from agentos.process import StepResult

from agentos.process import StepResult

    

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
        
    
    
    