from dataclasses import field
from enum import Enum
from pydantic.dataclasses import dataclass
from typing import ClassVar, Optional

class AgentState(str, Enum):
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"
    

@dataclass
class StepResult:
    # "continue" = agent can keep running, "yield" = voluntarily yields the CPU,
    # "block" = waiting on I/O or a syscall, "done" = completed execution.
    VALID_KINDS: ClassVar[list[str]] = ["continue", "yield", "block", "done"]
    kind: str
    # optional syscall payload. Returned by an agent step()
    payload: Optional[dict] = None

    def __post_init__(self):
        if self.kind not in self.VALID_KINDS:
            raise ValueError(f"Invalid StepResult kind: {self.kind}")
    
    
@dataclass
class AgentControlBlock:
    pid: int
    parent_pid: Optional[int] = None
    priority: int = 3
    state: AgentState = AgentState.NEW
    token_budget: int = 100_000
    tokens_used: int = 0
    capabilities: list[str] = field(default_factory=list)
    steps_run: int = 0
    cost_usd: float = 0.0

    def transition_state(self, new_state: AgentState):
        if self.state == AgentState.NEW and new_state != AgentState.READY:
            raise ValueError(f"Invalid state transition: {self.state} can only transition to READY")
        elif self.state == AgentState.READY and new_state not in [AgentState.RUNNING, AgentState.TERMINATED]:
            raise ValueError(f"Invalid state transition: {self.state} can only transition to RUNNING or TERMINATED")
        elif self.state == AgentState.RUNNING and new_state not in [AgentState.WAITING, AgentState.TERMINATED]:
            raise ValueError(f"Invalid state transition: {self.state} can only transition to WAITING or TERMINATED")
        elif self.state == AgentState.WAITING and new_state != AgentState.READY:
            raise ValueError(f"Invalid state transition: {self.state} can only transition to READY")
        elif self.state == AgentState.TERMINATED and new_state != AgentState.NEW:
            raise ValueError(f"Invalid state transition: {self.state} can only transition to NEW")
        self.state = new_state
    
class Agent:
    behavior: StepResult
    acb: AgentControlBlock
    
    def __init__(self, behavior: StepResult, acb: AgentControlBlock):
        self.behavior = behavior
        self.acb = acb
    
    async def step(self) -> StepResult:
        return self.behavior
    

    
    
        
    