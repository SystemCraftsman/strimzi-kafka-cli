from unittest import TestCase

from kfk.config import KUBECTL_PATH
from kfk.kubectl_command_builder import Kubectl


class TestKubectl(TestCase):
    def test_get(self):
        self.assertEqual(
            Kubectl().get().build(), "{kubectl} get".format(kubectl=KUBECTL_PATH)
        )

    def test_describe(self):
        self.assertEqual(
            Kubectl().describe().build(),
            "{kubectl} describe".format(kubectl=KUBECTL_PATH),
        )

    def test_exec(self):
        self.assertEqual(
            Kubectl()
            .exec("-it", "test-pod")
            .container("test-container")
            .namespace("test-namespace")
            .exec_command("echo 'test'")
            .build(),
            "{kubectl} exec -it test-pod -c test-container -n test-namespace -- bash -c"
            " \"echo 'test'\"".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkas_all(self):
        self.assertEqual(
            Kubectl().get().kafkas().build(),
            "{kubectl} get kafkas".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkas_specific(self):
        self.assertEqual(
            Kubectl().get().kafkas("my-cluster").build(),
            "{kubectl} get kafkas my-cluster".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkatopics_all(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().build(),
            "{kubectl} get kafkatopics".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkatopics_specific(self):
        self.assertEqual(
            Kubectl().get().kafkatopics("my-topic").build(),
            "{kubectl} get kafkatopics my-topic".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkausers_all(self):
        self.assertEqual(
            Kubectl().get().kafkausers().build(),
            "{kubectl} get kafkausers".format(kubectl=KUBECTL_PATH),
        )

    def test_kafkausers_specific(self):
        self.assertEqual(
            Kubectl().get().kafkausers("my-user").build(),
            "{kubectl} get kafkausers my-user".format(kubectl=KUBECTL_PATH),
        )

    def test_configmap_yaml(self):
        self.assertEqual(
            Kubectl().get().configmap("my-cluster-kafka-config").output("yaml").build(),
            "{kubectl} get configmap my-cluster-kafka-config -o yaml".format(
                kubectl=KUBECTL_PATH
            ),
        )

    def test_label(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().label("app=test").build(),
            "{kubectl} get kafkatopics -l app=test".format(kubectl=KUBECTL_PATH),
        )

    def test_labels(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().label("app=test, included=true").build(),
            "{kubectl} get kafkatopics -l app=test, included=true".format(
                kubectl=KUBECTL_PATH
            ),
        )

    def test_namespace(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().namespace("test").build(),
            "{kubectl} get kafkatopics -n test".format(kubectl=KUBECTL_PATH),
        )

    def test_namespace_all(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().namespace().build(),
            "{kubectl} get kafkatopics --all-namespaces".format(kubectl=KUBECTL_PATH),
        )

    def test_label_namespace(self):
        self.assertEqual(
            Kubectl().get().kafkatopics().label("app=test").namespace("test").build(),
            "{kubectl} get kafkatopics -l app=test -n test".format(
                kubectl=KUBECTL_PATH
            ),
        )

    def test_cluster(self):
        self.assertEqual(
            Kubectl().get().kafkas().container("test-container").build(),
            "{kubectl} get kafkas -c test-container".format(kubectl=KUBECTL_PATH),
        )

    def test_output(self):
        self.assertEqual(
            Kubectl().get().kafkas().output("yaml").build(),
            "{kubectl} get kafkas -o yaml".format(kubectl=KUBECTL_PATH),
        )
