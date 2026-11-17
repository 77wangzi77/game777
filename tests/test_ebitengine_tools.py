#!/usr/bin/env python3
"""Offline regression tests for the skill's project and release helpers.

Run: python3 -m unittest tests.test_ebitengine_tools
The generated Go game's build/render checks are separate; these tests do not
require a display, Go, network access, or a signing identity.
"""
import contextlib
import importlib.util
import io
import os
import plistlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parents[1] / "skills/ebitengine/ebitengine-game/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load("check_ebitengine")
packager = load("package_macos_app")


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_tool(self, name, *args):
        return subprocess.run([sys.executable, str(HERE / name), *map(str, args)],
                              capture_output=True, text=True)

    def test_generator_escapes_title_and_supports_underscore_module(self):
        out = self.root / "game with spaces"
        result = self.run_tool("new_game.py", "--out", out, "--module", "example.com/my_game",
                               "--title", 'A "quoted" \\ path & <game>', "--ci")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(r'\"quoted\" \\ path', (out / "main.go").read_text())
        self.assertIn("&amp; &lt;game&gt;", (out / "web/index.html").read_text())
        self.assertIn("com.example.my-game", (out / ".github/workflows/ci.yml").read_text())
        result = self.run_tool("check_ebitengine.py", out, "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (out / "keep.txt").write_text("keep")
        result = self.run_tool("new_game.py", "--out", out, "--module", "example.com/my_game")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((out / "keep.txt").read_text(), "keep")

    def test_generator_skips_major_version_suffix_in_game_name(self):
        out = self.root / "versioned"
        result = self.run_tool("new_game.py", "--out", out, "--module", "github.com/you/coolgame/v2", "--ci")
        self.assertEqual(result.returncode, 0, result.stderr)
        workflow = (out / ".github/workflows/ci.yml").read_text()
        self.assertIn("GAME: coolgame", workflow)
        self.assertIn("com.example.coolgame", workflow)

    def test_generator_rejects_known_incompatible_or_bad_inputs_before_writing(self):
        for options in (("--module", "example.com/../game"),
                        ("--ebiten", "v2.9.0"), ("--go", "1.24.0")):
            with self.subTest(options=options):
                out = self.root / "rejected"
                result = self.run_tool("new_game.py", "--out", out,
                                       "--module", "example.com/game", *options)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(out.exists())

    def scan(self, src):
        path = self.root / "scan.go"
        path.write_text(src)
        return checker.scan_file(str(path), [])

    def test_checker_handles_aliases_comments_and_unrelated_types(self):
        found = self.scan('''package main
import e "github.com/hajimehoshi/ebiten/v2"
// import "github.com/hajimehoshi/ebiten/v2/text"
const example = `import "github.com/hajimehoshi/ebiten"`
func f() { e.SetMaxTPS(60) }
''')
        self.assertEqual([(f[0], f[1], f[2]) for f in found],
                         [("warn", str(self.root / "scan.go"), 5)])
        found = self.scan('''package main
import audio "example.com/audio"
func f() { audio.NewPlayer(nil); obj.ReplacePixels(nil); obj.ColorM.Reset() }
''')
        self.assertFalse([f for f in found if f[0] == "error"])
        self.assertEqual(len(found), 2)  # ambiguous receiver methods are review warnings

    def test_checker_multiple_context_sites_are_review_warnings(self):
        for suffix in ("linux", "windows"):
            (self.root / ("sound_" + suffix + ".go")).write_text('''package main
import "github.com/hajimehoshi/ebiten/v2/audio"
func newSound() { audio.NewContext(48000) }
''')
        result = self.run_tool("check_ebitengine.py", self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("multiple audio.NewContext call sites", result.stdout)
        self.assertIn("WARNING sound_linux.go:3:", result.stdout)
        self.assertIn("WARNING sound_windows.go:3:", result.stdout)

    def test_checker_old_import_reports_source_file_and_import_line(self):
        found = self.scan('''package main
import (
    "github.com/hajimehoshi/ebiten"
    "fmt"
)
''')
        self.assertEqual([(f[0], f[1], f[2]) for f in found],
                         [("warn", str(self.root / "scan.go"), 3)])

    def macho_header(self, arch):
        path = self.root / arch
        path.write_bytes(struct.pack("<8I", 0xFEEDFACF, packager.MACHO_CPUS[arch], 0,
                                     2, 1, 24, 0, 0) + struct.pack("<6I", 0x32, 24, 1, 13 << 16, 13 << 16, 0))
        return path

    def package_args(self, binary, *extra):
        return ["--name", "Test Game", "--bundle-id", "com.example.test", "--arm64", binary,
                "--out", self.root / "apps", *extra]

    def test_packager_checks_architecture_and_output_paths(self):
        arm = self.macho_header("arm64")
        for extra in (("--name", "../escaped"), ("--exe", "../escaped"),
                      ("--build", "1.2-beta"), ("--min-macos", "12.0"), ("--arm64", self.macho_header("amd64"))):
            with self.subTest(extra=extra):
                result = self.run_tool("package_macos_app.py", *self.package_args(arm, *extra))
                self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((self.root / "escaped.app").exists())
        self.assertFalse((self.root / "apps").exists())

    def test_packager_single_arch_bundle_and_force_failure_preserves_existing(self):
        arm = self.macho_header("arm64")
        result = self.run_tool("package_macos_app.py", *self.package_args(arm))
        self.assertEqual(result.returncode, 0, result.stderr)
        app = self.root / "apps/Test Game.app"
        with (app / "Contents/Info.plist").open("rb") as f:
            self.assertEqual(plistlib.load(f)["CFBundleExecutable"], "testgame")
        target = app / "Contents/MacOS/testgame"
        # Windows does not expose POSIX execute bits for an extensionless file.
        # Keep the rest of the bundle/preservation test active on every platform.
        if os.name != "nt":
            self.assertTrue(target.stat().st_mode & 0o111)
        original = target.read_bytes()
        # A failed universal merge should never destroy an existing good bundle.
        argv = ["package_macos_app.py", *map(str, self.package_args(arm, "--amd64", self.macho_header("amd64"), "--force"))]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(packager, "find_lipo", return_value="lipo"), \
             mock.patch.object(packager.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "bad input")):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                packager.main()
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(sorted(p.name for p in app.parent.iterdir()), [app.name])


if __name__ == "__main__":
    unittest.main()
