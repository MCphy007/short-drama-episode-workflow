"""Smoke-test the distributed ZIP without modifying the user's skills or starting production."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

SLUG = "short-drama-episode-workflow"
ARCHIVE = Path(__file__).resolve().with_name(SLUG + "-portable.zip")


class PortableInstallTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        with zipfile.ZipFile(ARCHIVE) as package:
            self.assertIsNone(package.testzip())
            package.extractall(self.folder)
        self.source = self.folder / SLUG
        self.home = self.folder / "隔离 user"
        self.home.mkdir()
        self.discovery = self.home / ".agents/skills"
        self.store = self.folder / "skills 实体"
        self.env = os.environ | {"HOME": str(self.home), "USERPROFILE": str(self.home),
                                 "CODEX_HOME": str(self.home / ".codex"), "WSL_DISTRO_NAME": "",
                                 "EPISODE_NONINTERACTIVE": "1"}
        self.lock = json.loads((self.source / "assets/portable-manifest.json").read_text(encoding="utf-8"))
        self.names = self.lock["skills"] + [SLUG]
        if os.name == "nt":
            self.command = ["cmd.exe", "/d", "/c", "Install-Windows.cmd"]
        else:
            self.command = ["sh", "./install.sh"]

    def invoke(self, *args, expected=0, installed=False):
        root = self.discovery / SLUG if installed else self.source
        p = subprocess.run([*self.command, *map(str, args)], cwd=root, env=self.env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        self.assertEqual(p.returncode, expected, p.stdout.decode(errors="replace"))

    def test_install_register_rerun_and_recover(self):
        self.invoke("--dest", self.store, "--check", expected=2)
        self.assertFalse(self.store.exists())
        self.invoke("--dest", self.store)
        for name in self.names:
            self.assertTrue((self.store / name).samefile(self.discovery / name))
            self.assertTrue((self.discovery / name / "SKILL.md").is_file())
        for name in [*self.lock["workflow_files"], "assets/portable-manifest.json", "assets/skill-dependencies.zip"]:
            self.assertEqual((self.discovery / SLUG / name).read_bytes(), (self.source / name).read_bytes())
        self.assertTrue((self.store / SLUG / "references/portable-install.md").is_file())
        self.invoke("--check", installed=True)
        marker = self.store / "hyperframes" / "local-note.txt"
        marker.write_text("keep me")
        # Simulate removal of one installed link and skill; recover into the originally chosen store.
        missing = "free-bgm-search"
        link = self.discovery / missing
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()
        shutil.rmtree(self.store / missing)
        self.invoke("--check", expected=2, installed=True)
        self.invoke(installed=True)
        self.assertTrue((self.store / missing).samefile(self.discovery / missing))
        self.invoke(installed=True)
        self.assertEqual(marker.read_text(), "keep me")

    def test_conflict_is_read_only(self):
        old = self.home / ".codex/skills/short-drama-edit/SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_text("Existing custom skill",encoding="utf-8")
        self.invoke("--dest", self.store, expected=1)
        self.assertFalse(self.store.exists())
        self.assertFalse(self.discovery.exists())
        self.assertEqual(old.read_text(encoding="utf-8"), "Existing custom skill")

    def test_reject_damaged_bundle(self):
        payload = self.source / "assets/skill-dependencies.zip"
        self.assertEqual(hashlib.sha256(payload.read_bytes()).hexdigest(), self.lock["archive_sha256"])
        with payload.open("ab") as f:
            f.write(b"damage")
        self.invoke("--dest", self.store, expected=1)
        self.assertFalse(self.discovery.exists())
        self.assertFalse(self.store.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
