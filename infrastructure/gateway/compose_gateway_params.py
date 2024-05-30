from urllib.parse import urlparse

from pika import PlainCredentials, ConnectionParameters


def compose_gateway_params(uri: str) -> ConnectionParameters:
    """compose_gateway_params"""

    # Todo: add SSL parameters
    parsed_url = urlparse(uri)

    credentials = PlainCredentials(username=parsed_url.username,
                                   password=parsed_url.password)

    return ConnectionParameters(host=parsed_url.hostname, port=parsed_url.port,
                                virtual_host=parsed_url.path, credentials=credentials)