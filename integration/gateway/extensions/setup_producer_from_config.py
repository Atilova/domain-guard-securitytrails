from pika.adapters.blocking_connection import BlockingChannel

from infrastructure.config import GatewayConfig


def setup_producer_from_config(*, channel: BlockingChannel, config: GatewayConfig):
    """setup"""

    exchange_name = config.producer_exchange
    queue_name = config.producer_queue

    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type='direct',
        durable=False
    )

    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            'x-single-active-consumer': True
        }
    )

    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name,
        routing_key=config.producer_routing_key
    )