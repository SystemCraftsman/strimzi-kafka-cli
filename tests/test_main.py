import shutil

from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.config import BASE_PATH


class TestKfkMain(TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test(self):
        shutil.rmtree(BASE_PATH, ignore_errors=True)
        from kfk.main import kfk
        result = self.runner.invoke(kfk)
        assert result.exit_code == 0
