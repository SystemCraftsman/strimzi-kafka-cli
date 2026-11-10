from unittest import TestCase

from kfk.utils import convert_string_to_type, parse_kv_string


class TestConvertStringToType(TestCase):
    def test_positive_int(self):
        self.assertEqual(convert_string_to_type("42"), 42)
        self.assertIsInstance(convert_string_to_type("42"), int)

    def test_negative_int(self):
        self.assertEqual(convert_string_to_type("-5"), -5)
        self.assertIsInstance(convert_string_to_type("-5"), int)

    def test_negative_one_stays_int(self):
        # e.g. Kafka configs like retention.ms=-1 must not become -1.0
        self.assertEqual(convert_string_to_type("-1"), -1)
        self.assertIsInstance(convert_string_to_type("-1"), int)

    def test_float(self):
        self.assertEqual(convert_string_to_type("1.5"), 1.5)

    def test_bool(self):
        self.assertIs(convert_string_to_type("true"), True)
        self.assertIs(convert_string_to_type("false"), False)

    def test_string(self):
        self.assertEqual(convert_string_to_type("foo"), "foo")

    def test_parse_kv_string_negative_int(self):
        self.assertEqual(
            parse_kv_string("retention.ms=-1,foo=bar"),
            {"retention.ms": -1, "foo": "bar"},
        )
        self.assertIsInstance(
            parse_kv_string("retention.ms=-1")["retention.ms"], int
        )
