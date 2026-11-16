// Write the lecture notes in Markdown: `node notes.js` -> ../en/notes/NN-Title.md and README.md.
// The notes come from the same sources as the slides, with the same code excerpts and the
// same recorded outputs, so slides, notes and examples never diverge.
const fs = require("fs");
const path = require("path");
const { ROOT, COURSE, PART_NAMES, slug, excerptLines, outputFile } = require("./lib");

const DIR = path.join(__dirname, "lectures");
const OUT = path.join(ROOT, "en", "notes");
const EX = path.join(ROOT, "examples");
const LANG = { ".py": "python", ".sh": "bash", ".ini": "ini", ".json": "json", ".csv": "text", ".cwl": "yaml", ".txt": "text" };

const md = (t) => { const s = String(t); const i = s.indexOf("|"); return i < 0 ? s : `**${s.slice(0, i)}** ${s.slice(i + 1)}`; };
const list = (items) => items.map((t) => `- ${md(t)}`).join("\n");
const cell = (t) => String(t).replace(/\|/g, "\\|");
const fence = (code, lang = "") => `\`\`\`${lang}\n${code}\n\`\`\``;
const noteOf = (d) => (d.note ? `\n\n> ${md(d.note)}` : "");
const KINDS = {
  agenda: (d) => `**Outline**\n\n${d.items.map((t, i) => `${i + 1}. ${md(t)}`).join("\n")}\n\n**After this lecture you can**\n\n${list(d.goals)}`,
  sec: (d) => `*${d.p}*`,
  bul(d) {
    let out = list(d.b);
    if (d.key) {
      const k = [d.key.big && `**${d.key.big}**`, d.key.h && `*${d.key.h}*`].filter(Boolean).join(" - ");
      out += `\n\n> ${k}${k && d.key.p ? "\n>\n> " : ""}${d.key.p || ""}`;
      if (d.key.code) out += `\n\n${fence(d.key.code)}`;
    }
    return out;
  },
  cards: (d) => d.c.map(([h, b]) => `- **${h}** - ${md(b)}`).join("\n") + noteOf(d),
  flow: (d) => d.s.map(([h, b], i) => `${i + 1}. **${h}** - ${b}`).join("\n") + noteOf(d),
  cmp: (d) => [d.l, d.r].map(([h, items]) => `**${h}**\n\n${list(items)}`).join("\n\n"),
  tbl: (d) => [`| ${d.h.map(cell).join(" | ")} |`, `|${d.h.map(() => "---").join("|")}|`,
    ...d.r.map((r) => `| ${r.map((c, j) => (d.mono && d.mono.includes(j) ? `\`${cell(c)}\`` : cell(c))).join(" | ")} |`)].join("\n") + noteOf(d),
  stat: (d) => d.s.map(([n, l]) => `- **${n}** - ${l}`).join("\n") + noteOf(d),
  code(d) {
    if (!d.src) return fence(d.c.replace(/\n+$/, "")) + (d.n ? `\n\n${list(d.n)}` : "");
    const code = excerptLines(path.join(EX, d.src), d, "notes").join("\n");
    return `[\`examples/${d.src}\`](../../examples/${d.src})\n\n${fence(code, LANG[path.extname(d.src)] || "")}` + (d.n ? `\n\n${list(d.n)}` : "");
  },
  out(d) {
    const code = excerptLines(outputFile(d.src), d, "notes").join("\n");
    return `Recorded output of \`python examples/${d.src}.py\`:\n\n${fence(code, "text")}` + (d.n ? `\n\n${list(d.n)}` : "");
  },
  dag(d) {
    const label = Object.fromEntries(d.nodes.map((n) => [n[0], n[1]]));
    const lines = ["flowchart LR", ...d.nodes.map(([id, l, , type]) => `  ${id}["${l}${type && type !== "batch" ? ` (${type})` : ""}"]`),
      ...d.edges.map(([a, b, k]) => `  ${a} ${k === "ctrl" ? "-.->" : "-->"} ${b}`)];
    void label;
    return fence(lines.join("\n"), "mermaid") + "\n\nSolid arrows: data dependencies (`workflow://`); dotted arrows: control dependencies." +
      (d.n ? `\n\n${list(d.n)}` : "") + noteOf(d);
  },
  demo: (d) => `**Steps**\n\n${d.steps.map((t, i) => `${i + 1}. ${md(t)}`).join("\n")}\n\n**Run it**\n\n${fence(d.run, "bash")}\n\n**Watch for:** ${d.watch}`,
  ex: (d) => `${d.tasks.map((t, i) => `${String.fromCharCode(65 + i)}. ${md(t)}`).join("\n")}\n\n**${d.h || "Deliverable"}:** ${d.p}`,
  q: (d) => d.qs.map((t, i) => `${i + 1}. ${md(t)}`).join("\n") +
    (d.a ? `\n\n<details><summary>Answers</summary>\n\n${d.a.map((a, i) => `${i + 1}. ${a}`).join("\n")}\n\n</details>` : ""),
  recap: (d) => `${d.pts.map((t, i) => `${i + 1}. ${md(t)}`).join("\n")}\n\n*${d.next}*`,
};
const TITLES = { agenda: "Today's lecture", recap: "Key takeaways", q: "Check your understanding" };

fs.mkdirSync(OUT, { recursive: true });
const index = [];
for (const f of fs.readdirSync(DIR).filter((f) => f.endsWith(".js")).sort()) {
  const lec = require(path.join(DIR, f));
  const id = typeof lec.n === "number" ? String(lec.n).padStart(2, "0") : String(lec.n);
  const name = `${id}-${slug(lec.title)}.md`;
  const deck = `${id}-DAGonStar-${slug(lec.title)}.pptx`;
  const folders = fs.readdirSync(EX).filter((x) => x.startsWith(id + "-"));
  const out = [`# ${id}. ${lec.title}`, "", `*${lec.subtitle}*`, "",
    `${COURSE} - ${lec.part === "A" ? "Appendix" : `Part ${lec.part}: ${PART_NAMES[lec.part]}`}. ` +
    `Slides: [${deck}](../lectures/${deck}).` + folders.map((x) => ` Examples: [examples/${x}](../../examples/${x}/).`).join(""), ""];
  lec.slides.forEach((d, i) => out.push(`## ${i + 2}. ${d.t || TITLES[d.k] || ""}`, "", KINDS[d.k](d), ""));
  out.push("---", "", `Raffaele Montella. CC0 1.0. Generated from \`src/lectures/${f}\`.`, "");
  fs.writeFileSync(path.join(OUT, name), out.join("\n"));
  index.push(`| ${id} | [${lec.title}](${name}) | ${lec.part} |`);
}
fs.writeFileSync(path.join(OUT, "README.md"), ["# Lecture notes", "",
  "One Markdown file per lecture, slide by slide, generated from the same sources as the decks in `../lectures`.",
  "Code excerpts are read from `examples/`; outputs are those recorded by `tools/run_examples.py --record`.", "",
  "| # | Lecture | Part |", "|---|---------|------|", ...index, "",
  "Regenerate with `cd src && node notes.js`.", ""].join("\n"));
console.log(`wrote ${index.length} notes in en/notes`);
