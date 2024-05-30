from pika.adapters.blocking_connection import BlockingChannel

from integration.gateway.adapters.IConsumerCallback import IConsumerCallback


def register_consumer(channel: BlockingChannel, queue: str, 
                       callback: IConsumerCallback, **params):
    """register_callback"""

    channel.basic_consume(
        queue=queue, 
        on_message_callback=callback,
        **params
    )