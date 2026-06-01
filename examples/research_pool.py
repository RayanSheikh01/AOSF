import pytest

from agentos.kernel import Kernel
from agentos.scheduler import MLFQ
from agentos.process import StepResult
from agentos.providers import OllamaProvider


MODEL = "llama3.2"

SUBTOPICS = [
    "the role of mitochondria in a cell, in one sentence",
    "why the sky appears blue, in one sentence",
    "what causes ocean tides, in one sentence",
]


# --- agent behaviors --------------------------------------------------------


class WorkerAgent:
    """Receives one subtopic via IPC, asks the LLM, writes the answer to the
    shared store segment it owns, then exits."""

    def __init__(self, provider, model):
        self.provider = provider
        self.model = model

    async def step(self, ctx) -> StepResult:
        msg = ctx.receive()  # gated by the "receive" capability
        if msg is None:
            # Task not delivered yet — give up the CPU and try again later.
            return StepResult(kind="yield")

        task = msg["task"]
        segment = msg["segment"]

        response = await self.provider.chat(
            messages=[{"role": "user", "content": task}],
            model=self.model,
        )

        # Share findings: the worker owns this segment, so the write is allowed.
        ctx.kernel_ref.store.write(segment, ctx.pid, response.text.strip())

        # Real local token accounting so the monitor shows actual usage.
        acb = ctx.kernel_ref.agent_control_blocks[ctx.pid]
        acb.tokens_used += response.prompt_tokens + response.completion_tokens

        return StepResult(kind="done")


class CoordinatorAgent:
    """Spawns one worker per subtopic, delegates via IPC, then polls the shared
    store until every worker has reported, and exits."""

    def __init__(self, provider, model, subtopics):
        self.provider = provider
        self.model = model
        self.subtopics = subtopics
        self.phase = "spawn"
        self.worker_pids: list[int] = []
        self.polls = 0

    async def step(self, ctx) -> StepResult:
        store = ctx.kernel_ref.store

        if self.phase == "spawn":
            for task in self.subtopics:
                wpid = ctx.spawn(  # spawn is an ungated bootstrap syscall
                    behavior=WorkerAgent(self.provider, self.model),
                    priority=3,
                    capabilities=["receive"],
                    token_budget=10_000,
                )
                self.worker_pids.append(wpid)
                segment = f"findings:{wpid}"
                # Worker owns its segment so only it can write the result.
                store.alloc(segment, owner_pid=wpid)
                ctx.send(wpid, {"task": task, "segment": segment})  # needs "send"
            self.phase = "await"
            return StepResult(kind="yield")

        # Await phase: yield until every worker has written its findings.
        self.polls += 1
        all_done = all(
            store.read(f"findings:{pid}", ctx.pid) is not None
            for pid in self.worker_pids
        )
        if all_done or self.polls > 500:
            return StepResult(kind="done")
        return StepResult(kind="yield")


# --- Ollama availability probe ----------------------------------------------


def _ollama_ready(model: str) -> tuple[bool, str]:
    """Return (ready, reason). Ready only if the server responds and `model`
    is pulled."""
    try:
        import ollama
    except ImportError:
        return False, "the 'ollama' package is not installed (pip install ollama)"

    try:
        listed = ollama.list()
    except Exception as exc:  # server down / not installed
        return False, f"no Ollama server reachable ({exc})"

    names = []
    for m in getattr(listed, "models", []) or []:
        name = getattr(m, "model", None) or (m.get("name") if isinstance(m, dict) else None)
        if name:
            names.append(name)

    if not any(model in n for n in names):
        return False, f"model '{model}' not pulled (run: ollama pull {model})"
    return True, "ok"


# --- driver -----------------------------------------------------------------


def run_demo() -> str:
    kernel = Kernel(
        config={"cores": 2, "boost_interval": 10, "token_cost_usd": 0.0001},
        scheduler_policy=MLFQ(num_queues=3),
    )
    provider = OllamaProvider()

    kernel.spawn(
        behavior=CoordinatorAgent(provider, MODEL, SUBTOPICS),
        priority=0,
        capabilities=["send"],
        token_budget=20_000,
    )

    kernel.run(until_idle=True)

    # Print the findings each worker shared via the store.
    print("\n=== Research findings (shared via the store) ===")
    for name, entry in kernel.store.store.items():
        print(f"[{name}] {entry['value']}")

    snapshot = kernel.monitor.snapshot()
    print("\n=== monitor.snapshot() ===")
    print(snapshot)
    return snapshot


def test_research_pool():
    ready, reason = _ollama_ready(MODEL)
    if not ready:
        pytest.skip(f"Skipping live Ollama demo: {reason}")
    snapshot = run_demo()
    assert "PID" in snapshot


if __name__ == "__main__":
    ready, reason = _ollama_ready(MODEL)
    if not ready:
        print(f"Skipping live Ollama demo: {reason}")
    else:
        run_demo()
