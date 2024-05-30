from flask import Flask

from config import conf

from integration.interactor import InteractorFactory
from integration.api.extensions.configure_app import configure_app
from integration.api.extensions.register_routes import register_routes
from integration.api.extensions.register_dependency_injection import register_dependency_injection

from domain.Services.orchestrator import OrchestratorService
from domain.Services.storage import StorageService

from infrastructure.orchestrator.main import ProcessOrchestrator
from infrastructure.redis.main import get_redis_factory
from infrastructure.repositories.storage.json import JsonStorageRepository


def create_app_factory() -> Flask:
    """create_app_factory"""

    orchestrator_service = OrchestratorService()
    orchestrator = ProcessOrchestrator(orchestrator_service,
									   workers=conf.job.processes,
									   max_tasks=conf.job.max_tasks)
    
    storage_service = StorageService()
    redis_client = get_redis_factory(conf.redis, conf.job.db)
    storage = JsonStorageRepository('job', storage_service, redis_client)

    ioc = InteractorFactory(orchestrator=orchestrator, storage=storage)
    
    app = Flask(__name__)
    configure_app(app)
    register_routes(app)
    register_dependency_injection(app, ioc=ioc)

    return app