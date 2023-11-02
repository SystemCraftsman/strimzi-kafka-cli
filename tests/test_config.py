from collections import namedtuple
from unittest import TestCase, mock

from kfk.config import _get_processor_type


def os_uname_mock(p_name_machine):
    OSUname = namedtuple("OSUname", ["machine"])
    return OSUname(machine=p_name_machine)


class TestKfkConfig(TestCase):
    @mock.patch("kfk.config._is_64_bit")
    @mock.patch("kfk.config.platform.uname")
    def test_processor_type_armhf_32bit(self, mock_os_uname, mock_is_64_bit):
        mock_os_uname.return_value = os_uname_mock("armhf")
        mock_is_64_bit.return_value = False
        assert _get_processor_type() == "arm"

    @mock.patch("kfk.config._is_64_bit")
    @mock.patch("kfk.config.platform.uname")
    def test_processor_type_armhf_64bit(self, mock_os_uname, mock_is_64_bit):
        mock_os_uname.return_value = os_uname_mock("armhf")
        mock_is_64_bit.return_value = True
        assert _get_processor_type() == "arm64"

    @mock.patch("kfk.config._is_64_bit")
    @mock.patch("kfk.config.platform.uname")
    def test_processor_type_aarch64_64bit(self, mock_os_uname, mock_is_64_bit):
        mock_os_uname.return_value = os_uname_mock("aarch64")
        mock_is_64_bit.return_value = True
        assert _get_processor_type() == "arm64"

    @mock.patch("kfk.config._is_64_bit")
    @mock.patch("kfk.config.os.uname")
    def test_processor_type_x86_64_64bit(self, mock_os_uname, mock_is_64_bit):
        mock_os_uname.return_value = os_uname_mock("x86_64")
        mock_is_64_bit.return_value = True
        assert _get_processor_type() == "amd64"

    @mock.patch("kfk.config._is_64_bit")
    @mock.patch("kfk.config.os.uname")
    def test_processor_type_x86_32bit(self, mock_os_uname, mock_is_64_bit):
        mock_os_uname.return_value = os_uname_mock("x86")
        mock_is_64_bit.return_value = False
        assert _get_processor_type() == "386"
