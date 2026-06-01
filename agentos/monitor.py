from rich.console import Console
from rich.table import Table


class Monitor:
    def __init__(self, kernel):
        self.kernel = kernel
    
    def snapshot(self) -> str:
        console = Console()
        table = Table()
        table.add_column("PID")
        table.add_column("State")
        table.add_column("Priority")
        table.add_column("Tokens Used/Budget")
        table.add_column("Cost USD")
        table.add_column("Mailbox Depth")

        for pid, acb in self.kernel.agent_control_blocks.items():
            state = acb.state.name
            priority = acb.priority
            tokens_used = acb.tokens_used
            tokens_budget = acb.token_budget
            cost_usd = tokens_used * self.kernel.config.get("token_cost_usd", 0.0001)
            mailbox_depth = len(self.kernel.inboxes[pid])

            table.add_row(str(pid), state, str(priority), f"{tokens_used}/{tokens_budget}", f"${cost_usd:.4f}", str(mailbox_depth))

        with console.capture() as capture:
            console.print(table)
        return capture.get()