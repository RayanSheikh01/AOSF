
from pydantic.dataclasses import dataclass


@dataclass
class Message:
    sender_pid: int
    recipient_pid: int
    content: dict
    kind: str
    correlation_id: str
    
class Mailbox:
    def __init__(self):
        self.messages: list[Message] = []
    
    def send(self, message: Message):
        self.messages.append(message)
    
    def receive(self) -> Message | None:
        if self.messages:
            return self.messages.pop(0)
        return None
    
class Broker:
    def __init__(self, mailboxes: dict[int, Mailbox] = None, topics: dict[str, set[int]] = None):
        self.mailboxes: dict[int, Mailbox] = mailboxes if mailboxes is not None else {}
        self.topics: dict[str, set[int]] = topics if topics is not None else {}
    
    def send(self, message: Message):
        if message.recipient_pid not in self.mailboxes:
            self.mailboxes[message.recipient_pid] = Mailbox()
        self.mailboxes[message.recipient_pid].send(message)
    
    def publish(self, topic: str, message: Message):
        for subscriber_pid in self.topics.get(topic, set()):
            if subscriber_pid not in self.mailboxes:
                self.mailboxes[subscriber_pid] = Mailbox()
            self.mailboxes[subscriber_pid].send(message)

    def subscribe(self, pid: int, topic: str):
        pids = self.topics.setdefault(topic, set())
        pids.add(pid)
        


        