import pytest

from agentos.errors import CapabilityError
from agentos.permissions import CapabilitySet, require


def test_permissions():
    caps = CapabilitySet(["read", "write"])
    
    # Test has_capability
    assert caps.has_capability("read") == True
    assert caps.has_capability("write") == True
    assert caps.has_capability("execute") == False
    
    # Test add_capability
    caps.add_capability("execute")
    assert caps.has_capability("execute") == True
    
    # Test remove_capability
    caps.remove_capability("write")
    assert caps.has_capability("write") == False
    
    # Test require function
    require(caps, "read")  # Should not raise an error
    with pytest.raises(CapabilityError):
        require(caps, "write")  # Should raise an error since "write" was removed
    