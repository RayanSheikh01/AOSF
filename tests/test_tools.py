import pytest

from agentos.tools import ToolRegistry


def test_tools():
    from agentos.tools import Tool, call_tool
    
    
    class Adder(Tool):
        name = "adder"
        description = "Adds two numbers"
        
        async def run(self, a: int, b: int) -> dict:
            return {"result": a + b}
    tool_registry = ToolRegistry()
    tool_registry.register(Adder())
    result = call_tool(tool_registry, "adder", a=2, b=3)
    assert result == {"result": 5}
    with pytest.raises(ValueError):
        call_tool(tool_registry, "nonexistent_tool")
        
    
    