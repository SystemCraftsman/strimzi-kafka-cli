from unittest import TestCase, mock
from click.testing import CliRunner
from kfk_users import kfk
from kubectl_command_builder import Kubectl


class TestKfkClusters(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.user = "my-user"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['users', '--user', self.user, '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk users" in result.output

    @mock.patch('kfk_users.os')
    def test_list_users(self, mock_os):
        result = self.runner.invoke(kfk, ['users', '--list', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkausers().label("strimzi.io/cluster={cluster}").namespace(self.namespace).build().format(
                cluster=self.cluster))

    @mock.patch('kfk_users.user_exists')
    @mock.patch('kfk_users.os')
    def test_describe_users(self, mock_os, mock_user_exists):
        result = self.runner.invoke(kfk, ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                          self.namespace])
        assert result.exit_code == 0
        mock_user_exists.return_value = True
        mock_os.system.assert_called_with(Kubectl().describe().kafkausers(self.user).namespace(self.namespace).build())

    @mock.patch('kfk_users.user_exists')
    @mock.patch('kfk_users.os')
    def test_describe_clusters_output_yaml(self, mock_os, mock_user_exists):
        result = self.runner.invoke(kfk,
                                    ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace, '-o',
                                     'yaml'])
        assert result.exit_code == 0
        mock_user_exists.return_value = True
        mock_os.system.assert_called_with(
            Kubectl().get().kafkausers(self.user).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk_users.os')
    def test_create_users(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'tls', '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        with open(r'yaml/user_create.yaml') as file:
            user_yaml = file.read()
            mock_os.system.assert_called_with(
                'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().create().from_file("-").namespace(
                    self.namespace).build())

    def test_create_users_with_wrong_auth_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'auth', '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    def test_create_users_without_auth_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    @mock.patch('kfk_users.user_exists')
    @mock.patch('kfk_users.os')
    def test_delete_users(self, mock_os, mock_user_exists):
        result = self.runner.invoke(kfk,
                                    ['users', '--delete', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        mock_user_exists.return_value = True
        mock_os.system.assert_called_with(Kubectl().delete().kafkausers(self.user).namespace(self.namespace).build())
