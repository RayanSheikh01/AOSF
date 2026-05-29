import pytest

from agentos.process import AgentControlBlock, AgentState

def test_agent_control_block():
    acb = AgentControlBlock(pid=1)
    assert acb.pid == 1
    assert acb.parent_pid is None
    assert acb.priority == 3
    assert acb.state == AgentState.NEW
    assert acb.token_budget == 100_000
    assert acb.tokens_used == 0
    assert acb.capabilities == []
    assert acb.steps_run == 0
    assert acb.cost_usd == 0.0
    

def test_pcb_start():
    acb = AgentControlBlock(pid=1)
    assert acb.state == AgentState.NEW
    acb.transition_state(AgentState.READY)
    assert acb.state == AgentState.READY
    acb.transition_state(AgentState.RUNNING)
    assert acb.state == AgentState.RUNNING
    acb.transition_state(AgentState.WAITING)
    assert acb.state == AgentState.WAITING
    acb.transition_state(AgentState.READY)
    assert acb.state == AgentState.READY
    acb.transition_state(AgentState.RUNNING)
    assert acb.state == AgentState.RUNNING
    acb.transition_state(AgentState.TERMINATED)
    assert acb.state == AgentState.TERMINATED
    with pytest.raises(ValueError):
        acb.transition_state(AgentState.RUNNING)
    
    
    
