import logging

from json import dumps

from typing import Any

from pika.adapters.blocking_connection import BlockingChannel

from integration.gateway.adapters.IGatewayConsumer import IGatewayConsumer

from infrastructure.config import GatewayConfig


logger = logging.getLogger('SecurityTrailsProducer')


class SecurityTrailsProducer:
    def __init__(self, *,
        consumer: IGatewayConsumer,
        config: GatewayConfig,
    ):
        self.__consumer = consumer
        self.__config = config
        self.__channel: BlockingChannel = None

        self.__consumer.require_channel(self.__update_channel)

    def __update_channel(self, channel: BlockingChannel):
        self.__channel = channel

    def __is_allowed(self):
        return self.__channel is not None and self.__channel.is_open

    def produce_json(self, data: dict[str, Any]):
        if not self.__is_allowed:
            return logger.warn('Channel is not ready.')

        try:
            body = dumps(data)
        except TypeError as exp:
            return logger.exception('Failed to parse JSON.')

        try:
            self.__channel.basic_publish(
                exchange=self.__config.producer_exchange,
                routing_key=self.__config.producer_routing_key,
                body=body
            )
        except Exception as exp:
            logger.exception('Failed to publish message.')

