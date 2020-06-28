from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.users_command import kfk
from kfk.kubectl_command_builder import Kubectl


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

    @mock.patch('kfk.users_command.os')
    def test_list_users(self, mock_os):
        result = self.runner.invoke(kfk, ['users', '--list', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkausers().label("strimzi.io/cluster={cluster}").namespace(self.namespace).build().format(
                cluster=self.cluster))

    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_describe_user(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk, ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                          self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().describe().kafkausers(self.user).namespace(self.namespace).build())

    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_describe_user_output_yaml(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['users', '--describe', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace, '-o',
                                     'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkausers(self.user).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.users_command.os')
    def test_create_user(self, mock_os, mock_create_temp_file):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'tls', '-c',
                                     self.cluster, '-n', self.namespace])

        assert result.exit_code == 0

        with open(r'yaml/user.yaml') as file:
            expected_user_yaml = file.read()
            result_user_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.users_command.os')
    def test_create_user_with_authorization_without_acls(self, mock_os, mock_create_temp_file):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'tls',
                                     '--authorization-type', 'simple', '-c', self.cluster, '-n', self.namespace])

        assert result.exit_code == 1

    def test_create_user_without_auth(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    def test_create_user_with_wrong_authentication_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'auth',
                                     '--authorization-type', 'simple', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 2

    def test_create_user_with_wrong_authorization_type(self):
        result = self.runner.invoke(kfk,
                                    ['users', '--create', '--user', self.user, '--authentication-type', 'tls',
                                     '--authorization-type', 'auth', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 2

    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_delete_user(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['users', '--delete', '--user', self.user, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().delete().kafkausers(self.user).namespace(self.namespace).build())

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_with_no_params(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                       mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'yaml/user.yaml') as file:
            expected_user_yaml = file.read()
            mock_get_resource_yaml.return_value = expected_user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0

            result_user_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_for_authentication_type(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                                mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'yaml/user.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_authentication.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_for_authorization(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                          mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'yaml/user.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authorization-type',
                                         'simple', '--add-acl', '--operation', 'Read', '--resource-type', 'topic',
                                         '--resource-name', 'my-topic', '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_authorization.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_for_quota(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'yaml/user.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '--quota', 'requestPercentage=55',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_one_quota.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_for_two_quotas(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                       mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'yaml/user.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--authentication-type',
                                         'scram-sha-512', '--quota', 'requestPercentage=55',
                                         '--quota', 'consumerByteRate=2097152',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_two_quotas.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_with_two_quotas_delete_one_quota(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                                         mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_with_two_quotas.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--delete-quota',
                                         'consumerByteRate',
                                         '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_one_quota.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_alter_user_with_two_quotas_delete_two_quotas(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                                          mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'yaml/user_with_two_quotas.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['users', '--alter', '--user', self.user, '--delete-quota',
                                         'consumerByteRate',
                                         '--delete-quota', 'requestPercentage', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0

            with open(r'yaml/user_with_quotas_empty.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]

                assert expected_user_yaml == result_user_yaml
