import json
import tempfile
import unittest
from pathlib import Path

from scripts.skilllib import RegistryError, build_links, verify_repo


class SkillLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        (self.repo / "upstreams/example/skills/external-skill").mkdir(parents=True)
        (self.repo / "upstreams/example/skills/external-skill/SKILL.md").write_text(
            "---\nname: external-skill\ndescription: test\n---\n",
            encoding="utf-8",
        )
        (self.repo / "skills/local/frontend/local-skill").mkdir(parents=True)
        (self.repo / "skills/local/frontend/local-skill/SKILL.md").write_text(
            "---\nname: local-skill\ndescription: test\n---\n",
            encoding="utf-8",
        )
        self.write_registry(
            {
                "schemaVersion": 1,
                "localRoots": ["skills/local"],
                "sources": [
                    {
                        "id": "example",
                        "url": "https://github.com/example/example.git",
                        "checkout": "upstreams/example",
                        "skillRoots": ["skills"],
                        "include": ["external-skill"],
                    }
                ],
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_registry(self, registry):
        (self.repo / "registry.json").write_text(
            json.dumps(registry), encoding="utf-8"
        )

    def test_build_links_creates_relative_links_for_local_and_external_skills(self):
        names = build_links(self.repo)

        self.assertEqual(names, ["external-skill", "local-skill"])
        external = self.repo / "enabled/external-skill"
        local = self.repo / "enabled/local-skill"
        self.assertTrue(external.is_symlink())
        self.assertTrue(local.is_symlink())
        self.assertFalse(external.readlink().is_absolute())
        self.assertFalse(local.readlink().is_absolute())
        self.assertEqual(external.resolve().name, "external-skill")
        self.assertEqual(local.resolve().name, "local-skill")

    def test_verify_repo_rejects_missing_declared_skill(self):
        registry = json.loads((self.repo / "registry.json").read_text())
        registry["sources"][0]["include"].append("missing-skill")
        self.write_registry(registry)

        with self.assertRaisesRegex(RegistryError, "missing-skill"):
            build_links(self.repo)

    def test_build_links_rejects_duplicate_skill_names(self):
        duplicate = self.repo / "skills/local/quality/external-skill"
        duplicate.mkdir(parents=True)
        (duplicate / "SKILL.md").write_text(
            "---\nname: external-skill\ndescription: duplicate\n---\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(RegistryError, "duplicate"):
            build_links(self.repo)

    def test_verify_repo_detects_broken_enabled_link(self):
        build_links(self.repo)
        target = self.repo / "upstreams/example/skills/external-skill"
        target.rename(target.with_name("renamed-skill"))

        with self.assertRaisesRegex(RegistryError, "broken"):
            verify_repo(self.repo)


if __name__ == "__main__":
    unittest.main()
