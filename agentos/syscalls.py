from typing import Optional



from agentos import permissions
from agentos.ipc import Message
from agentos.permissions import CapabilitySet
from agentos.errors import CapabilityError
from agentos.kernel import Kernel
from agentos.process import AgentState, StepResult


class SyscallContext:
    """Per-agent kernel interface. `pid` is the acting (calling) agent; every
    capability-gated syscall is checked against that agent's control block."""

    pid: int
    kernel_ref: Kernel

    def __init__(self, pid, kernel_ref):
        self.pid = pid
        self.kernel_ref = kernel_ref

    # -- internal helpers ---------------------------------------------------

   


    
    def _caller_acb(self):
        try:
            return self.kernel_ref.agent_control_blocks[self.pid]
        except KeyError:
            raise PermissionError(f"No such acting agent: pid {self.pid}")

    def _require(self, capability: str):
        """Raise CapabilityError if the calling agent lacks `capability`."""
        acb = self._caller_acb()
        caps = CapabilitySet(acb.capabilities)
        permissions.require(caps, capability)

    # -- process control (ungated bootstrap syscalls) -----------------------

    def spawn(self, behavior: StepResult, priority: int = 3, capabilities: list[str] = [], token_budget: int = 100_000) -> int:
        """Spawn a new agent with the given behavior and return its PID.

        An agent cannot grant its child a capability it does not itself hold;
        the child's capability set must be a subset of the caller's. The
        bootstrap case (caller not yet registered) is exempt and acts as root."""
        parent_acb = self.kernel_ref.agent_control_blocks.get(self.pid)
        if parent_acb is not None:
            parent_caps = CapabilitySet(parent_acb.capabilities)
            requested = CapabilitySet(capabilities)
            if not requested.subset_of(parent_caps):
                raise CapabilityError(
                    f"Agent {self.pid} cannot grant capabilities it lacks: "
                    f"{sorted(requested.capabilities - parent_caps.capabilities)}"
                )
        return self.kernel_ref.spawn(
            behavior=behavior,
            priority=priority,
            capabilities=capabilities,
            token_budget=token_budget,
        )

    def exit(self):
        """Terminate the calling agent."""
        self._caller_acb().transition_state(AgentState.TERMINATED)

    def yield_cpu(self):
        """Yield the CPU to allow other agents to run."""
        acb = self._caller_acb()
        if self.kernel_ref.scheduler_policy is not None:
            self.kernel_ref.scheduler_policy.on_yield(acb)

    # -- messaging ----------------------------------------------------------

    def send(self, target_pid: int, message: Message):
        """Send a message to another agent's inbox."""        
        self._require(f"MSG:{target_pid}")
        if target_pid not in self.kernel_ref.agents:
            raise ValueError(f"Target PID {target_pid} does not exist")
        
        self.kernel_ref.broker.mailboxes[target_pid].add(message)
        
    def receive(self):
        """Pop the next message from this agent's inbox, or None if empty."""
        self._require(f"MSG:{self.pid}")
        inbox = self.kernel_ref.broker.mailboxes.get(self.pid)
        if inbox is not None:
            return inbox.receive()
        return None
    

    # -- pub/sub ------------------------------------------------------------

    def publish(self, topic: str, message: Message):
        """Publish a message to every subscriber of `topic`."""
        self._require(f"MSG:{topic}")
        for subscriber_pid in self.kernel_ref.broker.topics.get(topic, set()):
            inbox = self.kernel_ref.broker.mailboxes.get(subscriber_pid)
            if inbox is not None:
                inbox.add(message)

    def subscribe(self, topic: str):
        """Subscribe the calling agent to `topic`."""
        self._require(f"MSG:{topic}")
        self.kernel_ref.broker.topics.setdefault(topic, set()).add(self.pid)

    # -- memory -------------------------------------------------------------

    def mem_alloc(self, name: str):
        """Open a shared segment owned by the calling agent."""
        self._require(f"MEM:{name}")
        self.kernel_ref.store.alloc(name, self.pid)

    def mem_attach(self, name: str):
        """Attach to an existing segment; returns its current value."""
        self._require(f"MEM:{name}")
        return self.kernel_ref.store.attach(name, self.pid)

    def mem_read(self, name: str):
        """Read the value of a shared segment."""
        self._require(f"MEM:{name}")
        return self.kernel_ref.store.read(name, self.pid)

    def mem_write(self, name: str, value):
        """Write a value to a shared segment (owner-only, enforced by store)."""
        self._require(f"MEM:{name}")
        self.kernel_ref.store.write(name, self.pid, value)

    def mem_free(self, name: str):
        """Release the calling agent's reference to a shared segment."""
        self._require(f"MEM:{name}")
        self.kernel_ref.store.free(name, self.pid)

    # -- resources ----------------------------------------------------------

    def request_tokens(self, amount: int):
        """Add `amount` tokens to the calling agent's budget."""
        self._require(f"TOKENS:{amount}")
        self._caller_acb().token_budget += amount

    def call_tool(self, tool_name: str, args: dict) -> dict:
        """Call an external tool and return its result."""
        self._require(f"TOOL:{tool_name}")
        # Placeholder dispatch: a real kernel would route to a tool registry.
        return {"result": "success", "tool": tool_name, "args": args}
