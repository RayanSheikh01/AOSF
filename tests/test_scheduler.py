import pytest

from agentos.process import AgentControlBlock, AgentState
from agentos.scheduler import MLFQ

def test_mlfq_scheduler():
    scheduler = MLFQ(num_queues=3)
    
    # Create some agents
    acb1 = AgentControlBlock(pid=1)
    acb2 = AgentControlBlock(pid=2)
    acb3 = AgentControlBlock(pid=3)
    
    # Transition agents to READY state
    scheduler.on_ready(acb1)
    scheduler.on_ready(acb2)
    scheduler.on_ready(acb3)
    
    # Pick next agent to run (should be acb1 since all have same priority and were added in order)
    next_acb = scheduler.pick_next([])
    assert next_acb.pid == 1
    
    # Simulate quantum expiration for acb1
    scheduler.on_quantum_expired(next_acb)
    
    # Now acb1 should be in the second queue, and acb2 should be picked next
    next_acb = scheduler.pick_next([])
    assert next_acb.pid == 2
    
    # Simulate yield for acb2
    scheduler.on_yield(next_acb)
    
    # Now acb3 should be picked next since acb2 yielded and goes to the back of the queue
    next_acb = scheduler.pick_next([])
    assert next_acb.pid == 3