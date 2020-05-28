# QOP
*Make quantum operators native in python*

Behold, the power of qop.

```python
from qop.base import *
from qop.utils import *

assert (2.0 * c1 + c0.D * c0) ** 2 == 4.0 * c1 * c0.D * c0 + c0.D * c0
assert (
        2 / 3* 
        (
            OPS.from_matrix(x_matrix / 2.0, [c0, c1]) ** 2
            + OPS.from_matrix(y_matrix / 2.0, [c0, c1]) ** 2
            + OPS.from_matrix(z_matrix / 2.0, [c0, c1]) ** 2
        )
        == 1 / 2 * OPS.from_matrix(i_matrix, [c0, c1]) - c0.D * c0 * c1.D * c1
    )
assert ((b0*b0.D)**3).E == 1.
assert  Sf("1").D | c1.D*c1 | c1.D | Sf() == 1.0
assert (4.*Sf()+ 3.* Sf("12")).norm() == 5.0
print(((2.+3.*c1*c2.D*c1.D)**2).normal_order())
# 4.0*I + -12.0*c2.D + -12.0*c1.D*c2.D*c1
```

See more examples in tests.
