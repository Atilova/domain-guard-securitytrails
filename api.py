import logging.config

from config import conf

from integration import create_flask_app_factory
from integration.api.extensions.str_routes import str_routes


logging.config.fileConfig('logger.conf')


if __name__ == '__main__' and conf.is_development:
	app = create_flask_app_factory()
	print(str_routes(app))
	app.run(debug=True, host='0.0.0.0', port=3000)