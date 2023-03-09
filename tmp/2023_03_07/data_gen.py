import math
import numpy as np
import scipy.stats as ss

def __select_quantile_index(x, quantiles):
    m = len(quantiles)
    for i in range(0, m - 2):
        if quantiles[i] <= x and x < quantiles[i + 1]:
            return i
    return m - 2

def __K(x_top):
    '''
    K : [0, 1] -> [0, 1],
    K(x_top) = 1,
    K(x) < K(x_top) for all x in [0, 1]
    '''
    return (lambda x: 1 - abs(x - x_top))

def __get_probability_breakpoints(x, quantiles):
    m = len(quantiles)
    i = __select_quantile_index(x, quantiles)
    x_top = i + (x - quantiles[i]) / (quantiles[i + 1] - quantiles[i])
    K = __K(x_top / (m - 1))
    S = 0
    result = [ 0 ]
    for n in range(m):
        S += K(n / (m - 1))
        result.append(S)
    return np.array(result) / S

def __get_random_class(x, quantiles):
    r = np.random.rand()
    pb = __get_probability_breakpoints(x, quantiles)
    for i in range(len(quantiles)):
        if pb[i] <= r and r < pb[i + 1]:
            return i
    return len(quantiles) - 1

def generate_dependent_classes(m, distribution):
    '''
    Generates set of classes with dependency inspired by the given distribution.
    
    Keyword arguments:
    m -- the number of classes
    distribution -- the given distribution
    '''
    quantiles = [ np.quantile(distribution, i / (m - 1)) for i in range(m) ]
    return [ __get_random_class(x, quantiles) for x in distribution ]

def generate_random_star(n, R_max=1):
    d_phi = math.pi * 2 / n
    result = []
    for i in range(n):
        r = R_max * np.random.rand()
        result.append((r * math.cos(i * d_phi), r * math.sin(i * d_phi)))
    return result

def generate_random_parabola(n, a=1, b=0, c=0):
    X_MIN = -3
    X_MAX = 3
    DEV_MIN = 1
    DEV_MAX = 3

    X = X_MIN + ss.truncnorm.rvs(0, (X_MAX - X_MIN), loc=0, scale=((X_MAX - X_MIN) / 3), size=n)
    f = a * (X ** 2) + b * X + c
    dev = (DEV_MAX - DEV_MIN) * (X - X_MIN) / (X_MAX - X_MIN) + DEV_MIN
    std = dev * ss.norm.rvs(loc=0, scale=1, size=n)
    Y = f + std
    
    return (X, Y)

def __get_loc():
    return np.random.rand() - .5

def __get_scale():
    return 1 + np.random.rand()

def generate_data(n, m=2):
    '''
    Generates random data.

    Keyword arguments:
    n -- the number of data samples
    m -- the number of classes of data samples
    '''
    norm_distribution = ss.norm.rvs(loc=__get_loc(), scale=__get_scale(), size=n)
    beta_scale = __get_scale()
    uniform_scale = __get_scale()
    random_star = generate_random_star(n)
    random_parabola = generate_random_parabola(n)
    return {
        'A' : norm_distribution,
        'B' : ss.laplace.rvs(loc=__get_loc(), scale=__get_scale(), size=n),
        'C' : ss.uniform.rvs(loc=__get_loc() - 3 * uniform_scale, scale=6 * uniform_scale, size=n),
        'D' : ss.expon.rvs(loc=__get_loc(), scale=__get_scale(), size=n),
        'E' : ss.beta.rvs(a=.5, b=.5, loc=__get_loc() - 3 * beta_scale, scale=6 * beta_scale, size=n),
        'X' : random_parabola[0],
        'Y' : random_parabola[1],
        'a' : generate_dependent_classes(m, norm_distribution),
        'b' : ss.randint.rvs(0, m, loc=0, size=n),
        'c' : ss.planck.rvs(1, loc=0, size=n),
        'x' : list(zip(*random_star))[0],
        'y' : list(zip(*random_star))[1],
    }