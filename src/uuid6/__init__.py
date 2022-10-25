r"""UUID draft version objects (universally unique identifiers).
This module provides the functions uuid6(), uuid7(), and uuid8() for
generating version 6, 7, and 8 UUIDs as specified in
https://github.com/ietf-wg-uuidrev/rfc4122bis
"""

import secrets
import time
import uuid
from typing import Tuple


class UUID(uuid.UUID):
    r"""UUID draft version objects"""

    def __init__(
        self,
        hex: str = None,
        bytes: bytes = None,
        bytes_le: bytes = None,
        fields: Tuple[int, int, int, int, int, int] = None,
        int: int = None,
        version: int = None,
        *,
        is_safe=uuid.SafeUUID.unknown
    ) -> None:
        r"""Create a UUID."""

        if int is None or [hex, bytes, bytes_le, fields].count(None) != 4:
            return super().__init__(
                hex=hex,
                bytes=bytes,
                bytes_le=bytes_le,
                fields=fields,
                int=int,
                version=version,
                is_safe=is_safe,
            )
        if not 0 <= int < 1 << 128:
            raise ValueError("int is out of range (need a 128-bit value)")
        if version is not None:
            if not 6 <= version <= 8:
                raise ValueError("illegal version number")
            # Set the variant to RFC 4122.
            int &= ~(0xC000 << 48)
            int |= 0x8000 << 48
            # Set the version number.
            int &= ~(0xF000 << 64)
            int |= version << 76
        super().__init__(int=int, is_safe=is_safe)

    @property
    def subsec(self) -> int:
        return ((self.int >> 64) & 0x0FFF) << 8 | ((self.int >> 54) & 0xFF)

    @property
    def time(self) -> int:
        if self.version == 6:
            return (
                (self.time_low << 28)
                | (self.time_mid << 12)
                | (self.time_hi_version & 0x0FFF)
            )
        if self.version == 7:
            return self.int >> 80
        if self.version == 8:
            return (self.int >> 80) * 10**6 + _subsec_decode(self.subsec)
        return super().time


def _subsec_decode(value: int) -> int:
    return -(-value * 10**6 // 2**20)


def _subsec_encode(value: int) -> int:
    return value * 2**20 // 10**6


_last_v6_timestamp = None
_last_v7_timestamp = None
_last_v8_timestamp = None


def uuid6(clock_seq: int = None) -> UUID:
    r"""UUID version 6 is a field-compatible version of UUIDv1, reordered for
    improved DB locality. It is expected that UUIDv6 will primarily be
    used in contexts where there are existing v1 UUIDs. Systems that do
    not involve legacy UUIDv1 SHOULD consider using UUIDv7 instead.

    If 'clock_seq' is given, it is used as the sequence number;
    otherwise a random 14-bit sequence number is chosen."""

    global _last_v6_timestamp

    nanoseconds = time.time_ns()
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds // 100 + 0x01B21DD213814000
    if _last_v6_timestamp is not None and timestamp <= _last_v6_timestamp:
        timestamp = _last_v6_timestamp + 1
    _last_v6_timestamp = timestamp
    if clock_seq is None:
        clock_seq = secrets.randbits(14)  # instead of stable storage
    time_high_and_time_mid = (timestamp >> 12) & 0xFFFFFFFFFFFF
    time_low_and_version = timestamp & 0x0FFF
    uuid_int = time_high_and_time_mid << 80
    uuid_int |= time_low_and_version << 64
    uuid_int |= (clock_seq & 0x3FFF) << 48
    uuid_int |= secrets.randbits(48)
    return UUID(int=uuid_int, version=6)


def uuid7() -> UUID:
    r"""UUID version 7 features a time-ordered value field derived from the
    widely implemented and well known Unix Epoch timestamp source, the
    number of milliseconds seconds since midnight 1 Jan 1970 UTC, leap
    seconds excluded. As well as improved entropy characteristics over
    versions 1 or 6.

    Implementations SHOULD utilize UUID version 7 over UUID version 1 and
    6 if possible."""

    global _last_v7_timestamp

    nanoseconds = time.time_ns()
    timestamp_ms, _ = divmod(nanoseconds, 10**6)
    if _last_v7_timestamp is not None and timestamp_ms <= _last_v7_timestamp:
        timestamp_ms = _last_v7_timestamp + 1
    _last_v7_timestamp = timestamp_ms
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= secrets.randbits(76)
    return UUID(int=uuid_int, version=7)


def uuid8() -> UUID:
    r"""UUID version 8 features a time-ordered value field derived from the
    widely implemented and well known Unix Epoch timestamp source, the
    number of nanoseconds seconds since midnight 1 Jan 1970 UTC, leap
    seconds excluded."""

    global _last_v8_timestamp

    nanoseconds = time.time_ns()
    if _last_v8_timestamp is not None and nanoseconds <= _last_v8_timestamp:
        nanoseconds = _last_v8_timestamp + 1
    _last_v8_timestamp = nanoseconds
    timestamp_ms, timestamp_ns = divmod(nanoseconds, 10**6)
    subsec = _subsec_encode(timestamp_ns)
    subsec_a = subsec >> 8
    subsec_b = subsec & 0xFF
    uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= subsec_a << 64
    uuid_int |= subsec_b << 54
    uuid_int |= secrets.randbits(54)
    return UUID(int=uuid_int, version=8)
