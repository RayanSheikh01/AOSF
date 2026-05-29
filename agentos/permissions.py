from agentos.errors import CapabilityError

class CapabilitySet:
    def __init__(self, capabilities):
        self.capabilities = set(capabilities)

    def has_capability(self, capability):
        return capability in self.capabilities

    def add_capability(self, capability):
        self.capabilities.add(capability)

    def remove_capability(self, capability):
        self.capabilities.discard(capability)

    def __str__(self):
        return f"CapabilitySet({self.capabilities})"
    
def require(caps, cap):
    if not caps.has_capability(cap):
        raise CapabilityError(f"Required capability '{cap}' not found in {caps}")