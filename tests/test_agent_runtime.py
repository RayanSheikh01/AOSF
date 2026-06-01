import pytest

async def test_agent_runtime():
    from agentos.agent_runtime import LLMAgent
    
    agent = LLMAgent()
    response = await agent.chat(messages=[{"role": "user", "content": "Hello"}], model="test-model")
    assert response.text == "This is a response from the LLM agent."
    assert response.prompt_tokens == 15
    assert response.completion_tokens == 10