from kfk.constants import SPACE

class Kubectl:

    def __init__(self):
        self.cmd_str = "kubectl"

    def get(self):
        self.cmd_str = self.cmd_str + SPACE + "get"
        return self

    def create(self):
        self.cmd_str = self.cmd_str + SPACE + "create"
        return self

    def apply(self):
        self.cmd_str = self.cmd_str + SPACE + "apply"
        return self

    def describe(self):
        self.cmd_str = self.cmd_str + SPACE + "describe"
        return self

    def delete(self):
        self.cmd_str = self.cmd_str + SPACE + "delete"
        return self

    def exec(self, flag, pod_name):
        self.cmd_str = self.cmd_str + SPACE + "exec" + SPACE + flag + SPACE + pod_name
        return self

    def exec_command(self, command):
        self.cmd_str = self.cmd_str + SPACE + "--" + SPACE + command
        return self

    def kafkas(self, *vals):
        return self.resource("kafkas", *vals)

    def kafkatopics(self, *vals):
        return self.resource("kafkatopics", *vals)

    def kafkausers(self, *vals):
        return self.resource("kafkausers", *vals)

    def resource(self, resource_name, *vals):
        self.cmd_str = self.cmd_str + SPACE + resource_name
        for val in vals:
            self.cmd_str = self.cmd_str + SPACE + val
        return self

    def label(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-l" + SPACE + val
        return self

    def namespace(self, val):
        self.cmd_str = self.cmd_str + SPACE + "-n" + SPACE + val
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
