from ..utils import convert_string_to_type
from unittest import TestCase


class TestUtils(TestCase):
    def test_convert_string_to_int(self):
        val_str = "12"
        self.assertEqual(convert_string_to_type(val_str), 12)

    def test_convert_string_to_float(self):
        val_str = "12.5"
        self.assertEqual(convert_string_to_type(val_str), 12.5)

    def test_convert_string_to_boolean(self):
        val_str = "true"
        self.assertEqual(convert_string_to_type(val_str), True)
        val_str = "false"
        self.assertEqual(convert_string_to_type(val_str), False)

    def test_convert_string_to_str(self):
        val_str = "test"
        self.assertEqual(convert_string_to_type(val_str), "test")
