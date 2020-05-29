# QOP

*Make quantum operators and algebras native in python*

Behold, the power of qop.

* Boson

```python
from qop.boson import *
assert (b0.D*b0)**3 == b0.D*b0+3*b0.D**2*b0**2+b0.D**3*b0**3
```

* Fermion

```python
from qop.fermion import *
assert (c0.D*c0)**3 == c0.D*c0
```

* Hardcore Boson

```python
from qop.hardcoreboson import *
assert (hb0.D*hb0)**2 ==hb0.D*hb0
assert hb0*hb1 == hb1*hb0
```

* Spin

```python
from qop.spin import *
assert s0.x*s0.y == 1j/2*s0.z
assert s0.z*s1.x == -2j*s1.x*s0.x*s0.y
```

* Grassmann numbers

```python
from qop.grassmann import *
assert (1+g(0)*g(1))**2 == 1+2*g(0)*g(1)
```

* Quaternion numbers

```python
from qop.quaternion import *
assert (1-qi)/(1-qj) == 0.5*(1-qi+qj-qk)
```

* Symbols

```python
from qop.symbol import *
a = Symbol("a")
assert np.conj((2+a)).evaluate({"a": 1j}) == 2-1j
```

* Quantum states

```python
from qop.fermion import *
from qop.state import *
assert Sf("1").D | c1.D * c1 | c1.D | Sf() == 1.0
```

And mix all, we have

```python
U = Symbol("U")
assert Sf("12").D | U * (np.array([c1.D, c2.D]) @ np.array([c1, c2])) ** 2 | Sf("12") == 4 * U
```

See more examples in tests.
