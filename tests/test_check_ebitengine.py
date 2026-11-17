"""End-to-end tests of the read-only Ebitengine checker CLI; no Go/display needed."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/ebitengine/ebitengine-game/scripts/check_ebitengine.py"
SOURCE = '''package main
import e "github.com/hajimehoshi/ebiten/v2"
func f() { e.SetMaxTPS(60); e.CurrentFPS() }
'''


class CheckEbitengineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "game with spaces"
        self.root.mkdir()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_check(self, *args, target=None):
        return subprocess.run([sys.executable, str(SCRIPT), str(target or self.root), *args],
                              capture_output=True, text=True)

    def test_json_and_text_are_warnings_until_strict_is_requested(self):
        path = self.write("main.go", SOURCE)
        original = path.read_bytes()
        result = self.run_check("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {"tool", "schema", "root", "files_checked",
                                      "error_count", "warning_count", "errors", "warnings", "truncated",
                                      "note_count", "notes"})
        self.assertEqual((report["tool"], report["schema"]), ("check_ebitengine", 1))
        self.assertEqual(report["root"], self.root.resolve().as_posix())
        self.assertEqual((report["error_count"], report["warning_count"], report["files_checked"]), (0, 2, 1))
        self.assertFalse(report["errors"])
        self.assertFalse(report["truncated"])
        self.assertTrue(all(i["file"] == "main.go" and i["line"] == 3 and i["fix"] for i in report["warnings"]))
        strict = self.run_check("--strict")
        self.assertEqual(strict.returncode, 1, strict.stderr)
        self.assertIn("WARNING main.go:3:", strict.stdout)
        self.assertIn("  fix:", strict.stdout)
        self.assertIn("Summary: 0 errors, 2 warnings in 1 files checked", strict.stdout)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual([p.name for p in self.root.iterdir()], ["main.go"])

    def test_truncation_preserves_totals_and_exit_status(self):
        self.write("main.go", SOURCE)
        result = self.run_check("--json", "--strict", "--max-issues", "1")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["warning_count"], len(report["warnings"])), (2, 1))
        self.assertTrue(report["truncated"])
        result = self.run_check("--json", "--max-issues", "0")
        report = json.loads(result.stdout)
        self.assertEqual(len(report["warnings"]), 2)
        self.assertFalse(report["truncated"])

    def test_clean_alias_and_comment_literal_do_not_create_findings(self):
        path = self.write("日本語.go", '''package main
import e "github.com/hajimehoshi/ebiten/v2"
// e.SetMaxTPS(60)
const example = `import "github.com/hajimehoshi/ebiten"; e.CurrentFPS()`
func f() { e.SetTPS(60) }
''')
        result = self.run_check("--json", "--strict", target=path)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["warning_count"], report["error_count"], report["files_checked"]), (0, 0, 1))

    def test_tests_and_generated_dependencies_are_excluded_by_default(self):
        self.write("main.go", SOURCE.replace("e.SetMaxTPS(60); e.CurrentFPS()", "e.SetTPS(60)"))
        self.write("main_test.go", SOURCE)
        self.write("vendor/dependency.go", SOURCE)
        self.write("node_modules/dependency.go", SOURCE)
        self.write(".hidden/dependency.go", SOURCE)
        report = json.loads(self.run_check("--json", "--strict").stdout)
        self.assertEqual((report["warning_count"], report["files_checked"]), (0, 1))
        result = self.run_check("--json", "--strict", "--include-tests")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["warning_count"], report["files_checked"]), (2, 2))
        self.assertTrue(all(i["file"] == "main_test.go" for i in report["warnings"]))

    def test_missing_wrong_project_and_bad_arguments_exit_two(self):
        self.write("main.go", '''package main
// github.com/hajimehoshi/ebiten/v2 is only a comment.
const example = `import "github.com/hajimehoshi/ebiten/v2"`
func main() {}
''')
        for target, args in ((self.root / "missing", ()), (self.root, ()),
                             (self.write("readme.txt", "text"), ()),
                             (self.root, ("--max-issues", "-1"))):
            with self.subTest(target=target, args=args):
                result = self.run_check(*args, target=target)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("error:", result.stderr)
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--max-issues", result.stdout)

    def test_module_signal_allows_checking_a_rules_only_package(self):
        self.write("go.mod", "module example.com/game\n\ngo 1.25\n\nrequire (\n github.com/hajimehoshi/ebiten/v2 v2.10.5\n)\n")
        self.write("rules.go", "package game\nfunc score() int { return 1 }\n")
        result = self.run_check("--json", "--strict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["files_checked"], 1)

    def test_struct_fields_named_like_packages_are_not_package_calls(self):
        self.write("main.go", '''package main
import (
    e "github.com/hajimehoshi/ebiten/v2"
    "github.com/hajimehoshi/ebiten/v2/audio"
)
func f(s *S, r R) { s.audio.NewPlayer(r); s.e.SetMaxTPS(60); audio.CurrentContext() }
''')
        result = self.run_check("--json", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["warning_count"], 0)

    def test_ambiguous_at_calls_are_notes_and_do_not_fail_strict(self):
        self.write("main.go", '''package main
import e "github.com/hajimehoshi/ebiten/v2"
func (g *Game) Draw(screen *e.Image) {
    g.Map.At(p)
    grid.At(x, y)
    screen.At(0, 0)
    // screen.At(1, 1)
    s := "screen.At(2, 2)"
}
''')
        result = self.run_check("--json", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["warning_count"], 0)
        self.assertEqual(report["note_count"], 3)
        self.assertEqual([n["line"] for n in report["notes"]], [4, 5, 6])
        text = self.run_check("--strict")
        self.assertEqual(text.returncode, 0)
        self.assertIn("NOTE main.go:4:", text.stdout)

    def test_readpixels_stays_warning_and_notes_obey_report_limit(self):
        self.write("main.go", '''package main
import "github.com/hajimehoshi/ebiten/v2"
func (g *Game) Update() error {
    g.Map.At(p)
    g.Map.At(q)
    g.image.ReadPixels(pixels)
    return nil
}
''')
        result = self.run_check("--json", "--strict", "--max-issues", "1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["warning_count"], report["note_count"]), (1, 2))
        self.assertEqual(len(report["warnings"]), 1)
        self.assertEqual(len(report["notes"]), 0)
        self.assertIn("GPU readback", report["warnings"][0]["message"])
        self.assertTrue(report["truncated"])

    def test_deprecated_player_methods_are_checked_only_with_audio_import(self):
        body = "func f(p *P, file *F) { p.Close(); p.Seek(d); p.Current(); file.Seek(0, 0) }\n"
        self.write("main.go", 'package main\nimport "github.com/hajimehoshi/ebiten/v2/audio"\n' + body)
        report = json.loads(self.run_check("--json").stdout)
        self.assertEqual(sorted(i["message"].split(" ")[2] for i in report["warnings"]),
                         ["Player.Close", "Player.Current", "Player.Seek"])
        self.write("main.go", 'package main\nimport "github.com/hajimehoshi/ebiten/v2"\n' + body)
        self.assertEqual(json.loads(self.run_check("--json").stdout)["warning_count"], 0)


if __name__ == "__main__":
    unittest.main()
