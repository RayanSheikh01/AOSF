import pytest

from agentos.process import AgentControlBlock, AgentState
from agentos.kernel import Kernel

class MockSchedulerPolicy:
    def on_ready(self, acb):
        pass
    
    def pick_next(self, acbs):
        return None
    
    def on_quantum_expired(self, acb):
        pass
    
    def on_yield(self, acb):
        pass
    
    def on_block(self, acb):
        pass
    
    def boost(self):
        pass

def test_kernel_spawn_and_run():
    kernel_config = {"cores": 2, "boost_interval": 5}
    kernel = Kernel(config=kernel_config, scheduler_policy=MockSchedulerPolicy())  # Use a mock scheduler policy for testing
    
    # Spawn a mock agent
    pid = kernel.spawn(behavior=None, priority=3, capabilities=[], token_budget=100_000)
    
    # Check that the agent was spawned correctly
    assert pid == 1
    assert pid in kernel.agents
    assert pid in kernel.agent_control_blocks
    
    # Run the kernel (this will use the mock scheduler policy which does nothing)
    kernel.run(until_idle=True)
    
    
