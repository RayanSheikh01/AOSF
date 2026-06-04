from agentos.errors import SegmentError


class SharedStore:
    """In-memory key/value store of named segments shared between agents.

    Each segment is ``{owner, value, refs}``. ``alloc`` opens a segment with
    one reference (the owner's); ``attach`` adds a reference; ``free`` drops
    one and reclaims the segment when the count reaches zero.
    """

    def __init__(self):
        self.store = {}

    def _segment(self, name):
        seg = self.store.get(name)
        if seg is None:
            raise SegmentError(f"Shared segment '{name}' does not exist")
        return seg

    def alloc(self, name, owner_pid):
        """Open a new segment owned by ``owner_pid``. Duplicate name fails."""
        if name in self.store:
            raise SegmentError(f"Shared segment '{name}' already exists")
        self.store[name] = {"owner": owner_pid, "value": None, "refs": 1}

    def attach(self, name, pid):
        """Add a reference to an existing segment. Returns the current value."""
        seg = self._segment(name)
        seg["refs"] += 1
        return seg["value"]

    def read(self, name, pid):
        """Read the value of a segment."""
        return self._segment(name)["value"]

    def write(self, name, pid, value):
        """Write a new value to a segment. Only the owner may write."""
        seg = self._segment(name)
        if seg["owner"] != pid:
            raise SegmentError(f"PID {pid} is not the owner of segment '{name}'")
        seg["value"] = value

    def free(self, name, pid):
        """Drop a reference; reclaim the segment when the count hits zero."""
        seg = self._segment(name)
        seg["refs"] -= 1
        if seg["refs"] <= 0:
            del self.store[name]
