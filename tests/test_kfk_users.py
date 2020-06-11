from unittest import TestCase, mock
from click.testing import CliRunner
from ..kfk_users import kfk
from ..kubectl_command_builder import Kubectl


class TestKfkUsers(TestCase):

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

    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_describe_user(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk, ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                          self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().describe().kafkausers(self.user).namespace(self.namespace).build())

    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_describe_user_output_yaml(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace, '-o',
                                     'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkausers(self.user).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk_users.os')
    def test_create_user(self, mock_os):
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

    def test_create_user_with_wrong_auth_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'auth', '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    def test_create_user_without_auth_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_delete_user(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['users', '--delete', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().delete().kafkausers(self.user).namespace(self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_with_no_params(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_create.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            mock_os.system.assert_called_with(
                'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                    self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_without_quotas(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_create.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/user_alter_without_quotas.yaml') as file:
                user_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_with_quota(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_create.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '--quota', 'requestPercentage=55',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/user_alter_one_quota.yaml') as file:
                user_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_with_two_quotas(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_create.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '--quota', 'requestPercentage=55',
                                         '--quota', 'consumerByteRate=2097152',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/user_alter_two_quotas.yaml') as file:
                user_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_with_two_quotas_delete_one_quota(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_alter_two_quotas.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--delete-quota', 'consumerByteRate',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/user_alter_one_quota.yaml') as file:
                user_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('commons.get_resource_yaml')
    @mock.patch('kfk_users.resource_exists')
    @mock.patch('kfk_users.os')
    def test_alter_user_with_two_quotas_delete_two_quotas(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_alter_two_quotas.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml
            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--delete-quota', 'consumerByteRate',
                                         '--delete-quota', 'requestPercentage', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/user_alter_with_quotas_empty.yaml') as file:
                user_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())
