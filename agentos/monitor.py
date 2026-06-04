try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    Console = Table = None


class Monitor:
    def __init__(self, kernel):
        self.kernel = kernel

    def _rows(self) -> list[tuple]:
        rows = []
        for pid, acb in self.kernel.agent_control_blocks.items():
            state = acb.state.name
            priority = acb.priority
            tokens_used = acb.tokens_used
            tokens_budget = acb.token_budget
            cost_usd = tokens_used * self.kernel.config.get("token_cost_usd", 0.0001)
            mailbox_depth = len(self.kernel.broker.mailboxes.get(pid, []))
            rows.append((
                str(pid),
                state,
                str(priority),
                f"{tokens_used}/{tokens_budget}",
                f"${cost_usd:.4f}",
                str(mailbox_depth),
            ))
        return rows

    def snapshot(self) -> str:
        columns = ["PID", "State", "Priority", "Tokens Used/Budget", "Cost USD", "Mailbox Depth"]
        rows = self._rows()
        if Console is None:
            return self._plain_table(columns, rows)

        console = Console()
        table = Table()
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)

        with console.capture() as capture:
            console.print(table)
        return capture.get()

    @staticmethod
    def _plain_table(columns: list[str], rows: list[tuple]) -> str:
        widths = [len(c) for c in columns]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        def fmt(cells):
            return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

        lines = [fmt(columns), fmt(["-" * w for w in widths])]
        lines.extend(fmt(row) for row in rows)
        return "\n".join(lines)
