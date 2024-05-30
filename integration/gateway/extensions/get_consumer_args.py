def get_consumer_args(*args, **kwargs):
    """"_get_consumer_args"""

    if len(args) > 4:
        return (args[0],), (args[1:]), kwargs
    return tuple(), args, kwargs