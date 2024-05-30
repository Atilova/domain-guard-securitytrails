from celery import Celery

from infrastructure.config import CeleryConfig


def get_celery_factory(name: str, config: CeleryConfig) -> Celery:
    """get_celery_factory"""

    return Celery(name, broker=config.broker, backend=config.backend)