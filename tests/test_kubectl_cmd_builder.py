from unittest import TestCase
from ..kubectl_command_builder import Kubectl


class TestKubectl(TestCase):
    def test_get(self):
        self.assertEqual(Kubectl().get().build(), "kubectl get")

    def test_create(self):
        self.assertEqual(Kubectl().create().build(), "kubectl create")

    def test_apply(self):
        self.assertEqual(Kubectl().apply().build(), "kubectl apply")

    def test_describe(self):
        self.assertEqual(Kubectl().describe().build(), "kubectl describe")

    def test_delete(self):
        self.assertEqual(Kubectl().delete().build(), "kubectl delete")

    def test_exec(self):
        self.assertEqual(
            Kubectl().exec("-it", "test-pod").container("test-container").namespace("test-namespace").exec_command(
                "echo 'test'").build(),
            "kubectl exec -it test-pod -c test-container -n test-namespace -- echo 'test'")

    def test_kafkas_all(self):
        self.assertEqual(Kubectl().get().kafkas().build(), "kubectl get kafkas")

    def test_kafkas_specific(self):
        self.assertEqual(Kubectl().get().kafkas("my-cluster").build(), "kubectl get kafkas my-cluster")

    def test_kafkatopics_all(self):
        self.assertEqual(Kubectl().get().kafkatopics().build(), "kubectl get kafkatopics")

    def test_kafkatopics_specific(self):
        self.assertEqual(Kubectl().get().kafkatopics("my-topic").build(), "kubectl get kafkatopics my-topic")

    def test_kafkausers_all(self):
        self.assertEqual(Kubectl().get().kafkausers().build(), "kubectl get kafkausers")

    def test_kafkausers_specific(self):
        self.assertEqual(Kubectl().get().kafkausers("my-user").build(), "kubectl get kafkausers my-user")

    def test_label(self):
        self.assertEqual(Kubectl().get().kafkatopics().label("app=test").build(), "kubectl get kafkatopics -l app=test")

    def test_labels(self):
        self.assertEqual(Kubectl().get().kafkatopics().label("app=test, included=true").build(),
                         "kubectl get kafkatopics -l app=test, included=true")

    def test_namespace(self):
        self.assertEqual(Kubectl().get().kafkatopics().namespace("test").build(), "kubectl get kafkatopics -n test")

    def test_label_namespace(self):
        self.assertEqual(Kubectl().get().kafkatopics().label("app=test").namespace("test").build(),
                         "kubectl get kafkatopics -l app=test -n test")

    def test_cluster(self):
        self.assertEqual(Kubectl().get().kafkas().container("test-container").build(),
                         "kubectl get kafkas -c test-container")

    def test_output(self):
        self.assertEqual(Kubectl().get().kafkas().output("yaml").build(), "kubectl get kafkas -o yaml")

    def test_from_file(self):
        self.assertEqual(Kubectl().create().from_file("/a/test/path/testfile.yaml").build(),
                         "kubectl create -f /a/test/path/testfile.yaml")
