from typing import Protocol, runtime_checkable


from pika.spec import Basic, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel


@runtime_checkable
class IConsumerCallback(Protocol):
    def __call__(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        pass