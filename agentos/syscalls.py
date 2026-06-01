from typing import Optional

from agentos import permissions
from agentos.permissions import CapabilitySet
from agentos.errors import CapabilityError, SegmentError
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
        """Raise PermissionError if the calling agent lacks `capability`."""
        acb = self._caller_acb()
        caps = CapabilitySet(acb.capabilities)
        try:
            permissions.require(caps, capability)
        except CapabilityError as exc:
            raise PermissionError(
                f"Agent {self.pid} lacks capability '{capability}'"
            ) from exc

    # -- process control (ungated bootstrap syscalls) -----------------------

    def spawn(self, behavior: StepResult, priority: int = 3, capabilities: list[str] = [], token_budget: int = 100_000) -> int:
        """Spawn a new agent with the given behavior and return its PID."""
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

    def send(self, target_pid: int, message: dict):
        """Send a message to another agent's inbox."""
        self._require("send")
        if target_pid not in self.kernel_ref.agents:
            raise ValueError(f"Target PID {target_pid} does not exist")
        self.kernel_ref.inboxes[target_pid].append(message)

    def receive(self) -> Optional[dict]:
        """Pop the next message from this agent's inbox, or None if empty."""
        self._require("receive")
        inbox = self.kernel_ref.inboxes.get(self.pid)
        if inbox:
            return inbox.popleft()
        return None

    # -- pub/sub ------------------------------------------------------------

    def publish(self, topic: str, message: dict):
        """Publish a message to every subscriber of `topic`."""
        self._require("publish")
        for subscriber_pid in self.kernel_ref.topics.get(topic, set()):
            inbox = self.kernel_ref.inboxes.get(subscriber_pid)
            if inbox is not None:
                inbox.append(message)

    def subscribe(self, topic: str):
        """Subscribe the calling agent to `topic`."""
        self._require("subscribe")
        self.kernel_ref.topics.setdefault(topic, set()).add(self.pid)

    # -- memory -------------------------------------------------------------

    def mem_alloc(self, size: int) -> int:
        """Allocate a block of memory and return its base address."""
        self._require("mem_alloc")
        address = self.kernel_ref.next_address
        self.kernel_ref.next_address += size
        self.kernel_ref.memory[address] = bytearray(size)
        return address

    def mem_attach(self, address: int):
        """Validate that a block exists at `address`."""
        self._require("mem_attach")
        if address not in self.kernel_ref.memory:
            raise SegmentError(f"No memory block at address {hex(address)}")

    def mem_read(self, address: int, size: int) -> bytes:
        """Read `size` bytes from the block at `address`."""
        self._require("mem_read")
        block = self.kernel_ref.memory.get(address)
        if block is None:
            raise SegmentError(f"No memory block at address {hex(address)}")
        return bytes(block[:size])

    def mem_write(self, address: int, data: bytes):
        """Write `data` into the block at `address`."""
        self._require("mem_write")
        block = self.kernel_ref.memory.get(address)
        if block is None:
            raise SegmentError(f"No memory block at address {hex(address)}")
        if len(data) > len(block):
            raise SegmentError(
                f"Write of {len(data)} bytes exceeds block size {len(block)}"
            )
        block[: len(data)] = data

    def mem_free(self, address: int):
        """Free the block at `address`."""
        self._require("mem_free")
        if self.kernel_ref.memory.pop(address, None) is None:
            raise SegmentError(f"No memory block at address {hex(address)}")

    # -- resources ----------------------------------------------------------

    def request_tokens(self, amount: int):
        """Add `amount` tokens to the calling agent's budget."""
        self._require("request_tokens")
        self._caller_acb().token_budget += amount

    def call_tool(self, tool_name: str, args: dict) -> dict:
        """Call an external tool and return its result."""
        self._require("call_tool")
        # Placeholder dispatch: a real kernel would route to a tool registry.
        return {"result": "success", "tool": tool_name, "args": args}
