import pytest

async def test_providers():
    from agentos.providers import FakeProvider

    provider = FakeProvider()
    response = await provider.chat(messages=[{"role": "user", "content": "Hello"}], model="fake-model")
    assert response.text == "This is a fake response."

    