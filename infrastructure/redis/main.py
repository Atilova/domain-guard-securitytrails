from redis import StrictRedis

from infrastructure.config import RedisConfig


def get_redis_factory(config: RedisConfig, db: int=0, **kwargs) -> StrictRedis:
    """get_redis_factory"""

    return StrictRedis(
        db=db,
        host=config.host,
        port=config.port,
        password=config.password,
        **kwargs
    )