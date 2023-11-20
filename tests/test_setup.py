import os
import tempfile
from unittest import TestCase, mock

from click.testing import CliRunner

from src.kfk.config import KUBECTL, STRIMZI_VERSION
from src.kfk.setup import prepare_resources


class TestSetup(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.KUBECTL_PATH", tempfile.mkdtemp() + "/" + KUBECTL)
    @mock.patch("src.kfk.setup._download_kubectl")
    def test_main(self, mock_download_kubectl, mock_rename):
        prepare_resources()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.KUBECTL_PATH", tempfile.mkdtemp() + "/" + KUBECTL)
    @mock.patch("src.kfk.setup._download_kubectl")
    def test_download_kubectl_if_not_exists(self, mock_download_kubectl, mock_rename):
        prepare_resources()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("src.kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists(
        self, mock_download_kubectl, mock_rename
    ):
        prepare_resources()
        assert mock_download_kubectl.call_count == 1

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("src.kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists_with_custom_kubectl_path(
        self, mock_download_kubectl, mock_rename
    ):
        os.environ["STRIMZI_KAFKA_CLI_KUBECTL_PATH"] = tempfile.mkdtemp()
        prepare_resources()
        assert mock_download_kubectl.call_count == 0

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.KUBECTL_VERSION", "x.x.x")
    @mock.patch("src.kfk.setup._download_kubectl")
    def test_update_kubectl_if_new_version_exists_with_custom_kubectl_version(
        self, mock_download_kubectl, mock_rename
    ):
        os.environ["STRIMZI_KAFKA_CLI_KUBECTL_VERSION"] = "x.x.y"
        prepare_resources()
        assert mock_download_kubectl.call_count == 0

    @mock.patch("src.kfk.setup.os.rename")
    @mock.patch("src.kfk.setup.os.remove")
    @mock.patch("src.kfk.setup.tarfile")
    @mock.patch("src.kfk.setup.print")
    @mock.patch("src.kfk.setup.wget.download")
    @mock.patch("src.kfk.setup.STRIMZI_PATH", tempfile.mkdtemp() + "/strimzi-x.x.x")
    def test_download_strimzi_if_not_exists(
        self, mock_wget_download, mock_print, mock_tarfile, mock_remove, mock_rename
    ):
        prepare_resources()
        mock_print.assert_called_with(
            "Extracting Strimzi {version}...\n".format(version=STRIMZI_VERSION)
        )
