// Print the number of slides each lecture source will produce (cover + entries).
const fs = require("fs"), path = require("path");
const dir = path.join(__dirname, "lectures");
for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".js")).sort()) {
  const lec = require(path.join(dir, f));
  const n = lec.slides.length + 1;
  if (n !== 30 || process.argv.includes("-a")) console.log(f, n);
}
