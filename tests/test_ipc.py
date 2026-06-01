import pytest

def test_ipc_send_and_receive():
    from agentos.ipc import Broker, Message
    
    broker = Broker()
    
    # Create a message and send it to a recipient
    message = Message(sender_pid=1, recipient_pid=2, content={"text": "Hello, Agent 2!"}, kind="greeting", correlation_id="123")
    broker.send(message)
    
    # The recipient should have the message in its mailbox
    assert 2 in broker.mailboxes
    received_message = broker.mailboxes[2].receive()
    assert received_message == message
    # The mailbox should now be empty
    assert broker.mailboxes[2].receive() is None
    
def test_ipc_publish_and_subscribe():
    from agentos.ipc import Broker, Message

    topics = {"news": {2, 3}}
    broker = Broker(topics=topics)
    
    # Subscribe two agents to a topic
    broker.subscribe(pid=2, topic="news")
    broker.subscribe(pid=3, topic="news")
    
    # Publish a message to the topic
    message = Message(sender_pid=1, recipient_pid=0, content={"headline": "Breaking News!", "content": "This is a test of the publish-subscribe system."}, kind="news", correlation_id="456")
    broker.publish(topic="news", message=message)
    
    # Both subscribers should have received the published message in their mailboxes
    assert 2 in broker.mailboxes
    assert 3 in broker.mailboxes
    assert broker.mailboxes[2].receive() == message
    assert broker.mailboxes[3].receive() == message