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

Core kernel runs end-to-end: MLFQ scheduler, capability-gated syscalls, IPC
mailboxes, shared store, token-budget accounting, and a `ps`/`top`-style monitor.
Build order and design live in [imp_plan.md](imp_plan.md).

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

## Live demo

[`examples/research_pool.py`](examples/research_pool.py) is a real Ollama run: a
**coordinator** agent spawns one **worker** per subtopic, delegates each task over IPC,
and the workers share their answers back through the kernel's shared store. It prints the
findings and `kernel.monitor.snapshot()`.

```bash
pip install -e .          # so `import agentos` resolves outside pytest
ollama pull llama3.2      # one-time; or use any local model
python examples/research_pool.py
```

It skips with a clear message if no Ollama server / model is available, so it is safe to
run (and is collected by `pytest`) on machines without a model pulled.

Example output:

```
=== Research findings (shared via the store) ===
[findings:2] Mitochondria generate energy through cellular respiration, producing ATP...
[findings:3] The sky appears blue because air molecules scatter shorter blue wavelengths...
[findings:4] Ocean tides are caused by the gravitational pull of the Moon and the Sun...

=== monitor.snapshot() ===
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ PID ┃ State      ┃ Priority ┃ Tokens Used/Budget ┃ Cost USD ┃ Mailbox Depth ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 1   │ TERMINATED │ 2        │ 0/20000            │ $0.0000  │ 0             │
│ 2   │ TERMINATED │ 2        │ 77/10000           │ $0.0077  │ 0             │
│ 3   │ TERMINATED │ 2        │ 80/10000           │ $0.0080  │ 0             │
│ 4   │ TERMINATED │ 2        │ 73/10000           │ $0.0073  │ 0             │
└─────┴────────────┴──────────┴────────────────────┴──────────┴───────────────┘
```
