import unittest
from time import time_ns
from unittest.mock import patch
from uuid import uuid1

from uuid6 import UUID, uuid6, uuid7, uuid8

REGEX_UUID6 = r"^[0-9a-f]{8}-[0-9a-f]{4}-6[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
REGEX_UUID7 = r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
REGEX_UUID8 = r"^[0-9a-f]{8}-[0-9a-f]{4}-8[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
YEAR_IN_NS = 3600 * 24 * 36525 * 10**7


class UUIDTests(unittest.TestCase):
    def test_uuid6_generation(self):
        uuid6_1 = uuid6()
        self.assertEqual(uuid6_1.version, 6)
        for _ in range(1000):
            self.assertRegex(str(uuid6_1), REGEX_UUID6)
            uuid6_2 = uuid6()
            self.assertLess(uuid6_1, uuid6_2)
            uuid6_1 = uuid6_2

    def test_uuid7_generation(self):
        uuid7_1 = uuid7()
        self.assertEqual(uuid7_1.version, 7)
        for _ in range(1000):
            self.assertRegex(str(uuid7_1), REGEX_UUID7)
            uuid7_2 = uuid7()
            self.assertLess(uuid7_1, uuid7_2)
            uuid7_1 = uuid7_2

    def test_uuid8_generation(self):
        uuid8_1 = uuid8()
        self.assertEqual(uuid8_1.version, 8)
        for _ in range(1000):
            self.assertRegex(str(uuid8_1), REGEX_UUID8)
            uuid8_2 = uuid8()
            self.assertLess(uuid8_1, uuid8_2)
            uuid8_1 = uuid8_2

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            _ = UUID(int=-1)
        with self.assertRaises(ValueError):
            _ = UUID(int=1 << 128)

    def test_valid_int(self):
        test_uuid = UUID(int=0)
        self.assertEqual(test_uuid.version, None)
        self.assertEqual(test_uuid.time, 0)
        test_uuid = UUID(int=(1 << 128) - 1)
        self.assertEqual(test_uuid.version, None)

    def test_invalid_version(self):
        with self.assertRaises(ValueError):
            _ = UUID(int=1, version=420)

    @patch("uuid6._last_v7_timestamp", 1)
    @patch("time.time_ns", return_value=1234)
    def test_uuid7_same_nanosecond(self, mocktime):
        uuid7_1 = uuid7()
        for _ in range(1000):
            uuid7_2 = uuid7()
            self.assertLess(uuid7_1, uuid7_2)
            uuid7_1 = uuid7_2

    @patch("uuid6._last_v8_timestamp", 1)
    @patch("time.time_ns", return_value=1234)
    def test_uuid8_same_nanosecond(self, mocktime):
        uuid8_1 = uuid8()
        for _ in range(1000):
            uuid8_2 = uuid8()
            self.assertLess(uuid8_1, uuid8_2)
            uuid8_1 = uuid8_2

    @patch("uuid6._last_v6_timestamp", 1)
    @patch("secrets.randbits", return_value=678)
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
        for i in range(1, 3260, 10):
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
        for i in range(1, 8000, 10):
            with patch("time.time_ns", return_value=i * YEAR_IN_NS):
                uuid_cur = uuid7()
                self.assertLess(uuid_prev, uuid_cur)
                uuid_prev = uuid_cur

    @patch("uuid6._last_v8_timestamp", 1)
    def test_uuid8_far_in_future(self):
        with patch("time.time_ns", return_value=1):
            uuid_prev = uuid8()
        for i in range(1, 8000, 10):
            with patch("time.time_ns", return_value=i * YEAR_IN_NS):
                uuid_cur = uuid8()
                self.assertLess(uuid_prev, uuid_cur)
                uuid_prev = uuid_cur

    def test_time(self):
        uuid_1 = uuid1()
        uuid_6 = uuid6()
        self.assertAlmostEqual(uuid_6.time / 10**7, uuid_1.time / 10**7, 3)
        cur_time = time_ns()
        uuid_7 = uuid7()
        self.assertAlmostEqual(uuid_7.time / 10**3, cur_time / 10**9, 2)
        uuid_8 = uuid8()
        self.assertAlmostEqual(uuid_8.time / 10**9, cur_time / 10**9, 3)

    def test_zero_time(self):
        uuid_6 = UUID(hex="00000000-0000-6000-8000-000000000000")
        self.assertEqual(uuid_6.time, 0)
        uuid_7 = UUID(hex="00000000-0000-7000-8000-000000000000")
        self.assertEqual(uuid_7.time, 0)
        uuid_8 = UUID(hex="00000000-0000-8000-8000-000000000000")
        self.assertEqual(uuid_8.time, 0)

    def test_max_time(self):
        uuid_6 = UUID(hex="ffffffff-ffff-6fff-bfff-ffffffffffff")
        self.assertEqual(uuid_6.time, 1152921504606846975)
        uuid_7 = UUID(hex="ffffffff-ffff-7fff-bfff-ffffffffffff")
        self.assertEqual(uuid_7.time, 281474976710655)
        uuid_8 = UUID(hex="ffffffff-ffff-8fff-bfff-ffffffffffff")
        self.assertEqual(uuid_8.time, 281474976710656000000)

    def test_multiple_arguments(self):
        with self.assertRaises(TypeError):
            _ = UUID(int=0, hex="061d0edc-bea0-75cc-9892-f6295fd7d295")


if __name__ == "__main__":
    unittest.main()
