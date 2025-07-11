import numpy as np
from scipy.stats import kendalltau
from scipy.stats import entropy

def kl_divergence(distrib1, distrib2, epsilon=1e-10):
    """
    KL divergence between 0 and + infinity
    """
    dict1 = dict(distrib1)
    dict2 = dict(distrib2)

    all_keys = set(dict1) | set(dict2)

    p = np.array([dict1.get(k, 0) for k in all_keys], dtype=float)
    q = np.array([dict2.get(k, 0) for k in all_keys], dtype=float)

    # Add smoothing to avoid zeros
    p += epsilon
    q += epsilon

    p /= p.sum()
    q /= q.sum()

    return entropy(p, q)

def mse(distrib1, distrib2):
    """
    Mean square error from 0 and + infinity
    """
    dict1 = dict(distrib1)
    dict2 = dict(distrib2)

    all_keys = set(dict1) | set(dict2)

    p = np.array([dict1.get(k, 0) for k in all_keys], dtype=float)
    q = np.array([dict2.get(k, 0) for k in all_keys], dtype=float)

    return np.mean((p - q) ** 2)

def rmse(distrib1, distrib2):
    """
    Square root mean square error from 0 to + infinity
    """
    return np.sqrt(mse(distrib1, distrib2))

def kendall_rank_correlation(distrib1, distrib2):
    """
    Return the value between -1 and 1
    """
    dict1 = dict(distrib1)
    dict2 = dict(distrib2)

    all_keys = sorted(set(dict1) | set(dict2))  # Sort for consistent ordering

    p = np.array([dict1.get(k, 0) for k in all_keys], dtype=float)
    q = np.array([dict2.get(k, 0) for k in all_keys], dtype=float)

    tau, _ = kendalltau(p, q)
    return tau

