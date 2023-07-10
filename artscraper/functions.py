"""

Functions used repeatedly, and in many places:

random_wait_time
retry

"""

import time
from random import random

def random_wait_time(min_wait=5, max_wait=None):
    """Compute a random wait time.

    This is a probability distribution with non-zero values between
    min_wait and max_wait. The PDF decreases as a powerlaw (**-1.5) between
    the two.

    Parameters
    ----------
    min_wait: int or float, default=5
        Minimum waiting time.
    max_wait: int or float, optional
        Maximum waiting time. If not supplied, use 3x
        minimum waiting time.

    Returns
    -------
    float:
        Waiting time between `min_wait` and `max_wait` according to
        the polynomial PDF.
    """

    #  pylint: disable=invalid-name
    if max_wait is None:
        max_wait = 3 * min_wait
    alpha = 1.5
    beta = alpha - 1
    b = min_wait
    c = max_wait
    a = -beta / (c**-beta - b**-beta)

    # def cdf(x):
    #     return a / beta * (b**-beta - x**-beta)

    def inv_cdf(x):
        return (b**-beta - beta * x / a)**(-1 / beta)

    return inv_cdf(random())


def retry(function, max_retries, min_wait_time, *args):
    '''
    Parameters
    ----------
    function: Function to run again
    max_retries: Maximum number of times to retry
    args: Arguments of the function

    Returns
    -------
    Value returned by function, or prints an error message
    '''

    # Want to catch all kinds of exceptions
    # pylint: disable=broad-except

    num_attempt = 0
    while num_attempt < max_retries:

        try:
            return function(*args)
        except Exception as error:
            print(f'Function {function} failed at attempt {num_attempt} \
            with exception {repr(error)}')
            time.sleep(random_wait_time(min_wait=min_wait_time))
            num_attempt = num_attempt + 1

    return None
