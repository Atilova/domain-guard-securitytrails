import logging.config

from integration import create_rabbitmq_factory


logging.config.fileConfig('logger.conf')


if __name__ == '__main__':
	app = create_rabbitmq_factory()
	app()