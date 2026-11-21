// Print the number of slides each lecture source will produce (cover + entries).
// Exits with status 1 when a deck does not have exactly 30 slides.
const fs = require("fs"), path = require("path");
const dir = path.join(__dirname, "lectures");
let wrong = 0;
for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".js")).sort()) {
  const lec = require(path.join(dir, f));
  const n = lec.slides.length + 1;
  if (n !== 30) wrong++;
  if (n !== 30 || process.argv.includes("-a")) console.log(f, n);
}
if (wrong) {
  console.error(`${wrong} deck(s) without exactly 30 slides`);
  process.exit(1);
}
