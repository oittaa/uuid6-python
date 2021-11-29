import unittest
from unittest.mock import patch

from uuid6 import DraftUUID, uuid6, uuid7


class DraftUUIDTests(unittest.TestCase):
    def test_uuid6_generation(self):
        uuid6_1 = uuid6()
        self.assertEqual(uuid6_1.version, 6)
        for _ in range(1000):
            uuid6_2 = uuid6()
            self.assertLess(uuid6_1, uuid6_2)
            uuid6_1 = uuid6_2

    def test_uuid7_generation(self):
        uuid7_1 = uuid7()
        self.assertEqual(uuid7_1.version, 7)
        for _ in range(1000):
            uuid7_2 = uuid7()
            self.assertLess(uuid7_1, uuid7_2)
            uuid7_1 = uuid7_2

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            _ = DraftUUID(int=-1)
        with self.assertRaises(ValueError):
            _ = DraftUUID(int=1 << 128)

    def test_valid_int(self):
        test_uuid = DraftUUID(int=0)
        self.assertEqual(test_uuid.version, None)
        test_uuid = DraftUUID(int=(1 << 128) - 1)
        self.assertEqual(test_uuid.version, None)

    def test_invalid_version(self):
        with self.assertRaises(ValueError):
            _ = DraftUUID(int=1, version=420)

    @patch("uuid6._last_v7_timestamp", 1)
    @patch("time.time_ns", return_value=1234)
    def test_uuid7_same_nanosecond(self, mocktime):
        uuid7_1 = uuid7()
        for _ in range(10):
            uuid7_2 = uuid7()
            self.assertLess(uuid7_1, uuid7_2)
            self.assertEqual(uuid7_1.int >> 56, (uuid7_2.int >> 56) - 1)
            uuid7_1 = uuid7_2

    @patch("uuid6._last_v6_timestamp", 1)
    @patch("uuid6._getrandbits", return_value=678)
    @patch("time.time_ns", return_value=12345)
    def test_uuid6_fields_without_randomness(self, mocktime, mockrand):
        uuid6_1 = uuid6(clock_seq=123)
        for _ in range(10):
            uuid6_2 = uuid6(clock_seq=123)
            self.assertLess(uuid6_1, uuid6_2)
            self.assertEqual(uuid6_1.fields[0], uuid6_2.fields[0])
            self.assertEqual(uuid6_1.fields[1], uuid6_2.fields[1])
            self.assertEqual(uuid6_1.fields[2], uuid6_2.fields[2] - 1)
            self.assertEqual(uuid6_1.fields[3], uuid6_2.fields[3])
            self.assertEqual(uuid6_1.fields[4], uuid6_2.fields[4])
            self.assertEqual(uuid6_1.fields[5], uuid6_2.fields[5])
            uuid6_1 = uuid6_2


if __name__ == "__main__":
    unittest.main()
