# uuid6
New time-based UUID formats which are suited for use as a database key.

[![CI](https://github.com/oittaa/uuid6-python/actions/workflows/main.yml/badge.svg)](https://github.com/oittaa/uuid6-python/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/oittaa/uuid6-python/branch/main/graph/badge.svg?token=O59DZ6UWQV)](https://codecov.io/gh/oittaa/uuid6-python)
[![PyPI status](https://badge.fury.io/py/uuid6.svg)](https://pypi.org/project/uuid6/)
[![Python versions supported](https://img.shields.io/pypi/pyversions/uuid6.svg?logo=python)](https://pypi.org/project/uuid6/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This module extends immutable UUID objects (the UUID class) with the functions `uuid6()`, `uuid7()`, and `uuid8()` from [the IETF draft][draft repository].

## Install

```shell
pip install uuid6
```

## Usage

```python
from uuid6 import uuid6, uuid7, uuid8

my_uuid = uuid6()
print(my_uuid)
assert my_uuid < uuid6()

my_uuid = uuid7()
print(my_uuid)
assert my_uuid < uuid7()

my_uuid = uuid8()
print(my_uuid)
assert my_uuid < uuid8()
```

## Which UUID version should I use?

> Implementations SHOULD utilize UUID version 7 over UUID version 1 and 6 if possible.

UUID version 7 features a time-ordered value field derived from the widely implemented and well known Unix Epoch timestamp source, the number of milliseconds seconds since midnight 1 Jan 1970 UTC, leap seconds excluded. As well as improved entropy characteristics over versions 1 or 6.

If your use case requires greater granularity than UUID vesion 7 can provide, you might consider UUID version 8. UUID version 8 doesn't provide as good entropy characteristics as UUID version 7, but it utilizes timestamp with nanosecond level of precision.

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

## UUIDv8 Field and Bit Layout

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
- `ver`: The 4 bit UUIDv8 version (1000)
- `subsec_a`: 12 bits allocated to sub-second precision values
- `var`: 2 bit UUID variant (10)
- `subsec_b`: 8 bits allocated to sub-second precision values
- `rand`: The remaining 54 bits are filled with [cryptographically strong random data][python randbits]

 20 extra bits dedicated to sub-second precision provide nanosecond resolution. The `unix_ts_ms`, `subsec_a`,  and `subsec_b` fields guarantee the order of UUIDs generated within the same nanosecond by monotonically incrementing the timer.

## Performance

Run the shell script [bench.sh][bench] to test on your own machine.

### Results

MacBook Air 2020
```
Python 3.10.4
Mean +- std dev: 870 ns +- 11 ns
Mean +- std dev: 1.17 us +- 0.01 us
Mean +- std dev: 2.18 us +- 0.02 us
Mean +- std dev: 1.60 us +- 0.02 us
Mean +- std dev: 1.78 us +- 0.02 us
+-----------+--------+-----------------------+-----------------------+-----------------------+-----------------------+
| Benchmark | uuid1  | uuid4                 | uuid6                 | uuid7                 | uuid8                 |
+===========+========+=======================+=======================+=======================+=======================+
| timeit    | 870 ns | 1.17 us: 1.35x slower | 2.18 us: 2.51x slower | 1.60 us: 1.84x slower | 1.78 us: 2.04x slower |
+-----------+--------+-----------------------+-----------------------+-----------------------+-----------------------+
```

[draft repository]: https://github.com/ietf-wg-uuidrev/rfc4122bis
[python randbits]: https://docs.python.org/3/library/secrets.html#secrets.randbits
[bench]: https://github.com/oittaa/uuid6-python/blob/main/bench.sh
