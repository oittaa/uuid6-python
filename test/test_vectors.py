import unittest
from unittest.mock import patch

from uuid6 import UUID, uuid6, uuid7, uuid8


class TestVectors(unittest.TestCase):
    """
    https://datatracker.ietf.org/doc/html/draft-ietf-uuidrev-rfc4122bis#appendix-C
    """

    def test_uuid6_from_int(self):
        uuid_int = (
            0x1EC9414C << 96
            | 0x232A << 80
            | 0xB00 << 64
            | int("11", 2) << 60
            | 0x3C8 << 48
            | 0x9E6BDECED846
        )
        uuid_6 = UUID(int=uuid_int, version=6)
        self.assertEqual(str(uuid_6), "1ec9414c-232a-6b00-b3c8-9e6bdeced846")

    def test_uuid7_from_int(self):
        uuid_int = (
            0x17F22E279B0 << 80
            | 0xCC3 << 64
            | int("01", 2) << 60
            | 0x8C4DC0C0C07398F
        )
        uuid_7 = UUID(int=uuid_int, version=7)
        self.assertEqual(str(uuid_7), "017f22e2-79b0-7cc3-98c4-dc0c0c07398f")

    @patch("uuid6._last_v6_timestamp", 1)
    @patch("secrets.randbits", return_value=0x9E6BDECED846)
    @patch("time.time_ns", return_value=0x16D6320C3D4DCC00)
    def test_uuid6_hex_from_time(self, mocktime, mockrand):
        uuid_6 = uuid6(0x3C8 | int("11", 2) << 12)
        self.assertEqual(str(uuid_6), "1ec9414c-232a-6b00-b3c8-9e6bdeced846")

    @patch("uuid6._last_v7_timestamp", 1)
    @patch("secrets.randbits", return_value=0xCC3 << 64 | 0x1 << 60 | 0x8C4DC0C0C07398F)
    @patch("time.time_ns", return_value=0x17F22E279B0 * 10**6)
    def test_uuid7_hex_from_time(self, mocktime, mockrand):
        uuid_7 = uuid7()
        self.assertEqual(str(uuid_7), "017f22e2-79b0-7cc3-98c4-dc0c0c07398f")

    # The timestamp is Tuesday, February 22, 2022 2:22:22.222222222 PM GMT-05:00
    # represented as 0x16D6320C4A8CA38E or 1645557742222222222
    @patch("uuid6._last_v8_timestamp", 1)
    @patch("secrets.randbits", return_value=0x3FDCBA98765432)
    @patch("time.time_ns", return_value=0x16D6320C4A8CA38E)
    def test_uuid8_hex_from_time(self, mocktime, mockrand):
        uuid_8 = uuid8()
        self.assertEqual(str(uuid_8), "017f22e2-7a8e-838e-8e3f-dcba98765432")

    def test_uuid6_time_from_hex(self):
        uuid_6 = UUID(hex="1EC9414C-232A-6B00-B3C8-9E6BDECED846")
        self.assertEqual(uuid_6.time, 138648505420000000)
        uuid_1 = UUID(hex="C232AB00-9414-11EC-B3C8-9E6BDECED846")
        self.assertEqual(uuid_6.time, uuid_1.time)

    def test_uuid7_time_from_hex(self):
        uuid_7 = UUID(hex="017F22E2-79B0-7CC3-98C4-DC0C0C07398F")
        self.assertEqual(uuid_7.time, 1645557742000)

    def test_uuid8_time_from_hex(self):
        uuid_8 = UUID(hex="017F22E2-7A8E-838E-8E3F-DCBA98765432")
        self.assertEqual(uuid_8.time, 1645557742222222222)


if __name__ == "__main__":
    unittest.main()
