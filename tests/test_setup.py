import tempfile
from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.config import STRIMZI_VERSION
from kfk.setup import setup


class TestSetup(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.STRIMZI_PATH", tempfile.mkdtemp())
    def test_setup_strimzi_exists(self):
        setup()

    @mock.patch("kfk.setup.os.remove")
    @mock.patch("kfk.setup.tarfile")
    @mock.patch("kfk.setup.print")
    @mock.patch("kfk.setup.wget.download")
    @mock.patch("kfk.setup.STRIMZI_PATH", tempfile.mkdtemp() + "/strimzi-x.x.x")
    def test_download_strimzi_if_not_exists(
        self, mock_wget_download, mock_print, mock_tarfile, mock_remove
    ):
        setup()
        mock_print.assert_called_with(
            "Extracting Strimzi {version}...\n".format(version=STRIMZI_VERSION)
        )
