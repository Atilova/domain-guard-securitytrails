from json import loads, JSONDecodeError

from .get_consumer_args import get_consumer_args

from integration.gateway.adapters.IConsumerCallback import IConsumerCallback


def json_obj_only(function: IConsumerCallback):
    """json_obj_only"""

    def wrapper(*args, **kwargs):
        _, arguments, keyword_argument = get_consumer_args(*args, **kwargs)
        channel, method, properties, body = arguments

        try:
            data = loads(body)
            if not isinstance(data, dict): raise TypeError
        except (JSONDecodeError, TypeError):
            return channel.basic_ack(method.delivery_tag)

        return function(*_, channel, method, properties, data, **keyword_argument)
    return wrapper