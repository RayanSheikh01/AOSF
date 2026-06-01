    

from asyncio import Protocol

from agentos.process import AgentControlBlock


class MemoryPolicy(Protocol):
    
    def on_pressure(self, acb: AgentControlBlock, context: dict):
        """Called when an agent is under memory pressure. The context dict can include information about the current memory usage, the agent's behavior, etc. The policy can choose to reduce the agent's token budget, revoke capabilities, or even terminate the agent."""
        ...
        
        
        
    
class BudgetAllocator():
    
    def __init__(self, total_budget: int, policy: MemoryPolicy):
        self.total_budget = total_budget
        self.pool = total_budget
        self.policy = policy
    
    def charge(self, acb: AgentControlBlock, used: int):
        if self.pool >= used:
            self.pool -= used
            return True
        else:
            # Not enough budget in the pool, trigger memory pressure handling
            self.policy.on_pressure(acb, context={"used": used, "pool": self.pool})
            return False
    
    
    
    