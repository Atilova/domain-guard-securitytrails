from time import sleep
from random import randrange


def rsleep(min=1, max=2):
    """rsleep"""

    if min == max: return sleep(min)

    sleep(randrange(min, max))

def get_rsleep(min, max):
    """create_rsleep"""

    return lambda: rsleep(min, max)