import pytest

from agentos.memory.store import SharedStore
from agentos.errors import SegmentError


def test_alloc_write_read_round_trips():
    store = SharedStore()
    store.alloc(name="var1", owner_pid=1)
    assert store.attach(name="var1", pid=2) is None
    store.write(name="var1", pid=1, value="Hello, World!")
    assert store.read(name="var1", pid=2) == "Hello, World!"


def test_refcount_lifecycle_reclaims_at_zero():
    store = SharedStore()
    store.alloc(name="seg", owner_pid=1)   # refs = 1
    store.attach(name="seg", pid=2)        # refs = 2
    store.attach(name="seg", pid=3)        # refs = 3

    store.free(name="seg", pid=3)          # refs = 2, still alive
    assert store.read(name="seg", pid=2) is None

    store.free(name="seg", pid=2)          # refs = 1, still alive
    store.free(name="seg", pid=1)          # refs = 0, reclaimed

    with pytest.raises(SegmentError):
        store.read(name="seg", pid=2)


def test_non_owner_write_raises():
    store = SharedStore()
    store.alloc(name="seg", owner_pid=1)
    with pytest.raises(SegmentError):
        store.write(name="seg", pid=2, value="denied")


def test_duplicate_alloc_raises():
    store = SharedStore()
    store.alloc(name="seg", owner_pid=1)
    with pytest.raises(SegmentError):
        store.alloc(name="seg", owner_pid=1)


def test_free_missing_segment_raises():
    store = SharedStore()
    with pytest.raises(SegmentError):
        store.free(name="nope", pid=1)
