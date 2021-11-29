# uuid6
New time-based UUID formats which are suited for use as a database key.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This module extends immutable UUID objects (the UUID class) with the functions `uuid6()` and `uuid7()` from [the IETF draft](https://github.com/uuid6/uuid6-ietf-draft).

## Install

```shell
pip install uuid6
```

## Usage

```python
from uuid6 import uuid6, uuid7

my_uuid = uuid6()
print(my_uuid)
assert my_uuid < uuid6()

my_uuid = uuid7()
print(my_uuid)
assert my_uuid < uuid7()
```
