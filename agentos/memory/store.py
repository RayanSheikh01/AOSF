class SharedStore:
    """
    A simple in-memory key-value store for sharing data between agents.
    """
    def __init__(self):
        self.store = {}

    def alloc(self, name, owner_pid):
        """Allocate a new shared variable with the given name, owned by owner_pid."""
        if name in self.store:
            raise ValueError(f"Shared variable '{name}' already exists")
        self.store[name] = {"owner": owner_pid, "value": None}
    
    def attach(self, name, pid):
        """Attach to an existing shared variable. Returns the current value."""
        if name not in self.store:
            raise ValueError(f"Shared variable '{name}' does not exist")
        return self.store[name]["value"]
    
    def read(self, name, pid):
        """Read the value of a shared variable."""
        if name not in self.store:
            raise ValueError(f"Shared variable '{name}' does not exist")
        return self.store[name]["value"]
    
    def write(self, name, pid, value):
        """Write a new value to a shared variable. Only the owner can write."""
        if name not in self.store:
            raise ValueError(f"Shared variable '{name}' does not exist")
        if self.store[name]["owner"] != pid:
            raise PermissionError(f"PID {pid} is not the owner of shared variable '{name}'")
        self.store[name]["value"] = value

    def free(self, name, pid):
        """Free a shared variable. Only the owner can free."""
        if name not in self.store:
            raise ValueError(f"Shared variable '{name}' does not exist")
        if self.store[name]["owner"] != pid:
            raise PermissionError(f"PID {pid} is not the owner of shared variable '{name}'")
        del self.store[name]
        