import logging

from functools import partial

from typing import Any

from pika.spec import Basic, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel

from .events import ConsumerEvents

from integration.adapters.IInteractorFactory import IInteractorFactory
from integration.gateway.adapters.IGatewayConsumer import IGatewayConsumer
from integration.gateway.adapters.IGatewayApiKeyNotifier import IGatewayApiKeyNotifier
from integration.gateway.extensions.auto_ack import auto_ack
from integration.gateway.extensions.serializers import json_obj_only
from integration.gateway.extensions.register_consumer import register_consumer

from application.Dto.api_key import (
    NewApiKeyInputDTO,
    GetApiKeyInputDTO,
    ApiKeyCreationStatus
)

from infrastructure.config import GatewayConfig


logger = logging.getLogger('SecurityTrailsConsumer')


class SecurityTrailsConsumer:
    def __init__(self, *,
        ioc: IInteractorFactory,
        consumer: IGatewayConsumer,
        notifier: IGatewayApiKeyNotifier,
        config: GatewayConfig,
    ):
        self.__ioc = ioc
        self.__consumer = consumer
        self.__notifier = notifier
        self.__config = config

        self.__consumer.require_channel(partial(register_consumer, callback=self.router,
                                                queue=self.__config.consumer_queue))

    @json_obj_only
    @auto_ack
    def router(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, data: dict[str, Any]):
        event = data.get('event')
        request_id = data.get('_id')

        if request_id is None or not isinstance(request_id, str):
            return logger.warning(f'Request missing request id (_id) of type string for: {event}.')

        match event:
            case ConsumerEvents.FABRICATE_ACCOUNT:
                if self.__notifier.retrieve_by_id(request_id) is not None:
                    return logger.warning(f'Requested with _id ({request_id}) already exists.')

                with self.__ioc.fabricate_api_key() as fabricate_api_key:
                    output_dto = fabricate_api_key(NewApiKeyInputDTO(
                        notifier=self.__notifier
                    ))
                    if output_dto.status is ApiKeyCreationStatus.FORBIDDEN:
                        return self.__notifier.notify(request_id, output_dto)
                    self.__notifier.register(request_id, output_dto)

            case ConsumerEvents.RETRIEVE_ACCOUNT:
                job_id = self.__notifier.retrieve_by_id(request_id)
                with self.__ioc.retrieve_api_key() as retrieve_api_key:
                    output_dto = retrieve_api_key(GetApiKeyInputDTO(
                        id=job_id
                    ))
                    return self.__notifier.notify(request_id, output_dto)

            case _:
                logger.warning(f'Received unknown event: {event}.')