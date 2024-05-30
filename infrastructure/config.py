import os
from dataclasses import dataclass, field


def _boolean(value: str) -> bool:
    """_boolean"""

    return bool(int(value))


@dataclass
class RedisConfig:
    """RedisConfig"""

    host: str
    port: int = 6379
    user: str = ''
    password: str = ''
    uri: str = field(init=False)

    def __post_init__(self):
        self.uri = f'redis://{self.user}:{self.password}@{self.host}:{self.port}/'

    def get_db_uri(self, db):
        return f'{self.uri}{db}'


@dataclass
class CeleryConfig:
    """CeleryConfig"""

    broker: str
    backend: str


@dataclass
class JobConfig:
    """JobConfig"""

    db: int
    processes: int
    max_tasks: int


@dataclass
class ApiServerConfig:
    """ApiServerConfig"""

    host: str
    port: int
    api_key: str


@dataclass
class DriverConfig:
    """WebDriverConfig"""

    is_headless: bool


@dataclass
class RabbitmqConfig:
    """RabbitmqConfig"""

    host: str
    port: int
    user: str
    password: str
    is_ssl: bool
    v_host: str = '/'
    uri: str = field(init=False)

    def __post_init__(self):
        protocol = { True: 'amqps://', False: 'amqp://' }[self.is_ssl]
        self.uri = f'{protocol}{self.user}:{self.password}@{self.host}:{self.port}{self.v_host}'


@dataclass
class GatewayConfig:
    """GatewayConfig"""

    consumer_exchange: str
    consumer_queue: str
    consumer_routing_key: str
    producer_exchange: str
    producer_queue: str
    producer_routing_key: str


@dataclass
class Config:
    """Config"""

    is_development: bool
    redis: RedisConfig
    celery: CeleryConfig
    job: JobConfig
    api: ApiServerConfig
    driver: DriverConfig
    rabbitmq: RabbitmqConfig
    gateway: GatewayConfig


def load_redis_config() -> RedisConfig:
    """load_redis_config"""

    host: str = os.environ.get('REDIS_HOST', 'localhost')
    port: int = int(os.environ.get('REDIS_PORT', 6379))
    user: str = os.environ.get('REDIS_USER', '')
    password: str = os.environ.get('REDIS_PASSWORD', '')

    return RedisConfig(
        host=host,
        port=port,
        user=user,
        password=password
    )

def load_celery_config(redis: RedisConfig) -> CeleryConfig:
    """load_celery_config"""

    db: int = int(os.environ.get('CELERY_REDIS_DB', 0))
    uri = redis.get_db_uri(db)

    return CeleryConfig(broker=uri, backend=uri)

def load_job_config() -> JobConfig:
    """load_jobs_config"""

    db: int = int(os.environ.get('JOB_REDIS_DB', 1))
    processes: int = int(os.environ.get('JOB_PROCESSES', 3))
    max_tasks: int = int(os.environ.get('JOB_MAX_TASKS', 6))

    return JobConfig(
        db=db,
        processes=processes,
        max_tasks=max_tasks
    )

def load_api_config() -> ApiServerConfig:
    """load_api_config"""

    host: str = os.environ.get('API_DEV_HOST', '0.0.0.0')
    port: int = int(os.environ.get('API_DEV_PORT', 3000))
    api_key: str = os.environ.get('API_ACCESS_API_KEY', '')

    return ApiServerConfig(host=host, port=port, api_key=api_key)

def load_driver_config() -> DriverConfig:
    """load_driver_config"""

    is_headless: bool = _boolean(os.environ.get('DRIVER_IS_HEADLESS', False))

    return DriverConfig(is_headless=is_headless)

def load_rabbitmq_config() -> RabbitmqConfig:
    """load_rabbitmq_config"""

    host: str = os.environ.get('RABBITMQ_HOST', 'localhost')
    port: int = int(os.environ.get('RABBITMQ_PORT', 5672))
    user: str = os.environ.get('RABBITMQ_USER', 'guest')
    password: str = os.environ.get('RABBITMQ_PASSWORD', 'guest')
    v_host: str = os.environ.get('RABBITMQ_V_HOST', '/')
    is_ssl: bool = _boolean(os.environ.get('RABBITMQ_IS_SSL', False))

    return RabbitmqConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        v_host=v_host,
        is_ssl=is_ssl
    )

def load_gateway_config() -> GatewayConfig:
    """load_gateway_config"""

    consumer_exchange: str = os.environ.get('GATEWAY_CONSUMER_EXCHANGE', 'exchange')
    consumer_queue: str = os.environ.get('GATEWAY_CONSUMER_QUEUE', 'consumer.default')
    consumer_routing_key: str = os.environ.get('GATEWAY_CONSUMER_ROUTING_KEY', 'consumer.key')
    producer_exchange: str = os.environ.get('GATEWAY_PRODUCER_EXCHANGE', 'exchange')
    producer_queue: str = os.environ.get('GATEWAY_PRODUCER_QUEUE', 'producer.res')
    producer_routing_key: str = os.environ.get('GATEWAY_PRODUCER_ROUTING_KEY', 'producer.res')

    return GatewayConfig(
        consumer_exchange=consumer_exchange,
        consumer_queue=consumer_queue,
        consumer_routing_key=consumer_routing_key,
        producer_exchange=producer_exchange,
        producer_queue=producer_queue,
        producer_routing_key=producer_routing_key
    )

def load() -> Config:
    """load"""

    is_development: bool = _boolean(os.environ.get('IS_DEVELOPMENT', True))
    redis = load_redis_config()
    celery = load_celery_config(redis)
    job = load_job_config()
    api = load_api_config()
    driver = load_driver_config()
    rabbitmq = load_rabbitmq_config()
    gateway = load_gateway_config()

    return Config(
        is_development=is_development,
        redis=redis,
        celery=celery,
        job=job,
        api=api,
        driver=driver,
        rabbitmq=rabbitmq,
        gateway=gateway
    )