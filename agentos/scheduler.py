from typing import Optional, Protocol
from collections import deque

from agentos.process import AgentControlBlock


class SchedulerPolicy(Protocol):
    
    def pick_next(self, ready_queue: list[AgentControlBlock]) -> Optional[AgentControlBlock]:
        """Given a list of ready agents, pick the next one to run."""
        ...
    
    def on_ready(self, acb: AgentControlBlock):
        """Called when an agent transitions to READY state."""
        ...
        
    def on_yield(self, acb: AgentControlBlock):
        """Called when an agent yields the CPU."""
        ...
        
    def on_quantum_expired(self, acb: AgentControlBlock):
        """Called when an agent's quantum expires."""
        ...
        
    def on_block(self, acb: AgentControlBlock):
        """Called when an agent blocks on I/O or a syscall."""
        ...
    
    def boost(self):
        """Called periodically to boost the priority of waiting agents."""
        ...
        
class MLFQ(SchedulerPolicy):
    def __init__(self, num_queues: int = 3):
        self.num_queues = num_queues
        self.queues: list[deque[AgentControlBlock]] = [deque() for _ in range(num_queues)]
        self.boost_interval = 20
        self.quantum_steps = [1, 2, 4]  # Example quantum steps for each queue level
        self.priority_level = 3  # Default priority level for new agents
    
    def on_ready(self, acb: AgentControlBlock):
        acb.priority = self.priority_level
        if acb.priority >= self.num_queues:
            acb.priority = self.num_queues - 1
        elif acb.priority < 0:
            acb.priority = 0
        
        self.queues[acb.priority].append(acb)
    
    def pick_next(self, ready_queue: list[AgentControlBlock]) -> Optional[AgentControlBlock]:
        for queue in self.queues:
            if queue:
                return queue.popleft()
        return None

    def on_quantum_expired(self, acb: AgentControlBlock):
        if acb.priority < self.num_queues - 1:
            acb.priority += 1
        self.queues[acb.priority].append(acb)
    
    
    def on_yield(self, acb: AgentControlBlock):
        self.queues[acb.priority].append(acb)
        
    def on_block(self, acb: AgentControlBlock):
        # Agent is WAITING on I/O, not runnable. Do not enqueue it here.
        # acb.priority is left untouched so on_ready re-enters it at the
        # same level once the I/O completes (anti-gaming: blocking does not
        # reset its place in the hierarchy).
        return

    def boost(self):
        for i in range(1, self.num_queues):
            while self.queues[i]:
                acb = self.queues[i].popleft()
                acb.priority = 0
                self.queues[0].append(acb)
    