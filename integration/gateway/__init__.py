from config import conf

from functools import partial

from integration.interactor import InteractorFactory
from integration.gateway.consumers.securitytrails import SecurityTrailsConsumer
from integration.gateway.producers.securitytrails import SecurityTrailsProducer
from integration.gateway.services.notifier import GatewayApiKeyNotifier
from integration.gateway.extensions.setup_consumer_from_config import setup_consumer_from_config
from integration.gateway.extensions.setup_producer_from_config import setup_producer_from_config

from domain.Services.orchestrator import OrchestratorService
from domain.Services.storage import StorageService

from infrastructure.redis.main import get_redis_factory
from infrastructure.orchestrator.main import ProcessOrchestrator
from infrastructure.repositories.storage.json import JsonStorageRepository
from infrastructure.gateway.consumer import GatewayConsumer
from infrastructure.gateway.compose_gateway_params import compose_gateway_params


def create_app_factory() -> None:
    """create_app_factory"""

    orchestrator_service = OrchestratorService()
    orchestrator = ProcessOrchestrator(orchestrator_service,
									   workers=conf.job.processes,
									   max_tasks=conf.job.max_tasks)

    gateway_params = compose_gateway_params(conf.rabbitmq.uri)

    consumer = GatewayConsumer(gateway_params)

    consumer.require_channel(partial(setup_consumer_from_config, config=conf.gateway))
    consumer.require_channel(partial(setup_producer_from_config, config=conf.gateway))

    storage_service = StorageService()
    redis_client = get_redis_factory(conf.redis, conf.job.db)
    storage = JsonStorageRepository('job', storage_service, redis_client)

    ioc = InteractorFactory(orchestrator=orchestrator, storage=storage)

    securitytrails_producer = SecurityTrailsProducer(consumer=consumer, config=conf.gateway)

    notifier_request_storage = JsonStorageRepository('notifier:request', storage_service, redis_client)
    notifier_response_storage = JsonStorageRepository('notifier:response', storage_service, redis_client)
    notifier = GatewayApiKeyNotifier(producer=securitytrails_producer, request_storage=notifier_request_storage,
                                     response_storage=notifier_response_storage)

    securitytrails_consumer = SecurityTrailsConsumer(ioc=ioc, consumer=consumer,
                                                     notifier=notifier, config=conf.gateway)

    return consumer.run