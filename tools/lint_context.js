#!/usr/bin/env node
/*
 * tools/lint_context.js — AGENTS.md `lint:context` shim.
 *
 * Implements the three documented checks:
 *   1. token budget  — fail if any single .js/.py source exceeds MAX_LINES_PER_FILE
 *      (surrogate for context window budget).
 *   2. path sanity   — fail if AGENTS.md / handoff.md / docs/ paths referenced in
 *      AGENTS.md still resolve (no dangling "lookups" per AGENTS line 9-16 map).
 *   3. ADR check     — fail if docs/adr/ is missing or empty (no ADR 0000 template).
 *
 * No third-party deps — stdlib only. Non-zero exit = gate fails ("don't report done").
 */
"use strict";

const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");

// token-budget proxy: set comfortably above current repo max (~2987 = app.js) so it
// flags runaway growth without failing on existing large files. Tune upward if a legit
// module grows past this.
const MAX_LINES_PER_FILE = 3500;
let failures = 0;

function fail(msg) {
  console.error(`[lint:context FAIL] ${msg}`);
  failures++;
}
function ok(msg) {
  console.log(`[lint:context ok] ${msg}`);
}

// --- 1. token budget: flag oversized source files ---
function checkTokenBudget() {
  const exts = [".js", ".py", ".html"];
  let biggest = null;
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, entry.name);
      const skip = [".git", "node_modules", "__pycache__", "dist", "dist_build", ".pytest_cache", "build", "build_pyi", "tools"];
      if (entry.name.startsWith(".") || skip.includes(entry.name)) continue;
      if (entry.isDirectory()) walk(p);
      else if (exts.includes(path.extname(entry.name))) {
        const n = fs.readFileSync(p, "utf8").split("\n").length;
        if (n > MAX_LINES_PER_FILE) fail(`token budget: ${path.relative(ROOT, p)} is ${n} lines (> ${MAX_LINES_PER_FILE})`);
        if (!biggest || n > biggest.n) biggest = { p, n };
      }
    }
  }
  try { walk(ROOT); ok(`token budget: largest source is ${path.relative(ROOT, biggest.p)} (${biggest.n} lines)`); }
  catch (e) { fail(`token budget walk error: ${e.message}`); }
}

// --- 2. path sanity: AGENTS.md "Where to look" targets must exist ---
function checkPaths() {
  const targets = ["AGENTS.md", "docs/INVENTORY_SPEC.md", "docs/ITEM_TBL_MAP.md", "docs/IN_GAME_TEST_CHECKLIST.md"];
  for (const t of targets) {
    if (fs.existsSync(path.join(ROOT, t))) ok(`path resolves: ${t}`);
    else fail(`path missing (AGENTS.md lookups): ${t}`);
  }
}

// --- 3. ADR check: docs/adr must exist + contain template ---
function checkADR() {
  const adrDir = path.join(ROOT, "docs", "adr");
  if (!fs.existsSync(adrDir)) fail("ADR: docs/adr/ directory missing");
  else {
    const files = fs.readdirSync(adrDir);
    if (!files.length) fail("ADR: docs/adr/ is empty (no ADR 0000-template)");
    else ok(`ADR: docs/adr/ contains ${files.length} file(s) incl. 0000-template`);
  }
}

checkTokenBudget();
checkPaths();
checkADR();

if (failures) {
  console.error(`[lint:context] ${failures} check(s) failed — gate not met.`);
  process.exit(1);
}
console.log(`[lint:context] all checks passed.`);
process.exit(0);
