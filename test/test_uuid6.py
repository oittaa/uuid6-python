import unittest
from time import time_ns
from unittest.mock import patch
from uuid import uuid1

from uuid6 import DraftUUID, uuid6, uuid7

YEAR_IN_NS = 3600 * 24 * 36525 * 10 ** 7


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
        self.assertEqual(test_uuid.time, 0)
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

    @patch("uuid6._last_v6_timestamp", 1)
    def test_uuid6_far_in_future(self):
        with patch("time.time_ns", return_value=1):
            uuid_prev = uuid6()
        for i in range(1, 3260):
            with patch("time.time_ns", return_value=i * YEAR_IN_NS):
                uuid_cur = uuid6()
                self.assertLess(uuid_prev, uuid_cur)
                uuid_prev = uuid_cur

        # Overflow
        with patch("time.time_ns", return_value=3270 * YEAR_IN_NS):
            uuid_3270y_from_epoch = uuid6()
        self.assertLess(uuid_3270y_from_epoch, uuid_prev)

    @patch("uuid6._last_v7_timestamp", 1)
    def test_uuid7_far_in_future(self):
        with patch("time.time_ns", return_value=1):
            uuid_prev = uuid7()
        for i in range(1, 2170):
            with patch("time.time_ns", return_value=i * YEAR_IN_NS):
                uuid_cur = uuid7()
                self.assertLess(uuid_prev, uuid_cur)
                uuid_prev = uuid_cur

        # Overflow after 2 ** 36 seconds
        with patch("time.time_ns", return_value=2178 * YEAR_IN_NS):
            uuid_2178_from_epoch = uuid7()
        self.assertLess(uuid_2178_from_epoch, uuid_prev)

    def test_time(self):
        uuid_1 = uuid1()
        uuid_6 = uuid6()
        self.assertAlmostEqual(uuid_6.time / 10 ** 7, uuid_1.time / 10 ** 7, 3)
        cur_time = time_ns()
        uuid_7 = uuid7()
        self.assertAlmostEqual(uuid_7.time / 10 ** 9, cur_time / 10 ** 9, 3)


if __name__ == "__main__":
    unittest.main()
