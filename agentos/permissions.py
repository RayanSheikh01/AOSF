from agentos.errors import CapabilityError

class CapabilitySet:
    def __init__(self, capabilities):
        self.capabilities = set(capabilities)

    def has(self, capability):
        match = capability in self.capabilities or "*" in self.capabilities or any(capability.startswith(prefix[:-1]) for prefix in self.capabilities if prefix.endswith("*"))
        return match

    def has_capability(self, capability):
        return capability in self.capabilities

    def subset_of(self, other):
        """True if every capability here is granted by `other` (self ⊆ other).

        Uses `other.has` so a wildcard in the parent (e.g. ``MSG:*``) covers a
        specific capability in the child."""
        return all(other.has(capability) for capability in self.capabilities)

    def add_capability(self, capability):
        self.capabilities.add(capability)

    def remove_capability(self, capability):
        self.capabilities.discard(capability)

    def __str__(self):
        return f"CapabilitySet({self.capabilities})"
    
def require(caps, cap):
    if not caps.has(cap):
        raise CapabilityError(f"Required capability '{cap}' not found in {caps}")