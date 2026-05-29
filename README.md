# AgentOS

A lightweight **"operating system" layer for a pool of LLM-backed agents**. Instead of
one agent per task, AgentOS manages many agents the way a kernel manages processes:
process scheduling, memory allocation, permission scoping, and inter-agent messaging.

Backed by a **free, local LLM via [Ollama](https://ollama.com)** — no API key, no rate
limits. The LLM backend sits behind an `LLMProvider` interface, so it can be swapped
without touching the kernel.

## The core analogy

| OS concept           | AgentOS mapping                                              |
|----------------------|-------------------------------------------------------------|
| Process              | Agent (local LLM-backed worker)                             |
| PCB                  | `AgentControlBlock` (pid, priority, state, budgets, caps)   |
| CPU core             | Dispatcher worker (asyncio task) running one agent at a time |
| Scheduler            | Multi-level feedback queue (priority + anti-starvation boost)|
| fork()               | `spawn` syscall — child inherits subset of parent caps      |
| RAM / paging         | Token-budget allocator; context compaction under pressure   |
| Heap / shared memory | Shared store: named segments, refcounted, alloc/attach/free |
| Syscalls             | Only path agents reach the kernel; perms checked here       |
| IPC                  | Per-agent mailboxes + pub/sub channels                      |
| Device drivers       | Tool registry — agents call tools via gated syscall         |
| top / ps             | `monitor` — live view of agents, states, budgets, queues    |

## Status

Early development. Build order and design live in
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

## Setup

```bash
pip install -e ".[dev]"

# For the live demo (not needed for tests):
ollama pull llama3.2
```

The full test suite runs without Ollama — the kernel is exercised by `MockAgent` and a
`FakeProvider`, so `pytest` is free and deterministic.

```bash
pytest -q
```
