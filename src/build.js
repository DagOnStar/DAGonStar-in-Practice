// Build the decks: `node build.js` builds every lecture, `node build.js 7 12 A1` only those.
// Decks go to ../en/lectures/NN-DAGonStar-<Title>.pptx; the build fails on any layout warning.
const fs = require("fs");
const path = require("path");
const { build, applyTheme, warnings, ROOT, slug } = require("./lib");

const only = process.argv.slice(2);
const DIR = path.join(__dirname, "lectures");
const deckName = (lec, id) => `${id}-DAGonStar-${slug(lec.title)}.pptx`;

(async () => {
  const out = path.join(ROOT, "en", "lectures");
  fs.mkdirSync(out, { recursive: true });
  for (const f of fs.readdirSync(DIR).filter((f) => f.endsWith(".js")).sort()) {
    const lec = require(path.join(DIR, f));
    if (only.length && !only.includes(String(lec.n)) && !only.includes(String(lec.n).padStart(2, "0"))) continue;
    const { pres, theme, id } = build(lec);
    const file = path.join(out, deckName(lec, id));
    await pres.writeFile({ fileName: file });
    await applyTheme(file, theme);
    console.log("built", path.relative(ROOT, file));
  }
  if (warnings.length) {
    console.log(`\n${warnings.length} warning(s):`);
    warnings.forEach((w) => console.log("  - " + w));
    process.exitCode = 1;
  }
})();

module.exports = { deckName };
