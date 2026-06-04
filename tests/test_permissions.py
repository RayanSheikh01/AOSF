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


def test_wildcard_grants_specific():
    # MSG:* grants MSG:7
    assert CapabilitySet(["MSG:*"]).has("MSG:7")


def test_specific_does_not_grant_other():
    # MSG:7 does not grant MSG:8
    assert not CapabilitySet(["MSG:7"]).has("MSG:8")


def test_subset_of():
    parent = CapabilitySet(["MSG:7", "MSG:8", "MEM:0"])
    child = CapabilitySet(["MSG:7"])

    # child capabilities are a subset of parent -> True
    assert child.subset_of(parent)
    # parent has caps the child lacks -> False
    assert not parent.subset_of(child)


def test_subset_of_via_wildcard():
    # A wildcard parent grants the child's specific capability.
    assert CapabilitySet(["MSG:7"]).subset_of(CapabilitySet(["MSG:*"]))
