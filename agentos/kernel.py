

import asyncio
from collections import deque
from typing import Optional

from agentos.ipc import Broker
from agentos.process import Agent, AgentControlBlock, AgentState
from agentos.scheduler import SchedulerPolicy
from agentos.memory.store import SharedStore
from agentos.monitor import Monitor
from agentos.tools import ToolRegistry


class Kernel:

    def __init__(self, config, scheduler_policy: SchedulerPolicy, tools: Optional[ToolRegistry] = None):
        self.config = config
        self.scheduler_policy = scheduler_policy
        self.tools = tools
        self.agents: dict[int, Agent] = {}
        self.agent_control_blocks: dict[int, AgentControlBlock] = {}
        self.next_pid = 1
        

        # IPC state
        self.broker = Broker()
        
        


        # Shared key/value store (named segments) for cross-agent findings.
        self.store = SharedStore()
        # ps/top-style live view over the PCB table.
        self.monitor = Monitor(self)

    def spawn(self, behavior, priority, capabilities, token_budget) -> int:
        pid = self.next_pid
        self.next_pid += 1

        acb = AgentControlBlock(pid=pid, priority=priority, capabilities=capabilities, token_budget=token_budget)
        agent = Agent(behavior=behavior, acb=acb)

        self.agents[pid] = agent
        self.agent_control_blocks[pid] = acb
        self.broker.spawn(pid)

        # NEW -> READY so the agent becomes schedulable / can later exit.
        acb.transition_state(AgentState.READY)
        if self.scheduler_policy is not None:
            self.scheduler_policy.on_ready(acb)

        return pid
    
    def run(self, until_idle=True):
       # Local import avoids a circular import: syscalls.py imports Kernel.
       from agentos.syscalls import SyscallContext
       
       cores = self.config.get("cores", 4)
       boost_interval = self.config.get("boost_interval", 20)
       steps = 0
       while True:
           steps += 1
           if steps % boost_interval == 0:
               self.scheduler_policy.boost()
           for _ in range(cores):
               next_acb = self.scheduler_policy.pick_next(list(self.agent_control_blocks.values()))
               if next_acb is None:
                   if until_idle:
                       return
                   else:
                       continue
               agent = self.agents[next_acb.pid]
               # Hand the running agent its kernel interface for this step.
               ctx = SyscallContext(pid=next_acb.pid, kernel_ref=self)
               step_result = asyncio.run(agent.behavior.step(ctx))
               if step_result.kind == "continue":
                   self.scheduler_policy.on_quantum_expired(next_acb)
               elif step_result.kind == "yield":
                   self.scheduler_policy.on_yield(next_acb)
               elif step_result.kind == "block":
                   # No real I/O wake path exists yet; re-ready the agent so a
                   # mock workload can still make progress toward "done".
                   self.scheduler_policy.on_block(next_acb)
                   self.scheduler_policy.on_yield(next_acb)
               elif step_result.kind == "done":
                   next_acb.transition_state(AgentState.TERMINATED)
                   
                