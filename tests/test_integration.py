import pytest

from agentos.agent_runtime import MockAgent
from agentos.kernel import Kernel
from agentos.process import AgentState
from agentos.scheduler import MLFQ

def test_integration():
    scheduler = MLFQ(num_queues=3)
    kernel_config = {"cores": 2, "boost_interval": 10}
    kernel = Kernel(config=kernel_config, scheduler_policy=scheduler)
    coordinator_pid = kernel.spawn(behavior=MockAgent(), priority=0, capabilities={"spawn", "send", "write_segment", "read_segment"}, token_budget=100)
    worker1_pid = kernel.spawn(behavior=MockAgent(), priority=0, capabilities={"send", "write_segment"}, token_budget=50)
    worker2_pid = kernel.spawn(behavior=MockAgent(), priority=0, capabilities={"send", "write_segment"}, token_budget=50)
    kernel.run(until_idle=True)
    
    assert kernel.agent_control_blocks[coordinator_pid].state == AgentState.TERMINATED
    assert kernel.agent_control_blocks[worker1_pid].state == AgentState.TERMINATED
    assert kernel.agent_control_blocks[worker2_pid].state == AgentState.TERMINATED
    
    