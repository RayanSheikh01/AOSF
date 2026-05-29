"""AgentOS — a kernel-style operating layer for a pool of LLM-backed agents.

Applies OS-design principles (process scheduling, memory allocation, permission
scoping, inter-agent messaging) to manage a pool of agents the way a kernel manages
processes.

Public exports are wired up incrementally as subsystems land (see IMPLEMENTATION_PLAN.md).
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
