from functools import total_ordering
import numpy as np


def assert_num(c):
    """
    assert c is a c-number

    :param c:
    :return: Union[float, complex]
    :raises ValueError: if c is not int/float/complex
    """
    if isinstance(c, int):
        return float(c)
    if isinstance(c, float) or isinstance(c, complex):
        return c
    raise ValueError("Only float/complex number is supported in this operation.")


def is_num(c):
    """
    whether c is a c-number

    :param c:
    :return: bool
    """
    if isinstance(c, int) or isinstance(c, float) or isinstance(c, complex):
        return True
    return False


@total_ordering
class Operator:
    """
    operator is the generator and minimal ingredients of some algebra
    """

    _exists = {}

    def __new__(cls, *args, name="OP", repr_=None):
        key = (tuple(args), name)
        if key in cls._exists:
            return cls._exists[key]
        op = super().__new__(cls)
        if len(args) == 0:
            op.label = (-1,)
        else:
            op.label = tuple(args)
        op.key = key
        op.name = name
        op.repr = repr_
        cls._exists[key] = op
        return op

    def __repr__(self):
        if self.repr is not None:
            return self.repr(self)
        if self.label[0] == -1:
            return "I"
        return self.name + str(self.label)

    __str__ = __repr__

    def simplify(self):
        return self

    def strfy(self):
        return OperatorString.from_op(self)

    def __add__(self, other):
        lops = self.strfy()
        return lops + other

    def __sub__(self, other):
        lops = self.strfy()
        return lops - other

    def __mul__(self, other):
        lops = self.strfy()
        return lops * other

    def __rmul__(self, other):
        lops = self.strfy()
        return lops.__rmul__(other)

    def __truediv__(self, other):
        ops = self.strfy()
        return ops / other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return -1 * self.__sub__(other)

    def __pow__(self, n):
        ops = self.strfy()
        return ops ** n

    def __pos__(self):
        ops = self.strfy()
        return ops

    def __neg__(self):
        ops = self.strfy()
        return -1.0 * ops

    def __eq__(self, other):  # break hashable
        if isinstance(other, Operator):
            if self.label[0] == -1 and other.label[0] == -1:
                return True  # 1.D = 1
            return self.key == other.key
        else:  # other is ops
            return other.__eq__(self)

    def __lt__(self, other):
        return self.label < other.label

    def __hash__(self):
        return hash(self.key)

    def evaluate(self, param_dict):
        ops = self.strfy()
        return ops.evaluate(param_dict)


class OperatorString:
    """
    OPS is some formula with operators, such as 3*op1*op2+2*op3+5
    """

    def __init__(self, ops=None, coeff=None):
        self.opdict = {}
        if not ops:
            pass
            # empty instance, need hand crafted
        else:
            if not coeff:
                coeff = [1.0] * len(ops)
            for i, oplist in enumerate(ops):
                self.opdict[tuple(oplist)] = (
                    self.opdict.get(tuple(oplist), 0) + coeff[i]
                )
            self.OP = type(ops[0][0])

    @classmethod
    def from_op(cls, op, coeff=None):
        return cls([[op]], coeff=coeff)

    @classmethod
    def from_opdict(cls, opdict):
        _instance = cls()
        _instance.opdict = opdict
        for k, v in opdict.items():
            _instance.OP = type(k[0])
            break
        return _instance

    def __repr__(self):
        s = ""
        for i, oplist in enumerate(self.opdict):
            s += str(self.opdict[oplist]) + "*"
            for op in oplist:
                s += op.__repr__() + "*"
            s = s[:-1] + " + "
        return s[:-3]

    __str__ = __repr__

    def __add__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):
            other = other.strfy()
        if isinstance(other, np.ndarray):
            return other.__add__(self)
        newdict = self.opdict.copy()
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) + v
        if type(self) == type(other):
            return type(self).from_opdict(newdict)
        else:
            return MultipleOperatorString.from_opdict(newdict)

    def __sub__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):
            other = other.strfy()
        if isinstance(other, np.ndarray):
            return (-other).__add__(self)
        newdict = self.opdict.copy()
        for k, v in other.opdict.items():
            newdict[k] = newdict.get(k, 0.0) - v
        if type(self) == type(other):
            return type(self).from_opdict(newdict)
        else:
            return MultipleOperatorString.from_opdict(newdict)

    def __rsub__(self, other):
        return -1.0 * self + other

    def __mul__(self, other):
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        if isinstance(other, Operator):  # sometimes fail working
            other = other.strfy()
        if isinstance(other, np.ndarray):
            return other.__rmul__(self)
        newdict = {}
        for k1, v1 in self.opdict.items():
            for k2, v2 in other.opdict.items():
                newdict[tuple(list(k1) + list(k2))] = v1 * v2
        if type(self) == type(other):
            return type(self).from_opdict(newdict)
        else:
            return MultipleOperatorString.from_opdict(newdict)

    def __rmul__(self, other):  # multiply by a number
        if is_num(other):
            other = type(self)([[self.OP()]], coeff=[other])
        return other.__mul__(self)

    def __truediv__(self, other):
        try:
            other = assert_num(other)
            return 1 / other * self
        except ValueError:
            return other.__rtruediv__(self)

    def __pow__(self, n):
        assert isinstance(n, int)
        assert n >= 0
        if n == 0:
            return type(self)([[self.OP()]])
        nops = self
        if n == 1:
            return nops
        return nops * nops ** (n - 1)

    def __radd__(self, other):
        return self.__add__(other)

    def __pos__(self):
        return self

    def __neg__(self):
        return -1.0 * self

    def __eq__(self, other):
        self.simplify()
        opdict1 = self.opdict
        if is_num(other):
            other = other * self.OP()
        if isinstance(other, Operator):
            other = other.strfy()
        # if type(self) != type(other): # MOS can be equal to some pure OS!
        #     return False
        other.simplify()
        opdict2 = other.opdict
        if len(opdict1) != len(opdict2):
            return False
        const = 0
        ## we utilize a relaxed equal relation, all I for different types of operators are the same
        for k2, v2 in opdict2.items():
            if len(list(k2)) == 1 and k2[0].label[0] == -1:
                const = v2
                break
        for k, v in opdict1.items():
            if not np.allclose(opdict2.get(k, 0.0), v):
                if len(list(k)) == 1 and k[0].label[0] == -1 and v == const:
                    continue
                else:
                    return False
        return True

    def simplify(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk, coeff = self.standardize(k)
            if coeff != 0:
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        newdict = {k: v for k, v in newdict.items() if v != 0}
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        self.opdict = newdict
        return self

    def standardize(self, opl):
        if len(opl) == 0:
            return [self.OP()], 1
        if len(opl) == 1:
            return opl, 1
        nk = []
        for op in list(opl):
            if op.label[0] == -1:
                continue
            nk.append(op)
        if len(nk) == 0:
            nk = [type(opl[0])()]
        return nk, 1

    def evaluate(self, param_dict):  # for compatibility
        return self.simplify()


class MultipleOperatorString(OperatorString):
    """
    MOS mix different types of operators, the common user case is symbol together with particles,
    e.g. 3*a*c1.D
    """

    def __eq__(self, other):
        self.normal_order()
        if getattr(other, "normal_order", False):
            other.normal_order()
        else:
            other.simplify()
        return super().__eq__(other)

    _category_order = [
        "GrassmannOperator",
        "QuaternionOperator",
        "SymbolOperator",
        "BosonOperator",
        "HardcoreBosonOperator",
        "FermionOperator",
        "SpinOperator",
    ]

    @classmethod
    def _get_category_dict(cls, opl):
        category_dict = {}
        for op in list(opl):
            category_dict[type(op).__name__] = category_dict.get(type(op).__name__, [])
            category_dict[type(op).__name__].append(op)
        return category_dict

    def standardize(self, opl):
        category_dict = self._get_category_dict(opl)
        nk = []
        sign = 1
        for c in self._category_order:
            if category_dict.get(c, False):
                nopl, coeff = category_dict[c][0].strfy().standardize(category_dict[c])
                if coeff != 0 and nopl[0].label[0] != -1:  # get rid of excess I
                    nk.extend(nopl)
                    sign *= coeff
                elif coeff == 0:
                    return None, 0
        if len(nk) == 0:
            nk = [self.OP()]
        return nk, sign

    def evaluate(self, param_dict):
        newdict = {}
        for k, v in self.opdict.items():
            nk, coeff = self.evaluate_basis(list(k), param_dict)
            if coeff != 0:
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        newdict = {k: v for k, v in newdict.items() if v != 0}
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        return type(self).from_opdict(newdict).simplify()

    def evaluate_basis(self, opl, param_dict):
        category_dict = self._get_category_dict(opl)
        if "SymbolOperator" not in category_dict:
            return opl, 1
        nk, coeff = (
            category_dict["SymbolOperator"][0]
            .strfy()
            .evaluate_basis(category_dict["SymbolOperator"], param_dict)
        )
        for c in self._category_order:
            if category_dict.get(c, False) and not c.startswith("Symbol"):
                nk.extend(category_dict[c])
        return nk, coeff

    def normal_order(self):
        self.simplify()
        h = []
        for i, k in enumerate(self.opdict):
            h.append(type(list(k)[0])())
            h[i] *= self.opdict[k]
            category_dict = self._get_category_dict(k)
            for c in self._category_order:
                if category_dict.get(c, False) and c in [
                    "BosonOperator",
                    "HardcoreBosonOperator",
                    "FermionOperator",
                ]:
                    h[i] *= type(category_dict[c][0].strfy())(
                        [category_dict[c]]
                    ).normal_order()
                elif category_dict.get(c, False):
                    h[i] *= type(category_dict[c][0].strfy())([category_dict[c]])
        return np.sum(h).simplify()

    def to_hb(self):
        self.simplify()
        h = []
        for i, k in enumerate(self.opdict):
            h.append(type(list(k)[0])())
            h[i] *= self.opdict[k]
            category_dict = self._get_category_dict(k)
            for c in self._category_order:
                if category_dict.get(c, False) and c in ["SpinOperator"]:
                    h[i] *= type(category_dict[c][0].strfy())(
                        [category_dict[c]]
                    ).to_hb()
                elif category_dict.get(c, False):
                    h[i] *= type(category_dict[c][0].strfy())([category_dict[c]])
        return np.sum(h).simplify()

    @property
    def E(self):
        self.simplify()
        h = []
        for i, k in enumerate(self.opdict):
            h.append(type(list(k)[0])())
            h[i] *= self.opdict[k]
            category_dict = self._get_category_dict(k)
            for c in self._category_order:
                if category_dict.get(c, False) and c in [
                    "BosonOperator",
                    "HardcoreBosonOperator",
                    "FermionOperator",
                ]:
                    h[i] *= type(category_dict[c][0].strfy())([category_dict[c]]).E
                elif category_dict.get(c, False):
                    h[i] *= type(category_dict[c][0].strfy())([category_dict[c]])
        result = np.sum(h).simplify()
        if len(result.opdict) == 1:
            for k, v in result.opdict.items():
                if len(list(k)) == 1 and k[0].label[0] == -1:
                    return v

        return result


@np.vectorize
def simplify(ops):
    return ops.simplify()


@np.vectorize
def normal_order(ops):
    return ops.normal_order()


@np.vectorize
def evaluate(ops, param_dict):
    return ops.evaluate(param_dict)


@np.vectorize
def evaluate_all(ops, param_dict):
    return ops.evaluate_all(param_dict)
