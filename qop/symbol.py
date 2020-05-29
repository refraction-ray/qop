import numpy as np
from . import base


class Symbol(base.Operator):
    """
    only works as representation for complex numbers (Abelian baked in) not other operators
    """

    _exists = {}
    count = -2

    def __new__(cls, arg="I", dagger=False):
        key = (arg, dagger)
        if key in cls._exists:
            return cls._exists[key]
        Symbol.count += 1
        op = object.__new__(cls)
        op.label = (Symbol.count, arg, dagger)  # (, symbol_name, dagger)
        op.d = dagger
        op.key = key
        op.name = arg
        cls._exists[key] = op
        return op

    def strfy(self):
        return SymbolString.from_op(self)

    def conjugate(self):
        if self.label[0] == -1:
            return self
        dagger = False if self.d else True
        return type(self)(*self.label[1], dagger=dagger)

    @property
    def D(self):
        return self.conjugate()

    def __repr__(self):
        return self.name + (".D" if self.d else "")

    __str__ = __repr__

    def __lt__(self, other):
        return self.label < other.label

    def evaluate(self, param_dict):
        ops = self.strfy()
        return ops.evaluate(param_dict)

    def evaluate_all(self, param_dict):
        ops = self.strfy()
        return ops.evaluate_all(param_dict)


Symbol()  # occupy the -1 count


class SymbolString(base.OperatorString):
    def conjugate(self):
        newdict = {}
        for k, v in self.opdict.items():
            nk = tuple([op.D for op in list(k)])
            newdict[nk] = newdict.get(nk, 0.0) + np.conj(v)
        self.opdict = newdict
        return self

    @property
    def D(self):
        return self.conjugate()

    def standardize(self, opl):
        nk, coeff = super().standardize(opl)
        return sorted(nk), coeff

    def evaluate(self, param_dict):
        self.simplify()
        newdict = {}
        for k, v in self.opdict.items():
            nk, coeff = self.evaluate_basis(list(k), param_dict)
            if coeff != 0:
                newdict[tuple(nk)] = newdict.get(tuple(nk), 0) + coeff * v
        newdict = {k: v for k, v in newdict.items() if v != 0}
        if len(newdict) == 0:
            newdict[tuple([self.OP()])] = 0.0
        return type(self).from_opdict(newdict)

    def evaluate_all(self, param_dict):
        ops = self.evaluate(param_dict)
        assert len(ops.opdict) == 1
        assert ops.opdict.get((Symbol(),), False)
        return ops.opdict.get((Symbol(),), 0)

    def evaluate_basis(self, opl, param_dict):
        assert "I" not in param_dict
        nk = []
        coeff = 1
        for op in opl:
            if op.name in param_dict:
                if op.d is True:
                    coeff *= np.conj(param_dict[op.name])
                else:
                    coeff *= param_dict[op.name]
            else:
                nk.append(op)
        if len(nk) == 0:
            nk = [Symbol()]
        return nk, coeff


@np.vectorize
def evaluate(ops, param_dict):
    return ops.evaluate(param_dict)


@np.vectorize
def evaluate_all(ops, param_dict):
    return ops.evaluate_all(param_dict)
