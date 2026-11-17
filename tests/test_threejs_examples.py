"""Execute the published scene examples with small renderer/timer test doubles."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/web-engines/threejs-scene-setup/SKILL.md"


@unittest.skipUnless(shutil.which("node"), "Node.js required to execute JavaScript examples")
class ThreeExamplesTests(unittest.TestCase):
    def run_js(self, source):
        result = subprocess.run(["node", "--input-type=module", "-e", source],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_loop_bounds_negative_and_stalled_deltas_without_losing_normal_time(self):
        section = SKILL.read_text(encoding="utf-8").split("### 3.")[1].split("### 4.")[0]
        snippet = re.search(r"```js\n(.*?)```", section, re.S).group(1)
        self.run_js('''
import assert from 'node:assert/strict';
let delta = 0, callback, updates = 0, renders = 0;
const THREE = { Timer: class {
  connect() {} update() { updates++; } getDelta() { return delta; }
}};
const document = {}, scene = {}, camera = {};
const cube = { rotation: { x: 0, y: 0 } };
const renderer = { setAnimationLoop(fn) { callback = fn; }, render() { renders++; } };
''' + snippet + '''
for (const [raw, expected] of [[-0.004, 0], [2, 0.1], [0.016, 0.016], [0, 0]]) {
  delta = raw;
  const before = cube.rotation.x;
  callback(1000);
  assert.ok(Math.abs(cube.rotation.x - before - expected) < 1e-10,
    `delta ${raw} advanced by ${cube.rotation.x - before}, expected ${expected}`);
}
assert.equal(updates, 4);
assert.equal(renders, 4);
''')

    def test_renderer_defaults_bound_hidpi_without_upscaling_low_dpi(self):
        expressions = re.findall(r"renderer\.setPixelRatio\((.*)\);", SKILL.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(expressions), 2)
        for expression in expressions:
            with self.subTest(expression=expression):
                self.run_js('''
import assert from 'node:assert/strict';
const expression = ''' + json.dumps(expression) + ''';
for (const dpr of [0.75, 1, 1.25, 2, 3]) {
  const value = Function('window', `return (${expression})`)({devicePixelRatio: dpr});
  assert.ok(value > 0 && value <= Math.min(dpr, 1.5), `unexpected ratio ${value}`);
}
''')


if __name__ == "__main__":
    unittest.main()
