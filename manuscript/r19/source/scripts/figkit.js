// Shared drawing kit for the paper's figures. Every figure is one PowerPoint slide of exactly its
// printed size, so a font size on the slide is the size in the paper. Shapes are native and editable:
// arrows are line shapes with small triangle heads (drawn as shapes, so every renderer shows the same size),
// curves and polylines are freeform shapes, and charts are drawn from the CSV files in data/ (rerun the
// scripts after changing the data).
//
// Used by make_diagrams_pptx.js (Fig. 1) and make_charts_pptx.js (Figs. 2-6).

const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const FONT = "Calibri";          // preserve the font requested by the supplied PowerPoint source

// Palette preserved from the supplied r14 drawing source.
const P = {
  ink: "000000", ink2: "404040", ink3: "595959", muted: "7F7F7F", rule: "A6A6A6", hair: "D9D9D9",
  grid: "E4E4E4", shade: "F2F2F2", white: "FFFFFF",
  // architecture layers
  appDark: "C55A11", app: "ED7D31", appCard: "F8CBAD", runtime: "5B9BD5", blue: "4472C4", gpu: "70AD47",
  sqC: "70AD47", sqM: "FFC000",
  // green = reads the shared source, blue = private work
  read: "A9D18E", readEdge: "548235", priv: "9DC3E6", privEdge: "2E75B6", blockEdge: "404040",
  pubK: "FFE699", pubK1: "F8CBAD",
  // timeline highlights
  hilite: "FFF2CC", hiliteEdge: "7F6000",
  // policies (charts)
  bim: "4472C4", bimDark: "2F5597", bimLight: "BDD7EE",
  manual: "ED7D31", manualDark: "C55A11", manualLight: "FBE5D6",
  full: "7F7F7F", fullDark: "404040", fullLight: "D9D9D9",
  clone: "8064A2", cloneDark: "5F4B8B", cloneLight: "E4DFEC",   // purple: green means "reads the source" in Figs. 1-3
  bad: "C00000",
};

const iconCache = new Map();
async function iconPng(Comp, color) {
  const key = Comp.name + color;
  if (!iconCache.has(key)) {
    if (color !== P.ink) throw new Error("The reference icons are black.");
    const files = { TbZoomCode: "analysis-icon.png", PiGraphicsCardBold: "gpu-icon.png" };
    const buf = fs.readFileSync(path.join(ROOT, "assets", files[Comp.name]));
    iconCache.set(key, "image/png;base64," + buf.toString("base64"));
  }
  return iconCache.get(key);
}

// CSV reader: skips '#' comment lines, returns an array of objects keyed by the header
function readCsv(name) {
  const lines = fs.readFileSync(path.join(ROOT, "data", name), "utf8").split(/\r?\n/)
    .filter((l) => l.trim() && !l.startsWith("#"));
  const head = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const v = l.split(",");
    const o = {};
    head.forEach((h, i) => { o[h] = v[i] === undefined ? "" : v[i]; });
    return o;
  });
}
// width (in) of a text line in Calibri (metrics of Carlito, which has the same advance widths)
const WIDTHS = JSON.parse(fs.readFileSync(path.join(__dirname, "calibri_widths.json"), "utf8"));
function tw(text, size, style = "regular") {
  const t = WIDTHS[style] || WIDTHS.regular;
  let em = 0;
  for (const ch of String(text)) em += t[ch] !== undefined ? t[ch] : 0.5;
  return em * size / 72;
}
const num = (v) => (v === "" || v === undefined || v === null ? NaN : Number(v));

// ---------------------------------------------------------------------------------------------
// drawing kit
// ---------------------------------------------------------------------------------------------
function kit(pres, slide, ops) {
  const T = (text, o = {}) => slide.addText(text, Object.assign({
    fontFace: FONT, fontSize: 7, color: P.ink, margin: 0, isTextBox: true, valign: "middle", wrap: false,
  }, o));
  const R = (o) => slide.addShape(o.radius ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.RECTANGLE, Object.assign({
    fill: o.fill === null || o.fill === undefined ? { type: "none" } : { color: o.fill },
    line: o.line ? o.line : { type: "none" },
  }, o.radius ? { rectRadius: o.radius } : {}, { x: o.x, y: o.y, w: o.w, h: o.h }, o.name ? { objectName: o.name } : {}));
  // plain line
  const L = (x1, y1, x2, y2, o = {}) => slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: Object.assign({ color: o.color || P.ink, width: o.width || 0.75 }, o.dash ? { dashType: o.dash } : {}),
  });
  // arrowhead: a filled triangle with its tip at (x2, y2), pointing along (ux, uy). Drawn as a shape rather
  // than an OOXML line end, because PowerPoint and LibreOffice size line ends differently for thin lines.
  const head = (x2, y2, ux, uy, o = {}) => {
    const w0 = o.width || 0.75;
    const hl = o.hl || (w0 >= 1.25 ? 0.075 : 0.055), hw = o.hw || (w0 >= 1.25 ? 0.075 : 0.05);
    const ang = Math.atan2(uy, ux) * 180 / Math.PI + 90, cx = x2 - ux * hl / 2, cy = y2 - uy * hl / 2;
    slide.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: cx - hw / 2, y: cy - hl / 2, w: hw, h: hl, rotate: ang,
      fill: { color: o.color || P.ink }, line: { type: "none" } });
    return hl;
  };
  // straight arrow from (x1, y1) with its tip at (x2, y2); o.both adds a head at (x1, y1)
  const A = (x1, y1, x2, y2, o = {}) => {
    const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len;
    const w0 = o.width || 0.75, hl = o.hl || (w0 >= 1.25 ? 0.075 : 0.055);
    const s0 = o.both ? hl * 0.85 : 0;
    L(x1 + ux * s0, y1 + uy * s0, x2 - ux * hl * 0.85, y2 - uy * hl * 0.85, o);
    head(x2, y2, ux, uy, o);
    if (o.both) head(x1, y1, -ux, -uy, o);
  };
  // freeform path through absolute points [[x, y], ...]; o.arrow puts a head on the last point;
  // o.close closes it; o.fill fills it. Segments given as {q: [cx, cy]} entries are quadratic curves.
  const path_ = (pts, o = {}) => {
    pts = pts.map((p) => (Array.isArray(p) ? p.slice() : { q: p.q.slice(), to: p.to.slice() }));
    let tip = null;
    if (o.arrow) {                          // shorten the last (straight) segment and put a drawn head on it
      const a = pts[pts.length - 2], b = pts[pts.length - 1];
      const ax = Array.isArray(a) ? a[0] : a.to[0], ay = Array.isArray(a) ? a[1] : a.to[1];
      const len = Math.hypot(b[0] - ax, b[1] - ay), ux = (b[0] - ax) / len, uy = (b[1] - ay) / len;
      const hl = o.hl || ((o.width || 0.75) >= 1.25 ? 0.075 : 0.055);
      tip = [b[0], b[1], ux, uy];
      pts[pts.length - 1] = [b[0] - ux * hl * 0.85, b[1] - uy * hl * 0.85];
    }
    const xs = [], ys = [];
    pts.forEach((p) => {
      if (Array.isArray(p)) { xs.push(p[0]); ys.push(p[1]); } else { xs.push(p.to[0], p.q[0]); ys.push(p.to[1], p.q[1]); }
    });
    const x0 = Math.min(...xs), y0 = Math.min(...ys);
    const w = Math.max(Math.max(...xs) - x0, 0.001), h = Math.max(Math.max(...ys) - y0, 0.001);
    const points = pts.map((p, i) => {
      if (Array.isArray(p)) return Object.assign({ x: p[0] - x0, y: p[1] - y0 }, i === 0 ? { moveTo: true } : {});
      return { x: p.to[0] - x0, y: p.to[1] - y0, curve: { type: "quadratic", x1: p.q[0] - x0, y1: p.q[1] - y0 } };
    });
    if (o.close) points.push({ close: true });
    const line = o.noLine ? { type: "none" } : Object.assign({ color: o.color || P.ink, width: o.width || 0.75 },
      o.dash ? { dashType: o.dash } : {});
    const shp = slide.addShape(pres.shapes.CUSTOM_GEOMETRY, { x: x0, y: y0, w, h, points, line,
      fill: o.fill ? { color: o.fill, transparency: o.transparency || 0 } : { type: "none" } });
    if (tip) head(tip[0], tip[1], tip[2], tip[3], o);
    return shp;
  };
  const O = (cx, cy, d, fill, line, dy) => slide.addShape(pres.shapes.OVAL, {
    x: cx - d / 2, y: cy - (dy || d) / 2, w: d, h: dy || d,
    fill: fill ? { color: fill } : { type: "none" }, line: line || { type: "none" } });
  const I = (Comp, x, y, s, color, sy) => ops.push(iconPng(Comp, color).then((data) => slide.addImage({ data, x, y, w: s, h: sy || s })));
  // black circled protocol step, as (1)-(6) in the text
  const step = (n, cx, cy, d = 0.13) => {
    O(cx, cy, d, P.ink);
    T(String(n), { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fontSize: 6, bold: true, color: P.white, align: "center" });
  };
  // 45-degree hatch clipped to a rectangle
  const hatch = (x0, y0, w, h, color, d = 0.045, width = 0.5, dir = 1) => {
    const x1 = x0 + w, y1 = y0 + h;
    if (dir > 0) {
      for (let c = x0 + y0 + d / 2; c < x1 + y1; c += d) {       // lines x + y = c (rising to the right)
        const xa = Math.max(x0, c - y1), xb = Math.min(x1, c - y0);
        if (xb - xa > 0.004) L(xa, c - xa, xb, c - xb, { color, width });
      }
    } else {
      for (let c = x0 - y1 + d / 2; c < x1 - y0; c += d) {       // lines x - y = c (falling to the right)
        const xa = Math.max(x0, c + y0), xb = Math.min(x1, c + y1);
        if (xb - xa > 0.004) L(xa, xa - c, xb, xb - c, { color, width });
      }
    }
  };
  // curly brace under [xa, xb] at y (opening up, tip down); depth = total height
  const brace = (xa, xb, y, depth = 0.1, o = {}) => {
    const r = depth / 2, xm = (xa + xb) / 2;
    return path_([[xa, y], { q: [xa, y + r], to: [xa + r, y + r] }, [xm - r, y + r], { q: [xm, y + r], to: [xm, y + 2 * r] },
      { q: [xm, y + r], to: [xm + r, y + r] }, [xb - r, y + r], { q: [xb, y + r], to: [xb, y] }],
    { color: o.color || P.ink, width: o.width || 0.75 });
  };
  // any preset shape ("star5", "diamond", ...) at o.x, o.y
  const S = (shape, o) => slide.addShape(pres.shapes[shape], o);
  // database cylinder for the stored plans
  const can = (o) => slide.addShape(pres.shapes.CAN, { x: o.x, y: o.y, w: o.w, h: o.h, fill: { color: o.fill },
    line: o.line || { type: "none" } });
  const k = (t, o = {}) => ({ text: t, options: Object.assign({ italic: true }, o) });
  // text runs with every standalone variable k (as in "k+1", "read k") set in italics
  const kt = (str, o = {}) => str.split(/(\bk\b)/).filter((x) => x !== "").map((x) =>
    ({ text: x, options: Object.assign({}, o, x === "k" ? { italic: true } : {}) }));
  // the same, ending with a line break
  const ktb = (str, o = {}) => { const runs = kt(str, o); runs[runs.length - 1].options.breakLine = true; return runs; };
  const r = (t, o = {}) => ({ text: t, options: o });
  return { T, R, L, A, head, path: path_, O, I, S, can, step, hatch, brace, k, kt, ktb, r, pres, slide };
}

// a view of the kit shifted by (dx, dy): panels drawn at their own origin are placed into a larger slide
function offset(K, dx, dy) {
  const P2 = (p) => (Array.isArray(p) ? [p[0] + dx, p[1] + dy] : { q: [p.q[0] + dx, p.q[1] + dy], to: [p.to[0] + dx, p.to[1] + dy] });
  const mv = (o) => Object.assign({}, o, { x: o.x + dx, y: o.y + dy });
  return Object.assign({}, K, {
    T: (t, o = {}) => K.T(t, "x" in o ? mv(o) : o),
    R: (o) => K.R(mv(o)),
    L: (x1, y1, x2, y2, o) => K.L(x1 + dx, y1 + dy, x2 + dx, y2 + dy, o),
    A: (x1, y1, x2, y2, o) => K.A(x1 + dx, y1 + dy, x2 + dx, y2 + dy, o),
    head: (x2, y2, ux, uy, o) => K.head(x2 + dx, y2 + dy, ux, uy, o),
    path: (pts, o) => K.path(pts.map(P2), o),
    O: (cx, cy, d, fill, line, dy2) => K.O(cx + dx, cy + dy, d, fill, line, dy2),
    I: (Comp, x, y, s0, color, sy) => K.I(Comp, x + dx, y + dy, s0, color, sy),
    S: (shape, o) => K.S(shape, mv(o)),
    can: (o) => K.can(mv(o)),
    step: (n, cx, cy, d) => K.step(n, cx + dx, cy + dy, d),
    hatch: (x0, y0, w, h, color, d, width, dir) => K.hatch(x0 + dx, y0 + dy, w, h, color, d, width, dir),
    brace: (xa, xb, y, depth, o) => K.brace(xa + dx, xb + dx, y + dy, depth, o),
  });
}

async function build(name, W, H, draw) {
  const pres = new pptxgen();
  pres.author = "ReadSeal authors";
  pres.subject = "ISPA r15: regenerated from r14 source coordinates and unchanged data";
  pres.defineLayout({ name: "FIG", width: W, height: H });
  pres.layout = "FIG";
  pres.title = name;
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  const ops = [];
  draw(kit(pres, slide, ops), W, H);
  await Promise.all(ops);
  const out = path.join(ROOT, "figures", name + ".pptx");
  await pres.writeFile({ fileName: out });
  console.log("wrote", path.relative(ROOT, out));
}

module.exports = { ROOT, FONT, P, readCsv, num, tw, kit, offset, build, iconPng };
