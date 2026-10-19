import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
for (const base of [
  "https://other.example/",
  "//other.example/",
  "/../assets/",
  "/papers?x=1",
  "/papers#fragment",
]) {
  test("reject unsafe base " + base, () => {
    const result = spawnSync(process.execPath, ["site/build.mjs", "--base", base], {
      cwd: root,
      encoding: "utf8",
    });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Base path must/);
  });
}
test("reject output traversal before touching source files", () => {
  const result = spawnSync(process.execPath, ["site/build.mjs", "--out", "../assets"], {
    cwd: root,
    encoding: "utf8",
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Output must/);
});
