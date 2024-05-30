from pika.adapters.blocking_connection import BlockingChannel

from infrastructure.config import GatewayConfig


def setup_consumer_from_config(*, channel: BlockingChannel, config: GatewayConfig):
    """setup"""

    exchange_name = config.consumer_exchange
    queue_name = config.consumer_queue

    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type='direct',
        durable=False
    )

    channel.queue_declare(
        queue=queue_name,
        durable=False,
        arguments={
            'x-single-active-consumer': True
        }
    )

    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name,
        routing_key=config.consumer_routing_key
    )