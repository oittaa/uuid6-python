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

### [Draft 03][draft 03]

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                           unix_ts_ms                          |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |          unix_ts_ms           |  ver  |       rand_a          |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |var|                        rand_b                             |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                            rand_b                             |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### This implementation

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                           unix_ts_ms                          |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |          unix_ts_ms           |  ver  |      subsec_a         |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |var|   subsec_b    |         rand                              |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                             rand                              |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- `unix_ts_ms`: 48 bit big-endian unsigned number of Unix epoch timestamp with millisecond level of precision
- `ver`: The 4 bit UUIDv7 version (0111)
- `subsec_a`: 12 bits allocated to sub-second precision values
- `var`: 2 bit UUID variant (10)
- `subsec_b`: 8 bits allocated to sub-second precision values
- `rand`: The remaining 54 bits are filled with pseudo-random data

 20 extra bits dedicated to sub-second precision provide nanosecond resolution. The `unix_ts` and `subsec` fields guarantee the order of UUIDs generated within the same nanosecond by monotonically incrementing the timer.

## Performance

Run the shell script [bench.sh][bench] to test on your own machine.

### Results

MacBook Air 2020
```
Python 3.10.2
Mean +- std dev: 1.02 us +- 0.01 us
Mean +- std dev: 1.13 us +- 0.02 us
Mean +- std dev: 2.33 us +- 0.02 us
Mean +- std dev: 1.91 us +- 0.02 us
+-----------+---------+-----------------------+-----------------------+-----------------------+
| Benchmark | uuid1   | uuid4                 | uuid6                 | uuid7                 |
+===========+=========+=======================+=======================+=======================+
| timeit    | 1.02 us | 1.13 us: 1.11x slower | 2.33 us: 2.29x slower | 1.91 us: 1.87x slower |
+-----------+---------+-----------------------+-----------------------+-----------------------+
```

Google [Cloud Shell][cloud shell] VM
```
Python 3.9.2
Mean +- std dev: 12.6 us +- 0.5 us
Mean +- std dev: 3.06 us +- 0.14 us
Mean +- std dev: 6.42 us +- 0.37 us
Mean +- std dev: 4.94 us +- 0.24 us
+-----------+---------+-----------------------+-----------------------+-----------------------+
| Benchmark | uuid1   | uuid4                 | uuid6                 | uuid7                 |
+===========+=========+=======================+=======================+=======================+
| timeit    | 12.6 us | 3.06 us: 4.11x faster | 6.42 us: 1.95x faster | 4.94 us: 2.54x faster |
+-----------+---------+-----------------------+-----------------------+-----------------------+
```

[ietf draft]: https://github.com/uuid6/uuid6-ietf-draft
[draft 03]: https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format-03#section-5.2
[cloud shell]: https://cloud.google.com/shell/docs
[bench]: https://github.com/oittaa/uuid6-python/blob/main/bench.sh
