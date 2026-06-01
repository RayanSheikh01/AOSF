class Monitor:

    def __init__(self, kernel):
        self.kernel = kernel
    
    def snapshot(self) -> str:
        # Header
        lines = ["PID | State   | Priority | Tokens Used/Budget | Cost USD | Mailbox Depth",
                 "----|---------|----------|--------------------|----------|--------------"]
        
        # Rows
        for pid, acb in self.kernel.agent_control_blocks.items():
            state = acb.state.name
            priority = acb.priority
            tokens_used = acb.token_budget - acb.token_budget  # Placeholder, as we don't track used tokens separately in this implementation
            tokens_budget = acb.token_budget
            cost_usd = tokens_used * self.kernel.config.get("token_cost_usd", 0.0001)  # Example cost calculation
            mailbox_depth = len(self.kernel.inboxes[pid])
            
            lines.append(f"{pid:3} | {state:7} | {priority:8} | {tokens_used}/{tokens_budget:16} | ${cost_usd:.4f} | {mailbox_depth:13}")
        
        return "\n".join(lines)