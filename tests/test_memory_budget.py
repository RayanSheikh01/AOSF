import pytest

def test_budget():
    from agentos.process import AgentControlBlock
    from agentos.memory.budget import MemoryPolicy, BudgetAllocator
    
    class MockMemoryPolicy(MemoryPolicy):
        def __init__(self):
            self.pressure_called = False
            self.last_acb = None
            self.last_context = None
        
        def on_pressure(self, acb: AgentControlBlock, context: dict):
            self.pressure_called = True
            self.last_acb = acb
            self.last_context = context
            
    policy = MockMemoryPolicy()
    allocator = BudgetAllocator(total_budget=1000, policy=policy)
    acb = AgentControlBlock(pid=1, token_budget=500)
    # Charge within the budget
    assert allocator.charge(acb, 200) == True
    assert allocator.pool == 800
    assert policy.pressure_called == False
    # Charge that exceeds the remaining budget
    assert allocator.charge(acb, 900) == False
    assert allocator.pool == 800  # Pool should not change
    assert policy.pressure_called == True
    assert policy.last_acb == acb
    assert policy.last_context == {"used": 900, "pool": 800}
    
