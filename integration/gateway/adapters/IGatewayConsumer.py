from typing import Protocol, runtime_checkable

from pika.adapters.blocking_connection import BlockingChannel


@runtime_checkable
class ConsumerFunction(Protocol):
    """ConsumerFunction"""
    
    def __call__(self, channel: BlockingChannel, *args, **kwargs) -> None:
        pass


class IGatewayConsumer(Protocol):
    """IGatewayConsumer"""

    def require_channel(self, function: ConsumerFunction) -> ConsumerFunction:
        pass

    def run(self):
        pass

    def stop(self):
        pass