class KernelError(Exception):
    """Base class for all exceptions raised by the kernel."""
    pass

class CapabilityError(KernelError):
    """Raised when a capability is not found or cannot be used."""
    pass

class OutOfTokensError(KernelError):
    """Raised when the kernel runs out of tokens to execute a task."""
    pass

class NoSuchAgentError(KernelError):
    pass

class SegmentError(KernelError):
    pass