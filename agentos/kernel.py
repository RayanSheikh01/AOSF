    

from agentos.process import Agent, AgentControlBlock, AgentState
from agentos.scheduler import SchedulerPolicy


class Kernel:
    
    def __init__(self, config, scheduler_policy: SchedulerPolicy):
        self.config = config
        self.scheduler_policy = scheduler_policy
        self.agents: dict[int, Agent] = {}
        self.agent_control_blocks: dict[int, AgentControlBlock] = {}
        self.next_pid = 1
    
    
    def spawn(self, behavior, priority, capabilities, token_budget) -> int:
        pid = self.next_pid
        self.next_pid += 1
        
        acb = AgentControlBlock(pid=pid, priority=priority, capabilities=capabilities, token_budget=token_budget)
        agent = Agent(behavior=behavior, acb=acb)
        
        self.agents[pid] = agent
        self.agent_control_blocks[pid] = acb
        
        self.scheduler_policy.on_ready(acb)
        
        return pid
    
    def run(self, until_idle=True):
       cores = self.config.get("cores", 1)
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
               step_result = agent.behavior
               if step_result.kind == "continue":
                   self.scheduler_policy.on_quantum_expired(next_acb)
               elif step_result.kind == "yield":
                   self.scheduler_policy.on_yield(next_acb)
               elif step_result.kind == "block":
                   self.scheduler_policy.on_block(next_acb)
               elif step_result.kind == "done":
                   self.scheduler_policy.pick_next(list(self.agent_control_blocks.values()))
                   next_acb.transition_state(AgentState.TERMINATED)
                   
                