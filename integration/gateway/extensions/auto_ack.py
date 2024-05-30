from .get_consumer_args import get_consumer_args

from integration.gateway.adapters.IConsumerCallback import IConsumerCallback


def auto_ack(function: IConsumerCallback):
    """auto_ack"""

    def wrapper(*args, **kwargs):
        _, arguments, keyword_argument = get_consumer_args(*args, **kwargs)
        channel, method, *_ = arguments

        result = function(*args, **kwargs)
        channel.basic_ack(method.delivery_tag)

        return result
    return wrapper