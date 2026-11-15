import unittest

from agntia_adversarial.execution.oci import OCISandbox, RuntimeSpec, SandboxError

DIGEST_IMAGE = "ghcr.io/example/scanner@sha256:" + "a" * 64


class OCITests(unittest.TestCase):
    def test_rejects_floating_image(self):
        with self.assertRaises(SandboxError):
            RuntimeSpec(image="ghcr.io/example/scanner:latest").validate()

    def test_command_is_hardened(self):
        sandbox = OCISandbox(RuntimeSpec(image=DIGEST_IMAGE))
        command = sandbox.command(["semgrep", "--version"])
        joined = " ".join(command)
        self.assertIn("--network=none", joined)
        self.assertIn("--read-only", joined)
        self.assertIn("--cap-drop=ALL", joined)
        self.assertIn("no-new-privileges", joined)
        self.assertIn("--pids-limit=128", joined)
        self.assertIn(DIGEST_IMAGE, command)

    def test_fake_runner_gets_exact_argv(self):
        captured = {}

        def runner(command):
            captured["command"] = list(command)
            return {"returncode": 0, "stdout": "ok", "stderr": ""}

        sandbox = OCISandbox(RuntimeSpec(image=DIGEST_IMAGE), runner=runner)
        result = sandbox.run(["echo", "hi; rm -rf /"])
        self.assertEqual(result["status"], "PASS")
        self.assertIn("hi; rm -rf /", captured["command"])
        self.assertNotIn("sh", captured["command"])

    def test_local_sha256_image_id_is_accepted(self):
        local = "sha256:" + "d" * 64
        RuntimeSpec(image=local).validate()

    def test_short_or_floating_id_is_rejected(self):
        for image in ("sha256:abc", "alpine:latest", "docker.io/library/alpine"):
            with self.assertRaises(SandboxError):
                RuntimeSpec(image=image).validate()

    def test_missing_runtime_is_blocked(self):
        sandbox = OCISandbox(RuntimeSpec(image=DIGEST_IMAGE, runtime="not-a-real-runtime"))
        self.assertEqual(sandbox.run(["echo", "x"])["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
