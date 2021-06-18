from kfk.config import KUBECTL_PATH
from kfk.constants import SPACE


class Kubectl:

    def __init__(self):
        self.cmd_str = KUBECTL_PATH

    def version(self, *vals):
        self.cmd_str = self.cmd_str + SPACE + "version"
        for val in vals:
            self.cmd_str = self.cmd_str + SPACE + val
        return self

    def get(self):
        self.cmd_str = self.cmd_str + SPACE + "get"
        return self

    def create(self):
        self.cmd_str = self.cmd_str + SPACE + "create"
        return self

    def apply(self):
        self.cmd_str = self.cmd_str + SPACE + "apply"
        return self

    def replace(self):
        self.cmd_str = self.cmd_str + SPACE + "replace"
        return self

    def describe(self):
        self.cmd_str = self.cmd_str + SPACE + "describe"
        return self

    def delete(self):
        self.cmd_str = self.cmd_str + SPACE + "delete"
        return self

    def edit(self):
        self.cmd_str = self.cmd_str + SPACE + "edit"
        return self

    def exec(self, flag, pod_name):
        self.cmd_str = self.cmd_str + SPACE + "exec" + SPACE + flag + SPACE + pod_name
        return self

    def exec_command(self, command):
        self.cmd_str = self.cmd_str + SPACE + "--" + SPACE + "bash -c" + SPACE + "\"" + command + "\""
        return self

    def cp(self, source_path, destination_path):
        self.cmd_str = self.cmd_str + SPACE + "cp" + SPACE + source_path + SPACE + destination_path
        return self

    def kafkas(self, *vals):
        return self.resource("kafkas", *vals)

    def kafkaconnects(self, *vals):
        return self.resource("kafkaconnects", *vals)

    def kafkaconnectors(self, *vals):
        return self.resource("kafkaconnectors", *vals)

    def kafkatopics(self, *vals):
        return self.resource("kafkatopics", *vals)

    def kafkausers(self, *vals):
        return self.resource("kafkausers", *vals)

    def configmap(self, *vals):
        return self.resource("configmap", *vals)

    def secret(self, *vals):
        return self.resource("secret", *vals)

    def resource(self, resource_name, *vals):
        self.cmd_str = self.cmd_str + SPACE + resource_name
        for val in vals:
            self.cmd_str = self.cmd_str + SPACE + val
        return self

    def label(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-l" + SPACE + val
        return self

    def namespace(self, *vals):
        if len(vals) > 0 and vals[0]:
            self.cmd_str = self.cmd_str + SPACE + "-n" + SPACE + vals[0]
        else:
            self.cmd_str = self.cmd_str + SPACE + "--all-namespaces"
        return self

    def container(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-c" + SPACE + val
        return self

    def output(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-o" + SPACE + val
        return self

    def from_file(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-f" + SPACE + val
        return self

    def build(self):
        return self.cmd_str
