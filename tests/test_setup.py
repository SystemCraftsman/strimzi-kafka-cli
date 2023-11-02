import os
import tempfile
from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.config import KUBECTL, STRIMZI_VERSION
from kfk.setup import setup


class TestSetup(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.KUBECTL_PATH", tempfile.mkdtemp() + "/" + KUBECTL)
    @mock.patch("kfk.setup._download_kubectl")
    def test_main(self, mock_download_kubectl, mock_rename):
        setup()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.KUBECTL_PATH", tempfile.mkdtemp() + "/" + KUBECTL)
    @mock.patch("kfk.setup._download_kubectl")
    def test_download_kubectl_if_not_exists(self, mock_download_kubectl, mock_rename):
        setup()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists(
        self, mock_download_kubectl, mock_rename
    ):
        setup()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists_with_custom_kubectl_path(
        self, mock_download_kubectl, mock_rename
    ):
        os.environ["STRIMZI_KAFKA_CLI_KUBECTL_PATH"] = tempfile.mkdtemp()
        setup()
        assert mock_download_kubectl.call_count == 0

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists_with_custom_kubectl_version(
        self, mock_download_kubectl, mock_rename
    ):
        os.environ["STRIMZI_KAFKA_CLI_KUBECTL_VERSION"] = "x.x.y"
        setup()
        assert mock_download_kubectl.call_count == 0

    @mock.patch("kfk.setup.os.rename")
    @mock.patch("kfk.setup.os.remove")
    @mock.patch("kfk.setup.tarfile")
    @mock.patch("kfk.setup.print")
    @mock.patch("kfk.setup.wget.download")
    @mock.patch("kfk.setup.STRIMZI_PATH", tempfile.mkdtemp() + "/strimzi-x.x.x")
    def test_download_strimzi_if_not_exists(
        self, mock_wget_download, mock_print, mock_tarfile, mock_remove, mock_rename
    ):
        setup()
        mock_print.assert_called_with(
            "Extracting Strimzi {version}...\n".format(version=STRIMZI_VERSION)
        )
