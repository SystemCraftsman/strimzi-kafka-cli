class StrimziKafkaCli < Formula
  include Language::Python::Virtualenv

  desc "Command Line Interface for Strimzi Kafka Operator"
  homepage "https://github.com/systemcraftsman/strimzi-kafka-cli"
  url "file:///dev/null"
  license "Apache-2.0"
  version "0.1.0a58"

  depends_on ["python@3.9", "python@3.8", "python@3.7", "python@3.6"]

  def install
    venv = virtualenv_create(libexec, python="python3")

    @venv_root = venv.instance_variable_get(:@venv_root)
    @formula = venv.instance_variable_get(:@formula)

    bin_before = Dir[@venv_root/"bin/*"].to_set

    system @venv_root/"bin/pip", "install", "strimzi-kafka-cli==" + version

    bin_after = Dir[@venv_root/"bin/*"].to_set
    bin_to_link = (bin_after - bin_before).to_a

    @formula.bin.install_symlink(bin_to_link)
  end

  test do
    assert_match "Strimzi Kafka CLI", shell_output("#{bin}/kfk")
    assert_match "CLI Version: " + version, shell_output("#{bin}/kfk --version")
  end
end
