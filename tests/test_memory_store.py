import pytest

def test_memory_store():
    from agentos.memory.store import SharedStore
    
    store = SharedStore()
    
    # Allocate a new shared variable
    store.alloc(name="var1", owner_pid=1)
    # Attach to the shared variable and check initial value
    value = store.attach(name="var1", pid=2)
    assert value is None
    # Write a value to the shared variable as the owner
    store.write(name="var1", pid=1, value="Hello, World!")
    # Read the value from another PID
    value = store.read(name="var1", pid=2)
    assert value == "Hello, World!"
    # Attempt to write from a non-owner PID should raise PermissionError
    with pytest.raises(PermissionError):
        store.write(name="var1", pid=2, value="This should fail")
    # Free the shared variable as the owner
    store.free(name="var1", pid=1)
    # Attempting to access the freed variable should raise ValueError
    with pytest.raises(ValueError):
        store.attach(name="var1", pid=2)
    with pytest.raises(ValueError):
        store.read(name="var1", pid=2)
    with pytest.raises(ValueError):
        store.write(name="var1", pid=1, value="This should also fail")
    with pytest.raises(ValueError):
        store.free(name="var1", pid=1)
        
