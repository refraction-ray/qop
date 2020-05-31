import numpy as np
import functools
import operator

try:
    from opt_einsum.backends.dispatch import _cached_funcs

except ImportError:
    _cached_funcs = {}


def py_einsum(eq, *arrays):
    """
    See this issue: https://github.com/dgasmith/opt_einsum/issues/142
    """

    lhs, output = eq.split("->")
    inputs = lhs.split(",")

    sizes = {}
    for term, array in zip(inputs, arrays):
        for k, d in zip(term, array.shape):
            sizes[k] = d

    out_size = tuple(sizes[k] for k in output)
    out = np.empty(out_size, dtype=object)

    inner = [k for k in sizes if k not in output]
    inner_size = [sizes[k] for k in inner]

    for coo_o in np.ndindex(*out_size):

        coord = dict(zip(output, coo_o))

        def gen_inner_sum():
            for coo_i in np.ndindex(*inner_size):
                coord.update(dict(zip(inner, coo_i)))
                locs = [tuple(coord[k] for k in term) for term in inputs]
                elements = (array[loc] for array, loc in zip(arrays, locs))
                yield functools.reduce(operator.mul, elements)

        out[coo_o] = functools.reduce(operator.add, gen_inner_sum())

    return out


_cached_funcs["einsum", "qop"] = py_einsum
_cached_funcs["transpose", "qop"] = np.transpose
_cached_funcs["tensordot", "qop"] = np.tensordot
