// Shared deck builder: theme, layouts and slide kinds of the DAGonStar in Practice decks.
// Each lecture file in ./lectures exports { n, part, title, subtitle, slides: [...] };
// every entry of `slides` is { k: <kind>, ... } and is rendered by KINDS[k] below.
// Code excerpts ("code") are read from the files in ../examples; recorded outputs ("out")
// from ../examples/<folder>/output/<script>.txt, written by tools/run_examples.py --record.
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");
const JSZip = require("jszip");

const ROOT = path.join(__dirname, "..");
const EXAMPLES = path.join(ROOT, "examples");
const COURSE = "DAGonStar in Practice";
const TEACHER = "Prof. Raffaele Montella, Ph.D.";
const AFFILIATION = "University of Naples “Parthenope”";
const SLIDES_PER_LECTURE = 30;
const LICENCE = "CC0 1.0";
const AUTHOR = "Raffaele Montella";
const YEAR = "A.Y. 2026/2027";
const PROGRAMME = "Scientific workflow engineering for AI–HPC";
const PART_NAMES = {
  1: "Foundations of scientific workflows",
  2: "Execution, data and recovery",
  3: "Task models for AI–HPC",
  4: "Infrastructure, FAIR and applications",
  A: "Appendix",
};
const PARTS = {
  1: { accent: "14508C", tint: "DCE8F5" },
  2: { accent: "0E7C7B", tint: "DDF0EF" },
  3: { accent: "7A3E9D", tint: "EEE3F5" },
  4: { accent: "B4532A", tint: "F8E6DC" },
  A: { accent: "3D5A3D", tint: "E3EFE3" },
};
// Colours of task types in DAG diagrams.
const TYPE_COLOURS = {
  batch: "14508C", slurm: "B4532A", native: "0E7C7B", web: "7A3E9D", llm: "9C2F6B",
  faas: "C08A00", iot: "2E7D32", agentic: "5B3F9E", docker: "1F5FA8", apptainer: "6D4C41",
  kubernetes: "326CE5", nomad: "00A36C", cloud: "4A6572", checkpoint: "62677F", data: "8A8F99",
  meta: "8E5B00", volume: "00796B",
  state: "62677F", finished: "2E7D32", failed: "B3261E", reused: "8A8F99",
};

function theme(part) {
  return {
    name: `${COURSE} - Part ${part}`,
    headFontFace: "Cambria",
    bodyFontFace: "Calibri",
    colors: {
      dk1: "14172B", lt1: "FFFFFF", dk2: "2B2F4A", lt2: "F1F3F8",
      accent1: PARTS[part].accent, accent2: "E0A526", accent3: "9FB3C8",
      accent4: "62677F", accent5: PARTS[part].tint, accent6: "2E8B57",
      hlink: PARTS[part].accent, folHlink: "62677F",
    },
  };
}

const MONO = "Courier New";
const W = 10, M = 0.5, TOP = 1.3, BOTTOM = 5.0, CW = W - 2 * M, CH = BOTTOM - TOP;
const MONO_W = 0.602; // Courier New glyph width, in em
const warnings = [];

// ---- text fitting -------------------------------------------------------------------------
const CHAR = 0.0069; // average Calibri glyph width, inches per point
const linesOf = (text, pt, w) => Math.max(1, Math.ceil((String(text).length * pt * CHAR) / w));
const lineH = (pt) => (pt * 1.2) / 72;
const plain = (t) => String(t).replace("|", " ");
function listHeight(items, pt, w, gapPt) {
  return items.reduce((h, t) => h + linesOf(plain(t), pt, w - 0.3) * lineH(pt) + gapPt / 72, 0);
}
function fitList(items, w, h, max, min, gapPt, where) {
  for (let pt = max; pt >= min; pt--) if (listHeight(items, pt, w, gapPt) <= h) return pt;
  warnings.push(`${where}: list does not fit at ${min}pt`);
  return min;
}
function fitText(text, w, h, max, min, where) {
  for (let pt = max; pt >= min; pt--) if (linesOf(text, pt, w) * lineH(pt) <= h) return pt;
  warnings.push(`${where}: text does not fit at ${min}pt: "${String(text).slice(0, 40)}..."`);
  return min;
}
// Hard-wrap monospaced lines at `cols` columns; continuation lines start with two spaces.
function wrapMono(lines, cols) {
  const out = [];
  for (const line of lines) {
    if (line.length <= cols) { out.push(line); continue; }
    let rest = line;
    out.push(rest.slice(0, cols)); rest = rest.slice(cols);
    while (rest.length) { out.push("  " + rest.slice(0, cols - 2)); rest = rest.slice(cols - 2); }
  }
  return out;
}

// "Lead|rest" renders the lead in bold.
function runs(t, opts = {}) {
  const s = String(t);
  const i = s.indexOf("|");
  if (i < 0) return [{ text: s, options: { ...opts } }];
  return [
    { text: s.slice(0, i), options: { ...opts, bold: true, breakLine: false } },
    { text: " " + s.slice(i + 1), options: { ...opts } },
  ];
}
function bulletRuns(items, opts = {}) {
  const out = [];
  items.forEach((t, idx) => {
    const r = runs(t);
    r[0].options = { ...r[0].options, bullet: opts.number ? { type: "number" } : true };
    r[r.length - 1].options.breakLine = idx < items.length - 1;
    out.push(...r);
  });
  return out;
}

// ---- excerpts -----------------------------------------------------------------------------
// The lines of an example file between the `from` and `to` markers (substrings), dedented.
function excerptLines(file, d, where) {
  let lines = fs.readFileSync(file, "utf8").replace(/\t/g, "    ").split("\n");
  let from = 0;
  if (d.from) {
    from = lines.findIndex((l) => l.includes(d.from));
    if (from < 0) { warnings.push(`${where}: marker "${d.from}" not in ${path.relative(ROOT, file)}`); from = 0; }
  }
  let to = d.len ? from + d.len : lines.length;
  if (d.to) {
    const j = lines.findIndex((l, i) => i >= from && l.includes(d.to));
    if (j < 0) warnings.push(`${where}: end marker "${d.to}" not in ${path.relative(ROOT, file)}`); else to = j + 1;
  }
  lines = lines.slice(from, to);
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  const nonEmpty = lines.filter((l) => l.trim());
  const indent = nonEmpty.length ? Math.min(...nonEmpty.map((l) => l.match(/^ */)[0].length)) : 0;
  return lines.map((l) => l.slice(indent));
}
const outputFile = (src) => {
  const [folder, script] = src.split("/");
  return path.join(EXAMPLES, folder, "output", `${script}.txt`);
};

// ---- deck ---------------------------------------------------------------------------------
function build(lec) {
  const pres = new PptxGenJS();
  const T = theme(lec.part);
  const C = pres.SchemeColor;
  const id = typeof lec.n === "number" ? String(lec.n).padStart(2, "0") : String(lec.n);
  const isAppendix = lec.part === "A";
  pres.layout = "LAYOUT_16x9";
  pres.theme = { headFontFace: T.headFontFace, bodyFontFace: T.bodyFontFace };
  pres.author = TEACHER;
  pres.company = COURSE;
  pres.title = `${COURSE} ${id} - ${lec.title}`;
  pres.subject = `${COURSE}: ${PROGRAMME}, ${YEAR}. Released under ${LICENCE}.`;

  const footer = `${COURSE}  ·  ${isAppendix ? "Appendix" : "Lecture"} ${id} ${lec.title}  ·  ${AUTHOR}  ·  ${LICENCE}`;
  const titleOpts = (color) => ({
    name: "title", type: "title", x: M, y: 0.32, w: 7.3, h: 0.8, margin: 0,
    fontSize: 30, bold: true, color, align: "left", valign: "middle",
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    objects: [
      { placeholder: { options: titleOpts(C.text1), text: "" } },
      { text: { text: footer, options: { x: M, y: 5.2, w: 8.2, h: 0.3, margin: 0, fontSize: 9, color: C.accent4 } } },
    ],
    slideNumber: { x: 8.9, y: 5.2, w: 0.6, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
  });
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { ...titleOpts(C.background1), y: 1.75, w: 9, h: 1.3, fontSize: 40, valign: "top" }, text: "" } },
      { text: { text: footer, options: { x: M, y: 5.2, w: 8.2, h: 0.3, margin: 0, fontSize: 9, color: C.accent3 } } },
    ],
    slideNumber: { x: 8.9, y: 5.2, w: 0.6, h: 0.3, fontSize: 10, color: C.accent3, align: "right" },
  });

  let section = null;
  let count = 0;
  const where = () => `L${id} slide ${count}`;

  function add(master, title, tag) {
    count++;
    const s = pres.addSlide({ masterName: master, sectionTitle: section });
    if (title) {
      const max = master === "DARK" ? 46 : tag ? 30 : 36;
      if (title.length > max + 10) warnings.push(`${where()}: title too long (${title.length}): ${title}`);
      const o = { placeholder: "title" };
      if (title.length > max) o.fontSize = master === "DARK" ? 32 : 24;
      s.addText(title, { ...o, lang: "en-GB" });
    }
    if (tag) {
      s.addText(`<${tag}/>`, {
        x: 7.9, y: 0.54, w: 1.6, h: 0.36, isTextBox: true, margin: 0, objectName: "Kind tag",
        shape: pres.ShapeType.roundRect, rectRadius: 0.18, fill: { color: C.accent5 },
        fontFace: MONO, fontSize: 12, bold: true, color: C.accent1, align: "center", valign: "middle",
      });
    }
    return s;
  }
  const text = (s, t, o) => s.addText(t, { isTextBox: true, margin: 0, valign: "top", lang: "en-GB", ...o });
  const card = (s, x, y, w, h, color, name) =>
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color }, objectName: name || "Card" });
  const badge = (s, label, x, y, color, d = 0.4) =>
    s.addText(String(label), {
      x, y, w: d, h: d, isTextBox: true, margin: 0, shape: pres.ShapeType.ellipse, fill: { color },
      fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", objectName: "Badge",
    });
  function bullets(s, items, x, y, w, h, o = {}) {
    const gap = o.gap ?? 8;
    const pt = fitList(items, w, h, o.max ?? 18, o.min ?? 12, gap, where());
    text(s, bulletRuns(items, o), { x, y, w, h, fontSize: pt, color: o.color ?? C.text1, paraSpaceAfter: gap });
  }
  function numbered(s, items, x, y, w, h, color, o = {}) {
    const rowH = Math.min(0.95, h / items.length);
    const tw = w - 0.6;
    items.forEach((t, i) => {
      const ry = y + i * rowH;
      badge(s, o.labels ? o.labels[i] : i + 1, x, ry + 0.02, color);
      const pt = fitText(plain(t), tw, rowH - 0.06, o.max ?? 16, o.min ?? 12, where());
      text(s, runs(t), { x: x + 0.6, y: ry, w: tw, h: rowH - 0.04, fontSize: pt, color: o.color ?? C.text1, valign: "top" });
    });
  }
  function note(s, t, y, h) {
    card(s, M, y, CW, h, C.accent5, "Note");
    const pt = fitText(plain(t), CW - 0.5, h - 0.1, 15, 12, where());
    text(s, runs(t), { x: M + 0.25, y, w: CW - 0.5, h, fontSize: pt, color: C.text1, valign: "middle" });
  }
  // A dark terminal-like panel with monospaced lines; returns nothing.
  function monoPanel(s, label, lines, x, y, w, h, o = {}) {
    const pad = 0.2, tabH = 0.34;
    const iw = w - 2 * pad, ih = h - tabH - 0.16;
    let pt = 15, shown = lines;
    for (; pt >= 9; pt -= 0.5) {
      const cols = Math.floor(iw / ((pt * MONO_W) / 72));
      shown = o.wrap ? wrapMono(lines, cols) : lines;
      const longest = Math.max(...shown.map((l) => l.length), 1);
      const fitsW = longest <= cols;
      const fitsH = shown.length * ((pt * 1.19) / 72) <= ih;
      if (fitsW && fitsH) break;
    }
    if (pt < 9) { warnings.push(`${where()}: ${o.kind || "code"} too big (${lines.length} lines) ${label}`); pt = 9; }
    card(s, x, y, w, h, o.bg || C.text1, o.name || "Code panel");
    text(s, label, { x: x + pad, y: y + 0.08, w: iw, h: tabH - 0.08, fontFace: MONO, fontSize: 10, color: C.accent3, valign: "middle" });
    const isComment = (l) => /^\s*(\/\/|#(?!!)|;|<!--|\/\*|\*\s|--\s)/.test(l);
    text(s, shown.map((l, i) => ({ text: l || " ", options: {
      color: o.kind === "out" ? (i === 0 && o.prompt ? C.accent2 : "D7E3EE") : isComment(l) ? C.accent2 : C.background1,
      breakLine: i < shown.length - 1 } })),
    { x: x + pad, y: y + tabH + 0.08, w: iw, h: ih, fontFace: MONO, fontSize: pt, objectName: o.kind === "out" ? "Output" : "Code" });
  }

  const KINDS = {
    cover() {
      section = "Opening";
      pres.addSection({ title: section });
      const s = add("DARK", lec.title);
      text(s, isAppendix ? `<appendix id="${id}">` : `<lecture n="${id}" part="${lec.part}">`, { x: M, y: 0.9, w: 9, h: 0.4, fontFace: MONO, fontSize: 16, bold: true, color: C.accent2 });
      text(s, lec.subtitle, { x: M, y: 3.05, w: 8.4, h: 0.8, fontSize: 18, color: C.accent3 });
      text(s, [
        { text: TEACHER, options: { bold: true, color: C.background1, breakLine: true } },
        { text: AFFILIATION, options: { color: C.accent3 } },
      ], { x: M, y: 4.15, w: 4.1, h: 0.7, fontSize: 14 });
      text(s, [
        { text: isAppendix ? PART_NAMES.A : `Part ${lec.part} · ${PART_NAMES[lec.part]}`, options: { bold: true, color: C.accent2, breakLine: true } },
        { text: `${COURSE} · ${YEAR}`, options: { color: C.accent3 } },
      ], { x: 4.6, y: 4.15, w: 4.9, h: 0.7, fontSize: 13, align: "right" });
    },

    agenda(d) {
      const s = add("CONTENT", d.t || "Today's lecture", "agenda");
      numbered(s, d.items, M, TOP, 5.2, CH, C.accent1, { max: 17 });
      card(s, 6.1, TOP, 3.4, CH, C.accent5, "Goals card");
      text(s, "After this lecture you can", { x: 6.35, y: TOP + 0.2, w: 2.9, h: 0.35, fontSize: 15, bold: true, color: C.accent1 });
      bullets(s, d.goals, 6.35, TOP + 0.7, 2.9, CH - 0.9, { max: 15, min: 12, gap: 10 });
    },

    sec(d) {
      section = d.t;
      pres.addSection({ title: section });
      const s = add("DARK", d.t);
      text(s, `<section n="${d.n || ""}">`, { x: M, y: 0.9, w: 9, h: 0.4, fontFace: MONO, fontSize: 16, bold: true, color: C.accent2 });
      const pt = fitText(d.p, 7.8, 1.5, 18, 13, where());
      text(s, d.p, { x: M, y: 3.1, w: 7.8, h: 1.5, fontSize: pt, color: C.accent3 });
    },

    bul(d) {
      const s = add("CONTENT", d.t, d.tag);
      if (!d.key) return bullets(s, d.b, M, TOP, CW, CH);
      bullets(s, d.b, M, TOP, 5.4, CH);
      card(s, 6.2, TOP, 3.3, CH, C.accent5, "Key idea card");
      let y = TOP + 0.25;
      if (d.key.big) {
        const pt = d.key.big.length > 9 ? 28 : d.key.big.length > 5 ? 38 : 52;
        text(s, d.key.big, { x: 6.45, y, w: 2.8, h: 0.95, fontFace: T.headFontFace, fontSize: pt, bold: true, color: C.accent1, valign: "middle" });
        y += 1.05;
      }
      if (d.key.h) {
        const hh = linesOf(d.key.h, 16, 2.8) * lineH(16) + 0.1;
        text(s, d.key.h, { x: 6.45, y, w: 2.8, h: hh, fontSize: 16, bold: true, color: C.text1 });
        y += hh + 0.05;
      }
      if (d.key.code) {
        const lines = d.key.code.split("\n");
        const longest = Math.max(...lines.map((l) => l.length));
        const pt = Math.min(13, Math.floor((2.8 / longest / MONO_W) * 72 * 2) / 2);
        if (pt < 9) warnings.push(`${where()}: key code too wide (${longest})`);
        const hh = lines.length * lineH(pt) + 0.1;
        text(s, d.key.code, { x: 6.45, y, w: 2.8, h: hh, fontFace: MONO, fontSize: Math.max(pt, 9), bold: true, color: C.text1 });
        y += hh + 0.1;
      }
      if (d.key.p) {
        const pt = fitText(d.key.p, 2.8, TOP + CH - 0.2 - y, 15, 12, where());
        text(s, d.key.p, { x: 6.45, y, w: 2.8, h: TOP + CH - 0.2 - y, fontSize: pt, color: C.text2 });
      }
    },

    cards(d) {
      const s = add("CONTENT", d.t, d.tag);
      const n = d.c.length;
      const cols = n <= 3 ? n : n === 4 ? 2 : 3;
      const rows = Math.ceil(n / cols);
      const gap = 0.25;
      const noteH = d.note ? 0.7 : 0;
      const w = (CW - gap * (cols - 1)) / cols;
      const h = (CH - noteH - gap * (rows - 1) - (d.note ? 0.1 : 0)) / rows;
      d.c.forEach(([head, body], i) => {
        const x = M + (i % cols) * (w + gap);
        const y = TOP + Math.floor(i / cols) * (h + gap);
        card(s, x, y, w, h, C.background2);
        badge(s, i + 1, x + 0.18, y + 0.15, C.accent1, 0.36);
        const hw = w - 0.85;
        const hpt = fitText(head, hw, 0.46, 16, 12, where());
        text(s, head, { x: x + 0.68, y: y + 0.1, w: hw, h: 0.46, fontSize: hpt, bold: true, color: C.text1, valign: "middle" });
        const bh = h - 0.7;
        const pt = fitText(plain(body), w - 0.36, bh, 15, 11, where());
        text(s, runs(body), { x: x + 0.18, y: y + 0.62, w: w - 0.36, h: bh, fontSize: pt, color: C.text2 });
      });
      if (d.note) note(s, d.note, TOP + CH - 0.62, 0.62);
    },

    flow(d) {
      const s = add("CONTENT", d.t, d.tag);
      const n = d.s.length;
      const gap = 0.36;
      const w = (CW - gap * (n - 1)) / n;
      const h = d.note ? 2.45 : CH;
      d.s.forEach(([head, body], i) => {
        const x = M + i * (w + gap);
        card(s, x, TOP, w, h, i % 2 ? C.background2 : C.accent5, "Step");
        text(s, String(i + 1).padStart(2, "0"), { x: x + 0.15, y: TOP + 0.12, w: w - 0.3, h: 0.36, fontFace: MONO, fontSize: 15, bold: true, color: C.accent1 });
        const hpt = n > 5 ? 13 : 15;
        const hl = linesOf(head, hpt, w - 0.3);
        text(s, head, { x: x + 0.15, y: TOP + 0.5, w: w - 0.3, h: hl * lineH(hpt) + 0.05, fontSize: hpt, bold: true, color: C.text1 });
        const by = TOP + 0.6 + hl * lineH(hpt);
        const bh = TOP + h - 0.12 - by;
        const longest = Math.max(...body.split(/[\s/]+/).map((x) => x.length));
        const wordMax = Math.floor((w - 0.3) / (longest * CHAR * 1.1));
        const minPt = n > 4 ? 11 : 12;
        if (wordMax < minPt) warnings.push(`${where()}: word too long for a flow box in "${body}"`);
        const pt = fitText(body, w - 0.3, bh, Math.max(minPt, Math.min(14, wordMax)), minPt, where());
        const headLongest = Math.max(...head.split(/[\s/]+/).map((x) => x.length));
        if (headLongest * hpt * CHAR * 1.1 > w - 0.3) warnings.push(`${where()}: word too long for a flow heading: ${head}`);
        text(s, body, { x: x + 0.15, y: by, w: w - 0.3, h: bh, fontSize: pt, color: C.text2 });
        if (i < n - 1) text(s, "›", { x: x + w, y: TOP + h / 2 - 0.3, w: gap, h: 0.6, fontSize: 26, bold: true, color: C.accent1, align: "center", valign: "middle" });
      });
      if (d.note) note(s, d.note, TOP + 2.7, CH - 2.7);
    },

    cmp(d) {
      const s = add("CONTENT", d.t, d.tag);
      const w = 4.35;
      [[d.l, M, C.accent1], [d.r, M + w + 0.3, C.text2]].forEach(([[head, items], x, color]) => {
        card(s, x, TOP, w, CH, C.background2, "Column");
        text(s, head, {
          x: x + 0.2, y: TOP + 0.2, w: w - 0.4, h: 0.45, margin: 8, shape: pres.ShapeType.roundRect, rectRadius: 0.08,
          fill: { color }, fontSize: 15, bold: true, color: C.background1, valign: "middle",
        });
        bullets(s, items, x + 0.2, TOP + 0.85, w - 0.4, CH - 1.0, { max: 16 });
      });
    },

    tbl(d) {
      const s = add("CONTENT", d.t, d.tag);
      const cols = d.h.length;
      const colW = d.w || Array(cols).fill(CW / cols);
      if (Math.abs(colW.reduce((a, b) => a + b, 0) - CW) > 0.05) warnings.push(`${where()}: table widths sum to ${colW.reduce((a, b) => a + b, 0)}`);
      const noteH = d.note ? 0.72 : 0;
      const avail = CH - noteH;
      let pt = 15, total = 0;
      const width = (c, i, p) => (d.mono && d.mono.includes(i) ? String(c).length * p * MONO_W / 72 / (colW[i] - 0.2) : linesOf(c, p, colW[i] - 0.2));
      for (; pt >= 10; pt--) {
        total = [d.h, ...d.r].reduce((h, row) => h + Math.max(...row.map((c, i) => Math.ceil(Math.max(1, width(c, i, pt))))) * lineH(pt) + 0.13, 0);
        if (total <= avail) break;
      }
      if (pt < 10) { pt = 10; warnings.push(`${where()}: table does not fit`); }
      const cell = (t, o) => ({ text: String(t), options: { fontSize: pt, valign: "middle", margin: [3, 6, 3, 6], lang: "en-GB", ...o } });
      const rows = [d.h.map((t) => cell(t, { bold: true, color: C.background1, fill: { color: C.accent1 } }))];
      d.r.forEach((r, i) => rows.push(r.map((t, j) => cell(t, {
        color: C.text1, bold: j === 0 && !(d.mono && d.mono.includes(0)), fill: { color: i % 2 ? C.background1 : C.background2 },
        fontFace: d.mono && d.mono.includes(j) ? MONO : undefined,
      }))));
      s.addTable(rows, { x: M, y: TOP, w: CW, colW, border: { type: "none" }, objectName: "Table" });
      if (d.note) note(s, d.note, Math.min(TOP + CH - 0.6, TOP + total + 0.2), 0.6);
    },

    stat(d) {
      const s = add("CONTENT", d.t, d.tag);
      const n = d.s.length, gap = 0.3, w = (CW - gap * (n - 1)) / n;
      d.s.forEach(([num, label], i) => {
        const x = M + i * (w + gap);
        card(s, x, TOP, w, 2.45, i === 0 ? C.accent5 : C.background2, "Stat");
        const pt = num.length > 7 ? 30 : num.length > 4 ? 40 : 52;
        text(s, num, { x: x + 0.2, y: TOP + 0.2, w: w - 0.4, h: 1.0, fontFace: T.headFontFace, fontSize: pt, bold: true, color: C.accent1, valign: "middle" });
        const lp = fitText(label, w - 0.4, 1.0, 15, 11, where());
        text(s, label, { x: x + 0.2, y: TOP + 1.3, w: w - 0.4, h: 1.0, fontSize: lp, color: C.text2 });
      });
      if (d.note) note(s, d.note, TOP + 2.7, CH - 2.7);
    },

    // Code read from examples/<src>, between the `from` and `to` markers.
    code(d) {
      const s = add("CONTENT", d.t, d.tag || "code");
      let lines, label = d.f || "";
      if (d.src) {
        const file = path.join(EXAMPLES, d.src);
        label = `examples/${d.src}`;
        if (!fs.existsSync(file)) { warnings.push(`${where()}: missing example ${d.src}`); lines = [`missing: ${d.src}`]; }
        else lines = excerptLines(file, d, where());
      } else lines = d.c.replace(/\n+$/, "").split("\n");
      const wide = !d.n || d.wide;
      const w = wide ? CW : 6.3;
      const notesH = d.n && d.wide ? Math.ceil(d.n.length / 2) * 0.36 + 0.1 : 0;
      const PH = CH - (notesH ? notesH + 0.15 : 0);
      monoPanel(s, label, lines, M, TOP, w, PH);
      if (d.n && d.wide) {
        const half = Math.ceil(d.n.length / 2);
        [d.n.slice(0, half), d.n.slice(half)].forEach((col, i) => {
          if (col.length) bullets(s, col, M + i * 4.6, TOP + PH + 0.15, 4.4, notesH, { max: 13, min: 11, gap: 4 });
        });
      } else if (d.n) bullets(s, d.n, 7.0, TOP + 0.05, 2.5, CH - 0.1, { max: 15, min: 11, gap: 10 });
    },

    // The recorded standard output of an example: examples/<folder>/output/<script>.txt.
    out(d) {
      const s = add("CONTENT", d.t, d.tag || "output");
      const file = outputFile(d.src);
      let lines;
      if (!fs.existsSync(file)) { warnings.push(`${where()}: missing output ${d.src}`); lines = ["(no recorded output)"]; }
      else lines = excerptLines(file, d, where());
      const prompt = `$ python examples/${d.src}.py`;
      const w = d.n ? 6.3 : CW;
      monoPanel(s, "terminal", [prompt, ...lines], M, TOP, w, CH, { kind: "out", wrap: true, prompt: true, bg: "1B2233" });
      if (d.n) bullets(s, d.n, 7.0, TOP + 0.05, 2.5, CH - 0.1, { max: 15, min: 11, gap: 10 });
    },

    // A workflow graph: nodes [id, label, layer, type], edges [from, to, "data"|"ctrl"].
    dag(d) {
      const s = add("CONTENT", d.t, d.tag || "dag");
      const areaW = d.n ? 6.3 : CW;
      const noteH = d.note ? 0.65 : 0;
      const areaH = CH - noteH - (d.note ? 0.12 : 0) - 0.3;
      const layers = Math.max(...d.nodes.map((x) => x[2])) + 1;
      const colW = areaW / layers;
      const bw = Math.min(1.75, colW - 0.38), bh = 0.46;
      const pos = {};
      for (let L = 0; L < layers; L++) {
        const inLayer = d.nodes.filter((x) => x[2] === L);
        const gapY = areaH / inLayer.length;
        inLayer.forEach((nd, i) => {
          pos[nd[0]] = { x: M + L * colW + (colW - bw) / 2, y: TOP + i * gapY + (gapY - bh) / 2, nd };
        });
      }
      for (const [a, b, kind] of d.edges) {
        if (!pos[a] || !pos[b]) { warnings.push(`${where()}: edge ${a}->${b} has an unknown node`); continue; }
        const x1 = pos[a].x + bw, y1 = pos[a].y + bh / 2, x2 = pos[b].x, y2 = pos[b].y + bh / 2;
        s.addShape(pres.ShapeType.line, {
          x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.01), h: Math.max(Math.abs(y2 - y1), 0.001),
          flipV: y2 < y1, flipH: x2 < x1,
          line: { color: kind === "ctrl" ? "62677F" : "14172B", width: kind === "ctrl" ? 1.25 : 1.75, dashType: kind === "ctrl" ? "dash" : "solid", endArrowType: "triangle" },
          objectName: "Edge",
        });
      }
      for (const { x, y, nd } of Object.values(pos)) {
        const [, label, , type] = nd;
        const colour = TYPE_COLOURS[type || "batch"] || TYPE_COLOURS.batch;
        const pt = fitText(label, bw - 0.1, bh - 0.04, 12, 9, where());
        s.addText(label, { x, y, w: bw, h: bh, shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: type === "data" ? "FFFFFF" : colour },
          line: { color: colour, width: 1.25 }, fontFace: MONO, fontSize: pt, bold: true, color: type === "data" ? colour : "FFFFFF", align: "center", valign: "middle", margin: 2, objectName: "Node" });
      }
      const types = [...new Set(d.nodes.map((x) => x[3] || "batch"))].filter((t) => t !== "data");
      const legend = [{ text: "solid: data (workflow://)   dashed: control   ", options: { color: C.accent4 } },
        ...types.map((t, i) => ({ text: (i ? "  " : "") + "■ " + t, options: { color: TYPE_COLOURS[t] || TYPE_COLOURS.batch } }))];
      text(s, legend, { x: M, y: TOP + areaH + 0.02, w: areaW, h: 0.26, fontSize: 10 });
      if (d.n) bullets(s, d.n, 7.0, TOP + 0.05, 2.5, CH - 0.1, { max: 15, min: 11, gap: 10 });
      if (d.note) note(s, d.note, TOP + CH - noteH, noteH);
    },

    demo(d) {
      const s = add("CONTENT", d.t, "demo");
      numbered(s, d.steps, M, TOP, 5.3, CH, C.accent6);
      card(s, 6.1, TOP, 3.4, CH, C.text1, "Demo panel");
      text(s, "RUN IT", { x: 6.3, y: TOP + 0.2, w: 3.0, h: 0.3, fontSize: 12, bold: true, color: C.accent2, charSpacing: 2 });
      const run = d.run.split("\n");
      const longest = Math.max(...run.map((l) => l.length));
      const rpt = Math.min(12, Math.floor((3.0 / longest / MONO_W) * 72 * 2) / 2);
      if (rpt < 9) warnings.push(`${where()}: demo run line too long (${longest})`);
      const rh = run.length * lineH(Math.max(rpt, 9)) + 0.1;
      text(s, d.run, { x: 6.3, y: TOP + 0.55, w: 3.0, h: rh, fontFace: MONO, fontSize: Math.max(rpt, 9), color: C.background1 });
      const wy = TOP + 0.75 + rh;
      text(s, "WATCH FOR", { x: 6.3, y: wy, w: 3.0, h: 0.3, fontSize: 12, bold: true, color: C.accent2, charSpacing: 2 });
      const wh = TOP + CH - 0.15 - (wy + 0.35);
      const pt = fitText(d.watch, 3.0, wh, 15, 11, where());
      text(s, d.watch, { x: 6.3, y: wy + 0.35, w: 3.0, h: wh, fontSize: pt, color: C.background1 });
      s.addNotes(`Live example. ${d.run.replace(/\n/g, " ; ")}. Watch for: ${d.watch}`);
    },

    ex(d) {
      const s = add("CONTENT", d.t, d.tag || "exercise");
      numbered(s, d.tasks, M, TOP, 5.3, CH, C.accent1, { labels: d.tasks.map((_, i) => String.fromCharCode(65 + i)) });
      card(s, 6.1, TOP, 3.4, CH, C.accent5, "Deliverable card");
      text(s, d.h || "Deliverable", { x: 6.35, y: TOP + 0.2, w: 2.9, h: 0.35, fontSize: 15, bold: true, color: C.accent1 });
      const pt = fitText(d.p, 2.9, CH - 0.9, 15, 12, where());
      text(s, d.p, { x: 6.35, y: TOP + 0.65, w: 2.9, h: CH - 0.9, fontSize: pt, color: C.text2 });
    },

    // Review questions; the answers go to the speaker notes.
    q(d) {
      const s = add("CONTENT", d.t || "Check your understanding", "quiz");
      numbered(s, d.qs, M, TOP, CW, CH, C.accent2, { max: 16, min: 12 });
      if (d.a) s.addNotes("Answers. " + d.a.map((a, i) => `${i + 1}) ${a}`).join(" "));
    },

    recap(d) {
      section = "Wrap-up";
      pres.addSection({ title: section });
      const s = add("DARK");
      text(s, "Key takeaways", { x: M, y: 0.4, w: 9, h: 0.7, fontFace: T.headFontFace, fontSize: 32, bold: true, color: C.background1, valign: "middle" });
      numbered(s, d.pts, M, 1.35, 9, 2.9, C.accent1, { color: C.background1, min: 12 });
      text(s, [
        { text: isAppendix ? "</appendix>  " : "</lecture>  ", options: { fontFace: MONO, bold: true, color: C.accent2 } },
        { text: d.next, options: { color: C.accent3 } },
      ], { x: M, y: 4.45, w: 9, h: 0.5, fontSize: 15, valign: "middle" });
    },
  };

  KINDS.cover();
  section = "Lecture";
  let opened = false;
  for (const d of lec.slides) {
    if (!KINDS[d.k]) throw new Error(`L${id}: unknown slide kind ${d.k}`);
    if (!opened && d.k !== "sec" && d.k !== "agenda") { pres.addSection({ title: section }); opened = true; }
    if (d.k === "agenda") section = "Opening";
    else if (d.k === "sec") opened = true;
    KINDS[d.k](d);
    if (d.k === "agenda") section = "Lecture";
    if (d.no) pres.slides[pres.slides.length - 1].addNotes(d.no);
  }
  if (count !== SLIDES_PER_LECTURE) warnings.push(`L${id}: ${count} slides instead of ${SLIDES_PER_LECTURE}`);
  return { pres, theme: T, id };
}

// pptxgenjs cannot write theme colors, so they are patched into ppt/theme/theme1.xml.
async function applyTheme(file, T) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const p = "ppt/theme/theme1.xml";
  let xml = await zip.file(p).async("string");
  for (const [slot, hex] of Object.entries(T.colors)) {
    xml = xml.replace(new RegExp(`<a:${slot}>.*?</a:${slot}>`, "s"), `<a:${slot}><a:srgbClr val="${hex}"/></a:${slot}>`);
  }
  xml = xml.replace(/<a:theme ([^>]*)name="[^"]*"/, `<a:theme $1name="${T.name}"`);
  zip.file(p, xml);
  // Repack for PowerPoint and cloud viewers: [Content_Types].xml first, no folder entries
  // (OneDrive, SharePoint and PowerPoint Online can refuse packages that contain them).
  const out = new JSZip();
  const names = Object.keys(zip.files).filter((n) => !zip.files[n].dir);
  names.sort((a, b) => (a === "[Content_Types].xml" ? -1 : b === "[Content_Types].xml" ? 1 : 0));
  for (const n of names) out.file(n, await zip.file(n).async("nodebuffer"), { createFolders: false });
  fs.writeFileSync(file, await out.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

const slug = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "");

module.exports = { build, applyTheme, warnings, ROOT, COURSE, PART_NAMES, slug, excerptLines, outputFile, SLIDES_PER_LECTURE };
