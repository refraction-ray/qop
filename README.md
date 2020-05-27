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
```
