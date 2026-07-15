import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("asset_upload.py")
SPEC = importlib.util.spec_from_file_location("asset_upload", SCRIPT)
asset_upload = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(asset_upload)


class AssetUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repo = self.root / "bee-static"
        (self.repo / ".git").mkdir(parents=True)
        self.source_dir = self.root / "incoming"
        self.source_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def mark_cdn_available(self, plan):
        return asset_upload.check_cdn(plan, probe=lambda url, timeout: 404)

    def test_rejects_destination_that_escapes_repo(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"logo")

        with self.assertRaisesRegex(ValueError, "relative path"):
            asset_upload.build_plan(self.repo, [source], "../outside")

    def test_extracts_final_hash_from_iconfont_download_folder(self):
        source = self.root / "font_4071061_semole6prt"
        source.mkdir()

        self.assertEqual(asset_upload.extract_iconfont_hash(source), "semole6prt")

    def test_rejects_iconfont_folder_without_expected_name(self):
        source = self.root / "font_4071061"
        source.mkdir()

        with self.assertRaisesRegex(ValueError, "font_<project-id>_<hash>"):
            asset_upload.extract_iconfont_hash(source)

    def test_builds_iconfont_destination_from_final_hash_only(self):
        source = self.root / "font_4071061_semole6prt"
        source.mkdir()
        (source / "iconfont.css").write_bytes(b"css")

        plan = asset_upload.build_iconfont_plan(
            self.repo,
            source,
        )

        self.assertEqual(plan["destination"], "hashIconfontDir/semole6prt")
        self.assertEqual(
            plan["files"][0]["relative_target"],
            "hashIconfontDir/semole6prt/iconfont.css",
        )
        self.assertEqual(plan["iconfont"]["root_status"], "create")

    def test_reuses_existing_hash_iconfont_directory(self):
        (self.repo / "hashIconfontDir").mkdir()
        source = self.root / "font_4071061_semole6prt"
        source.mkdir()
        (source / "iconfont.css").write_bytes(b"css")

        plan = asset_upload.build_iconfont_plan(self.repo, source)

        self.assertEqual(plan["iconfont"]["root_status"], "existing")

    def test_rejects_non_directory_hash_iconfont_path(self):
        (self.repo / "hashIconfontDir").write_bytes(b"not-a-directory")
        source = self.root / "font_4071061_semole6prt"
        source.mkdir()
        (source / "iconfont.css").write_bytes(b"css")

        with self.assertRaisesRegex(ValueError, "hashIconfontDir must be a directory"):
            asset_upload.build_iconfont_plan(self.repo, source)

    def test_apply_creates_hash_iconfont_directory_after_confirmation(self):
        source = self.root / "font_4071061_semole6prt"
        source.mkdir()
        (source / "iconfont.css").write_bytes(b"css")
        plan = self.mark_cdn_available(asset_upload.build_iconfont_plan(self.repo, source))
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 404)

        self.assertEqual(
            (self.repo / "hashIconfontDir" / "semole6prt" / "iconfont.css").read_bytes(),
            b"css",
        )

    def test_classifies_new_identical_and_conflicting_files(self):
        destination = self.repo / "react-taro-teacher" / "iconfont" / "abc123"
        destination.mkdir(parents=True)
        (destination / "same.svg").write_bytes(b"same")
        (destination / "conflict.svg").write_bytes(b"old")
        (self.source_dir / "new.svg").write_bytes(b"new")
        (self.source_dir / "same.svg").write_bytes(b"same")
        (self.source_dir / "conflict.svg").write_bytes(b"new-value")

        plan = asset_upload.build_plan(
            self.repo,
            [self.source_dir],
            "react-taro-teacher/iconfont/abc123",
        )

        statuses = {Path(item["target"]).name: item["status"] for item in plan["files"]}
        self.assertEqual(
            statuses,
            {"new.svg": "new", "same.svg": "identical", "conflict.svg": "conflict"},
        )

    def test_rejects_symlink_sources(self):
        real = self.source_dir / "real.svg"
        real.write_bytes(b"svg")
        link = self.source_dir / "linked.svg"
        link.symlink_to(real)

        with self.assertRaisesRegex(ValueError, "symbolic link"):
            asset_upload.build_plan(self.repo, [link], "assets")

    def test_apply_rechecks_hash_and_copies_only_new_files(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"version-one")
        plan = self.mark_cdn_available(asset_upload.build_plan(self.repo, [source], "images"))
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        source.write_bytes(b"changed-after-confirmation")
        with self.assertRaisesRegex(ValueError, "changed since planning"):
            asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 404)

        source.write_bytes(b"version-one")
        result = asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 404)
        self.assertEqual(result["copied"], 1)
        self.assertEqual((self.repo / "images" / "logo.png").read_bytes(), b"version-one")

    def test_apply_refuses_conflicts_without_explicit_overwrite(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"new")
        target = self.repo / "images" / "logo.png"
        target.parent.mkdir()
        target.write_bytes(b"old")
        plan = self.mark_cdn_available(asset_upload.build_plan(self.repo, [source], "images"))
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "conflicting target"):
            asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 404)

    def test_apply_rejects_target_tampering_in_plan_file(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"logo")
        plan = self.mark_cdn_available(asset_upload.build_plan(self.repo, [source], "images"))
        plan["files"][0]["target"] = str(self.repo / "different" / "logo.png")
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "inconsistent target"):
            asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 404)

    def test_cdn_check_builds_encoded_url_and_marks_existing_name(self):
        source = self.source_dir / "logo 你好.png"
        source.write_bytes(b"logo")
        plan = asset_upload.build_plan(self.repo, [source], "images")
        requested = []

        checked = asset_upload.check_cdn(
            plan,
            probe=lambda url, timeout: requested.append(url) or 200,
        )

        self.assertEqual(
            requested,
            ["https://static-cdn-test.mifengjiaoyu.com/images/logo%20%E4%BD%A0%E5%A5%BD.png"],
        )
        self.assertEqual(checked["files"][0]["cdn"]["status"], "exists")

    def test_cdn_check_treats_404_as_available_and_5xx_as_unknown(self):
        first = self.source_dir / "first.png"
        second = self.source_dir / "second.png"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        plan = asset_upload.build_plan(self.repo, [self.source_dir], "images")
        statuses = iter([404, 503])

        checked = asset_upload.check_cdn(plan, probe=lambda url, timeout: next(statuses))

        self.assertEqual(
            [item["cdn"]["status"] for item in checked["files"]],
            ["available", "unknown"],
        )

    def test_apply_requires_completed_cdn_check(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"logo")
        plan = asset_upload.build_plan(self.repo, [source], "images")
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "CDN check"):
            asset_upload.apply_plan(plan_file)

    def test_apply_requires_explicit_permission_for_existing_cdn_url(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"logo")
        plan = asset_upload.check_cdn(
            asset_upload.build_plan(self.repo, [source], "images"),
            probe=lambda url, timeout: 200,
        )
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "CDN URL already exists"):
            asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 200)

        result = asset_upload.apply_plan(
            plan_file,
            allow_cdn_overwrite=True,
            cdn_probe=lambda url, timeout: 200,
        )
        self.assertEqual(result["copied"], 1)

    def test_apply_rechecks_cdn_and_rejects_status_change(self):
        source = self.source_dir / "logo.png"
        source.write_bytes(b"logo")
        plan = self.mark_cdn_available(asset_upload.build_plan(self.repo, [source], "images"))
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "CDN status changed"):
            asset_upload.apply_plan(plan_file, cdn_probe=lambda url, timeout: 200)


if __name__ == "__main__":
    unittest.main()
