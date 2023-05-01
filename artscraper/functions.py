'''
random_wait_time: Function to determine a random wait time
between two events
'''

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
