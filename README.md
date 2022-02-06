# uuid6
New time-based UUID formats which are suited for use as a database key.

[![CI](https://github.com/oittaa/uuid6-python/actions/workflows/main.yml/badge.svg)](https://github.com/oittaa/uuid6-python/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/oittaa/uuid6-python/branch/main/graph/badge.svg?token=O59DZ6UWQV)](https://codecov.io/gh/oittaa/uuid6-python)
[![PyPI status](https://badge.fury.io/py/uuid6.svg)](https://pypi.org/project/uuid6/)
[![Python versions supported](https://img.shields.io/pypi/pyversions/uuid6.svg?logo=python)](https://pypi.org/project/uuid6/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This module extends immutable UUID objects (the UUID class) with the functions `uuid6()` and `uuid7()` from [the IETF draft][ietf draft].

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

## UUIDv6 Field and Bit Layout

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                           time_high                           |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |           time_mid            |      time_low_and_version     |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |clk_seq_hi_res |  clk_seq_low  |         node (0-1)            |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         node (2-5)                            |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

## UUIDv7 Field and Bit Layout

### [Draft 02][draft 02]

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                            unixts                             |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |unixts |       subsec_a        |  ver  |       subsec_b        |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |var|                   subsec_seq_node                         |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                       subsec_seq_node                         |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### This implementation

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                            unixts                             |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |unixts |       subsec_a        |  ver  |       subsec_b        |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |var| subsec_c  |             rand                              |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                             rand                              |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- `unixts`: 36 bit big-endian unsigned Unix Timestamp value
- `subsec_a`: 12 bits allocated to sub-second precision values
- `ver`: The 4 bit UUIDv7 version (0111)
- `subsec_b`: 12 bits allocated to sub-second precision values
- `var`: 2 bit UUID variant (10)
- `subsec_c`: 6 bits allocated to sub-second precision values
- `rand`: The remaining 56 bits are filled with pseudo-random data

 30 bits dedicated to sub-second precision provide nanosecond resolution. The `unixts` and `subsec` fields guarantee the order of UUIDs generated within the same nanosecond by monotonically incrementing the timer.

This implementation does not include a clock sequence counter as defined in the draft RFC.

## Performance

Run the included shell script `./bench.sh` to test on your own machine.

MacBook Air
```
Python 3.10.2
Mean +- std dev: 1.02 us +- 0.01 us
Mean +- std dev: 1.11 us +- 0.01 us
Mean +- std dev: 2.34 us +- 0.02 us
Mean +- std dev: 2.04 us +- 0.02 us
+-----------+---------+-----------------------+-----------------------+-----------------------+
| Benchmark | uuid1   | uuid4                 | uuid6                 | uuid7                 |
+===========+=========+=======================+=======================+=======================+
| timeit    | 1.02 us | 1.11 us: 1.08x slower | 2.34 us: 2.28x slower | 2.04 us: 1.99x slower |
+-----------+---------+-----------------------+-----------------------+-----------------------+
```

Google [Cloud Shell][cloud shell] VM
```
Python 3.7.3
Mean +- std dev: 10.1 us +- 0.7 us
Mean +- std dev: 4.25 us +- 0.79 us
Mean +- std dev: 9.37 us +- 1.75 us
Mean +- std dev: 7.51 us +- 1.42 us
+-----------+---------+-----------------------+-----------------------+-----------------------+
| Benchmark | uuid1   | uuid4                 | uuid6                 | uuid7                 |
+===========+=========+=======================+=======================+=======================+
| timeit    | 10.1 us | 4.25 us: 2.38x faster | 9.37 us: 1.08x faster | 7.51 us: 1.35x faster |
+-----------+---------+-----------------------+-----------------------+-----------------------+
```

[ietf draft]: https://github.com/uuid6/uuid6-ietf-draft
[draft 02]: https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format-02#section-4.4
[cloud shell]: https://cloud.google.com/shell/docs
