// readers/node_dotenv_all.js
// Usage: node readers/node_dotenv_all.js <file-or-dir> [--out results/node-dotenv.json]
const fs = require("fs");
const path = require("path");
const dotenv = require("dotenv");
const { expand } = require("dotenv-expand");

function read(file) {
  try {
    const plain = dotenv.parse(fs.readFileSync(file)); // pass the raw Buffer
    // processEnv: {} so expansion can't see the real environment
    const expanded = expand({ parsed: { ...plain }, processEnv: {} }).parsed;
    return { plain, expanded };
  } catch (e) {
    return { error: `${e.name}: ${e.message}` };
  }
}

// Stable key order, so the file diffs cleanly in git
function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value).sort().map((k) => [k, sortKeys(value[k])])
    );
  }
  return value;
}

const args = process.argv.slice(2);
const outIdx = args.indexOf("--out");
const out = outIdx !== -1 ? args[outIdx + 1] : null;
const target = args.find((a, i) => !a.startsWith("--") && i !== outIdx + 1);

if (!target) {
  console.error("usage: node readers/node_dotenv_all.js <file-or-dir> [--out file.json]");
  process.exit(2);
}

let result;
if (fs.statSync(target).isDirectory()) {
  result = {};
  for (const f of fs.readdirSync(target).filter((f) => f.endsWith(".env")).sort()) {
    result[path.basename(f, ".env")] = read(path.join(target, f));
  }
} else {
  result = read(target);
}

const text = JSON.stringify(sortKeys(result), null, 2) + "\n";
if (out) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, text, "utf8");
} else {
  process.stdout.write(text);
}
