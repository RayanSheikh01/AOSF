

import asyncio
from typing import Protocol


class Tool(Protocol):
    name: str
    description: str
    
    async def run(self, **kwargs) -> dict:
        ...
        

class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Tool:
        tool = self.tools.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        return tool
    
    
def call_tool(tool_registry: ToolRegistry, tool_name: str, **kwargs) -> dict:
    tool = tool_registry.get(tool_name)
    return asyncio.run(tool.run(**kwargs))


