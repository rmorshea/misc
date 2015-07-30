# misc

## Overview

This is a collection of miscellaneous, single-file Python modules.

## Installation

These modules are designed to be installed through [`antipackage`](https://github.com/rmorshea/antipackage).
You can install it using `pip`:

```
pip install git+https://github.com/rmorshea/antipackage.git#egg=antipackage
```

Once you do this, simply import `antipackage`:

```
import antipackage
```

Once `antipackage` has been imported, you can use any of the modules in this repo by importing
it using the following syntax:

```
from github.rmorshea.misc import numberic
```

This will automatically download and install the `numbers` module and import it. `antipackage` will
automatically update any of these modules the next time you import them.
