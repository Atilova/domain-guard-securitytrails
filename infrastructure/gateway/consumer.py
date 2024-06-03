import logging

from time import sleep

from typing import Protocol, runtime_checkable

from pika import BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError, ChannelWrongStateError


logger = logging.getLogger('GatewayConsumer')


@runtime_checkable
class ConsumerFunction(Protocol):
    """ConsumerFunction"""

    def __call__(self, channel: BlockingChannel, *args, **kwargs) -> None:
        pass


class GatewayConsumer:
    """GatewayConsumer"""

    def __init__(self, parameters: ConnectionParameters):
        self.__parameters = parameters
        self.__connection: BlockingConnection
        self.__channel: BlockingChannel
        self.__consumers: set[ConsumerFunction] = set()
        self.__running = False

    def require_channel(self, function):
        self.__consumers.add(function)
        return function

    def run(self):
        logger.info('Starting.')
        while True:
            try:
                connection = BlockingConnection(self.__parameters)
                if not connection.is_open:
                    logger.warning('Connection not open, retrying.')
                    continue

                logger.info('Connected to broker.')

                self.__connection = connection
                self.__channel = self.__connection.channel()
                self.__running = True

                self.__initiate_consumers()
                if not len(self.__channel.consumer_tags):
                    logger.warning('No queues subscribed to consume, quitting.')
                    return self.__shutdown()

                self.__channel.start_consuming()
            except KeyboardInterrupt:
                logger.info('Received keyboard interrupt, stopping.')
                return self.__shutdown()
            except AMQPConnectionError:
                self.__running = False
                logger.info('Failed to establish connection with broker.')
                sleep(5) # Todo: add coefficient
            except Exception as exp:
                logger.exception('Unexpected error encountered while running the consumer.')
                sleep(5) # Todo: add coefficient

    def stop(self):
        logger.info('Stop called, shutting down.')
        self.__shutdown()

    def __initiate_consumers(self):
        for consumer in self.__consumers:
            try:
                consumer(channel=self.__channel)
            except Exception as exp:
                name = getattr(consumer, '__name__', repr(consumer))
                logger.exception(f'Error initializing consumer: {name}.')

    def __shutdown(self):
        if not self.__running: return

        try:
            if self.__channel is not None and self.__channel.is_open:
                self.__channel.close()

            if self.__connection is not None and self.__connection.is_open:
                self.__channel.close()
        except ChannelWrongStateError as exp:
            logger.info('Closing encountered unexpected channel state.')

        self.__running = False