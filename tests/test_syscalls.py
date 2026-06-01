import pytest

from agentos.kernel import Kernel
from agentos.syscalls import SyscallContext

def test_syscall_context_spawn():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    
    # Test spawning a new agent
    new_pid = syscall_context.spawn(behavior=None, priority=3, capabilities=[], token_budget=100_000)
    assert new_pid == 1  # Since this is the first agent being spawned, it should have PID 1
    assert new_pid in kernel.agents
    assert new_pid in kernel.agent_control_blocks
    
def test_syscall_context_exit():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    
    # Spawn a new agent to exit
    new_pid = syscall_context.spawn(behavior=None, priority=3, capabilities=[], token_budget=100_000)
    
    # Test exiting the agent
    syscall_context.exit()
    assert kernel.agent_control_blocks[new_pid].state == "terminated"
    
def test_syscall_context_yield_cpu():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    
    # Spawn a new agent to yield
    new_pid = syscall_context.spawn(behavior=None, priority=3, capabilities=[], token_budget=100_000)
    
    # Test yielding the CPU
    syscall_context.yield_cpu()
    # Since the mock scheduler policy does nothing, we can't assert any changes here. In a real implementation, we'd want to check that the agent's state has changed appropriately.
    
def test_syscall_context_send_and_receive():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    sender_syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    receiver_syscall_context = SyscallContext(pid=2, kernel_ref=kernel)
    
    # Spawn a sender and receiver agent
    sender_pid = sender_syscall_context.spawn(behavior=None, priority=3, capabilities=["send"], token_budget=100_000)
    receiver_pid = receiver_syscall_context.spawn(behavior=None, priority=3, capabilities=["receive"], token_budget=100_000)

    # Test sending a message from the sender to the receiver
    message = {"text": "Hello, Agent 2!"}
    sender_syscall_context.send(target_pid=receiver_pid, message=message)

    # Receiver pops the delivered message off its inbox
    received_message = receiver_syscall_context.receive()
    assert received_message == message
    # Inbox is now empty
    assert receiver_syscall_context.receive() is None
    
def test_syscall_context_publish_and_subscribe():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    publisher_syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    subscriber_syscall_context = SyscallContext(pid=2, kernel_ref=kernel)
    
    # Spawn a publisher and subscriber agent
    publisher_pid = publisher_syscall_context.spawn(behavior=None, priority=3, capabilities=["publish"], token_budget=100_000)
    subscriber_pid = subscriber_syscall_context.spawn(behavior=None, priority=3, capabilities=["subscribe", "receive"], token_budget=100_000)

    # Test subscribing to a topic
    topic = "news"
    subscriber_syscall_context.subscribe(topic=topic)

    # Test publishing a message to the topic
    message = {"headline": "Breaking News!", "content": "This is a test of the publish-subscribe system."}
    publisher_syscall_context.publish(topic=topic, message=message)

    # The subscriber should have received the published message in its inbox
    assert subscriber_syscall_context.receive() == message

def test_syscall_context_permissions():
    kernel = Kernel(config={"cores": 1, "boost_interval": 10}, scheduler_policy=None)  # Use a mock scheduler policy for testing
    syscall_context = SyscallContext(pid=1, kernel_ref=kernel)
    
    # Spawn a new agent without permissions
    new_pid = syscall_context.spawn(behavior=None, priority=3, capabilities=[], token_budget=100_000)
    
    # Test that the agent cannot perform actions it doesn't have permissions for
    with pytest.raises(PermissionError):
        syscall_context.send(target_pid=new_pid, message={"text": "This should fail"})
    
    with pytest.raises(PermissionError):
        syscall_context.receive()
    
    with pytest.raises(PermissionError):
        syscall_context.publish(topic="test", message={"text": "This should also fail"})
    
    with pytest.raises(PermissionError):
        syscall_context.subscribe(topic="test")


