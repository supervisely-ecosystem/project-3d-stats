import numpy as np


def get_agg_stats(array, round_value, agg="mean"):
    if not len(array):
        return "-"
    np_array = np.array(array)
    if np_array.dtype == np.int64:
        np_array = np_array.astype(np.int32)
    if len(np_array.shape) == 1:
        axis = None
    elif len(np_array.shape) == 2:
        axis = 0
    if agg == "mean":
        np_array = np_array.mean(axis)
    elif agg == "min":
        np_array = np_array.min(axis)
    elif agg == "max":
        np_array = np_array.max(axis)
    elif agg == "std":
        np_array = np_array.std(axis)
    elif agg == "sum":
        np_array = np_array.sum(axis)
    if isinstance(np_array, np.ndarray):
        np_array = [round(val, round_value) for val in np_array]
    else:
        np_array = round(np_array, round_value)
    return np_array
