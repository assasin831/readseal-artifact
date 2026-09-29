// Data figures of the BIM paper as editable PowerPoint slides, drawn from the CSV files in data/.
//
//   node scripts/make_charts_pptx.js [name ...]       (default: all five figures)
//     -> figures/fig2_trace.pptx        Fig. 2  one-slot trace at 20 Hz                     data/trace_20hz.csv
//     -> figures/fig3_boundaries.pptx   Fig. 3  read boundaries of graph snapshots          data/boundaries.csv
//     -> figures/fig5_delivery.pptx     Fig. 4  (a)-(c) rate sweep, (d) late read           data/rate_sweep.csv, late_read.csv
//     -> figures/fig6_slots.pptx        Fig. 5  slots window at 30 Hz, deadlines            data/slots_30hz.csv, deadlines_30hz.csv
//     -> figures/fig7_mixed.pptx        Fig. 6  jitter, mixed recipients, clone-on-accept   data/mixed_30hz.csv
//   sh scripts/export_figures_pdf.sh                  -> the matching PDFs used by main.tex
//
// Each figure is one slide at its printed size, with its legend row and panel captions on the slide.
// Everything is a native, editable shape (no pasted images): boxed axes, outward ticks, light grid lines,
// solid bars and filled markers for BIM, hatched bars and hollow marks for the baselines, so that the figures
// survive greyscale printing. Axes are drawn from data coordinates, so the plotted values are the CSV values.

const { P, readCsv, num, tw, offset, build } = require("./figkit");

// ---------------------------------------------------------------------------------------------
// chart kit
// ---------------------------------------------------------------------------------------------
const FS = { tick: 7, label: 7.5, note: 6.5, small: 6 };
const POL = {
  BIM: { label: "BIM + ReadSeal", color: P.bim, edge: P.bimDark, fill: P.bim, marker: "circle", hollow: false, dash: null },
  Manual: { label: "Manual", color: P.manual, edge: P.manualDark, fill: P.white, hatch: { color: P.manual, dir: 1 },
    marker: "diamond", hollow: true, dash: "dash" },
  Full: { label: "Full retention", color: P.full, edge: P.fullDark, fill: P.fullLight, hatch: { color: P.full, dir: -1 },
    marker: "square", hollow: false, dash: null },
  Clone: { label: "Clone-on-accept", color: P.clone, edge: P.cloneDark, fill: P.clone, marker: "triangle", hollow: false, dash: null },
};

function axes(K, o) {
  const { T, L, R } = K;
  const x0 = o.x, y0 = o.y, x1 = o.x + o.w, y1 = o.y + o.h;
  const X = (v) => x0 + (v - o.xr[0]) / (o.xr[1] - o.xr[0]) * o.w;
  const Y = (v) => y1 - (v - o.yr[0]) / (o.yr[1] - o.yr[0]) * o.h;
  const tl = 0.03;
  const ax = { X, Y, x0, y0, x1, y1 };
  ax.grid = (which = "y") => {
    if (which.includes("y")) (o.yticks || []).forEach((v) => { if (v > o.yr[0] && v < o.yr[1]) L(x0, Y(v), x1, Y(v), { color: P.grid, width: 0.5 }); });
    if (which.includes("x")) (o.xticks || []).forEach((v) => { if (v > o.xr[0] && v < o.xr[1]) L(X(v), y0, X(v), y1, { color: P.grid, width: 0.5 }); });
  };
  ax.frame = () => {
    R({ x: x0, y: y0, w: o.w, h: o.h, fill: null, line: { color: P.ink2, width: 0.6 } });
    (o.yticks || []).forEach((v, i) => {
      L(x0 - tl, Y(v), x0, Y(v), { color: P.ink2, width: 0.6 });
      const lab = o.ytl ? o.ytl[i] : String(v);
      if (lab !== "") T(lab, { x: x0 - tl - 0.42, y: Y(v) - 0.06, w: 0.4, h: 0.12, fontSize: FS.tick, align: "right" });
    });
    if (!o.noXticks) (o.xticks || []).forEach((v, i) => {
      L(X(v), y1, X(v), y1 + tl, { color: P.ink2, width: 0.6 });
      const lab = o.xtl ? o.xtl[i] : String(v), al = o.xtlAlign ? o.xtlAlign[i] : "center";
      const bx = al === "left" ? X(v) - 0.02 : al === "right" ? X(v) - 0.58 : X(v) - 0.3;
      T(lab, { x: bx, y: y1 + tl + 0.005, w: 0.6, h: 0.12, fontSize: FS.tick, align: al });
    });
    if (o.xlabel) T(o.xlabel, { x: x0 - 0.2, y: y1 + 0.16, w: o.w + 0.4, h: 0.13, fontSize: FS.label, align: "center" });
    if (o.ylabel) {
      // centred on the plot, but kept inside the slide when the label is longer than the plot is tall
      const Lh = tw(o.ylabel, FS.label) / 2 + 0.02;
      let cy = (y0 + y1) / 2;
      if (o.H) cy = Math.min(Math.max(cy, Lh), o.H - Lh);
      T(o.ylabel, { x: x0 - o.ylabelDx - 0.6, y: cy - 0.07, w: 1.2, h: 0.14, fontSize: FS.label, align: "center", rotate: 270 });
    }
  };
  return ax;
}

// markers centred at (cx, cy)
function marker(K, kind, cx, cy, s, fill, edge, width = 0.6) {
  const shape = { circle: "OVAL", square: "RECTANGLE", diamond: "DIAMOND", triangle: "ISOSCELES_TRIANGLE" }[kind];
  const sz = kind === "diamond" ? s * 1.3 : kind === "square" ? s * 0.9 : s;
  K.S(shape, { x: cx - sz / 2, y: cy - sz / 2, w: sz, h: sz, fill: fill ? { color: fill } : { type: "none" },
    line: { color: edge, width } });
}

function polLine(K, ax, xs, ys, pol, o = {}) {
  const st = POL[pol];
  const pts = xs.map((x, i) => [ax.X(x), ax.Y(ys[i])]).filter((p) => !isNaN(p[1]));
  K.path(pts, { color: st.color, width: o.width || (pol === "BIM" ? 1.3 : 1.1), dash: o.dash !== undefined ? o.dash : st.dash });
  if (o.noMarkers) return;
  pts.forEach(([x, y]) => marker(K, st.marker, x, y, o.ms || 0.055, (o.hollow !== undefined ? o.hollow : st.hollow) ? P.white : st.color,
    st.color, 0.7));
}

function errBar(K, x, ylo, yhi, color = P.ink, cap = 0.018, width = 0.6) {
  if (Math.abs(yhi - ylo) < 0.004) return;
  K.L(x, ylo, x, yhi, { color, width });
  K.L(x - cap, ylo, x + cap, ylo, { color, width });
  K.L(x - cap, yhi, x + cap, yhi, { color, width });
}

// bar in data coordinates: centre xc (in), width w (in), from value v0 to v1
function polBar(K, ax, xc, w, v0, v1, pol, o = {}) {
  const st = POL[pol];
  const yTop = ax.Y(v1), yBot = ax.Y(v0), h = yBot - yTop;
  if (h <= 0.0005) return;
  K.R({ x: xc - w / 2, y: yTop, w, h, fill: o.fill || st.fill });
  if (!o.fill && st.hatch) K.hatch(xc - w / 2, yTop, w, h, st.hatch.color, 0.04, 0.45, st.hatch.dir);
  K.R({ x: xc - w / 2, y: yTop, w, h, fill: null, line: Object.assign({ color: st.edge, width: 0.6 }, o.dashEdge ? { dashType: "dash" } : {}) });
}

// one framed legend row; items: {kind: "bar"|"barline"|"line"|"patch", pol, label, ...}. Text is measured with
// Calibri's advance widths and the font shrinks (down to 6 pt) until the row fits the figure width.
function legendRow(K, W, H, items, o = {}) {
  const { T, R } = K;
  const sw = (it) => (it.kind === "bar" ? 0.2 : it.kind === "patch" ? 0.24 : 0.3);
  let fs = o.fs || 7;
  const gap = o.gap || 0.16, pad = 0.07, lg = 0.045;
  const total = (f) => items.reduce((a, it) => a + sw(it) + lg + tw(it.label, f), 0) + gap * (items.length - 1) + 2 * pad;
  while (total(fs) > W - 0.04 && fs > 6) fs -= 0.1;
  const tot = total(fs);
  let x = (W - tot) / 2 + pad;
  const y = H / 2;
  R({ x: (W - tot) / 2, y: 0.015, w: tot, h: H - 0.03, fill: P.white, line: { color: P.rule, width: 0.5 } });
  items.forEach((it) => {
    const st = it.pol ? POL[it.pol] : null, w0 = sw(it);
    if (it.kind === "bar" || it.kind === "barline") {
      const bw = it.kind === "barline" ? 0.11 : 0.2;
      K.R({ x, y: y - 0.045, w: bw, h: 0.09, fill: st.fill });
      if (st.hatch) K.hatch(x, y - 0.045, bw, 0.09, st.hatch.color, 0.04, 0.45, st.hatch.dir);
      K.R({ x, y: y - 0.045, w: bw, h: 0.09, fill: null, line: { color: st.edge, width: 0.6 } });
      if (it.kind === "barline") {
        K.path([[x + 0.14, y], [x + w0, y]], { color: st.color, width: 1.1, dash: st.dash });
        marker(K, st.marker, x + 0.14 + (w0 - 0.14) / 2, y, 0.055, st.hollow ? P.white : st.color, st.color, 0.7);
      }
    } else if (it.kind === "line") {
      K.path([[x, y], [x + w0, y]], { color: it.color, width: it.width || 1.1, dash: it.dash });
    } else if (it.kind === "patch") {
      K.R({ x, y: y - 0.045, w: w0, h: 0.09, fill: it.fill,
        line: it.edge ? { color: it.edge, width: 0.6, dashType: it.dashEdge ? "dash" : "solid" } : null });
    }
    T(it.label, { x: x + w0 + lg, y: y - 0.07, w: tw(it.label, fs) + 0.05, h: 0.14, fontSize: fs });
    x += w0 + lg + tw(it.label, fs) + gap;
  });
}

// =============================================================================================
// Fig. 2: one-slot trace at 20 Hz (scheme rows with rotated names, lanes of pill-shaped
// work items, arrival stars, latency bars with end caps, dashed highlight boxes, a framed legend)
// =============================================================================================
function fig2(K, W, H) {
  const { T, R, L, O, path } = K;
  const rows = readCsv("trace_20hz.csv");
  const TMAX = 255;
  const x0 = 0.5, x1 = W - 0.05;
  const X = (t) => x0 + t / TMAX * (x1 - x0);
  const pillH = 0.055, laneH = 0.076;
  const GREEN = { edge: P.readEdge, fill: "C5E0B4" }, BLUE = { edge: P.privEdge, fill: "BDD7EE" };
  const HOLD = P.blue;
  const star = (cx, cy, s, edge, fill) => K.S("STAR_5_POINT", { x: cx - s / 2, y: cy - s / 2, w: s, h: s,
    fill: fill ? { color: fill } : { type: "none" }, line: { color: edge, width: 0.6 } });
  const cross = (cx, cy, s, color) => { L(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2, { color, width: 1.1 });
    L(cx - s / 2, cy + s / 2, cx + s / 2, cy - s / 2, { color, width: 1.1 }); };
  const hbar = (a, b, y, color) => {                 // latency bar with end caps
    L(X(a), y, X(b), y, { color, width: 1.1 });
    L(X(a), y - 0.03, X(a), y + 0.03, { color, width: 1.1 });
    L(X(b), y - 0.03, X(b), y + 0.03, { color, width: 1.1 });
  };
  const pill = (a, b, y, st) => {
    const w = Math.max(X(b) - X(a), 0.02);
    K.R({ x: X(a), y: y - pillH / 2, w, h: pillH, fill: st.fill, line: { color: st.edge, width: 0.6 }, radius: Math.min(pillH / 2, w / 2) });
  };

  // ---- framed legend ----
  const ly = 0.1, lfs = 6.5;
  const items = [
    ["admitted", 0.08, (x) => star(x + 0.04, ly, 0.08, P.ink, P.white)],
    ["dropped", 0.06, (x) => cross(x + 0.03, ly, 0.055, P.bad)],
    ["slot hold (ms)", 0.17, (x) => { L(x, ly, x + 0.17, ly, { color: HOLD, width: 1.1 }); L(x, ly - 0.03, x, ly + 0.03, { color: HOLD, width: 1.1 });
      L(x + 0.17, ly - 0.03, x + 0.17, ly + 0.03, { color: HOLD, width: 1.1 }); }],
    ["borrow held", 0.15, (x) => K.R({ x, y: ly - pillH / 2, w: 0.15, h: pillH, fill: GREEN.fill, line: { color: GREEN.edge, width: 0.6 }, radius: pillH / 2 })],
    ["after return", 0.15, (x) => K.R({ x, y: ly - pillH / 2, w: 0.15, h: pillH, fill: BLUE.fill, line: { color: BLUE.edge, width: 0.6 }, radius: pillH / 2 })],
  ];
  const wItem = items.map(([t, sw]) => sw + 0.035 + tw(t, lfs));
  const gapL = 0.09, totL = wItem.reduce((a, b) => a + b, 0) + gapL * (items.length - 1);
  R({ x: (W - totL) / 2 - 0.07, y: 0.02, w: totL + 0.14, h: 0.16, fill: P.white, line: { color: P.ink, width: 0.5 } });
  let lx = (W - totL) / 2;
  items.forEach(([t, sw, draw], i) => {
    draw(lx);
    T(t, { x: lx + sw + 0.035, y: ly - 0.065, w: tw(t, lfs) + 0.1, h: 0.13, fontSize: lfs });
    lx += wItem[i] + gapL;
  });

  // ---- two scheme rows ----
  const schemes = [["Full", ["Full", "retention"], "(a)"], ["BIM", ["BIM +", "ReadSeal"], "(b)"]];
  const top0 = 0.225, blockH = 0.215 + 4 * laneH + 0.005, gapY = 0.04;
  const bottom = top0 + 2 * blockH + gapY;
  for (let t = 0; t <= 250; t += 50) L(X(t), top0 - 0.02, X(t), bottom, { color: P.hair, width: 0.5, dash: "sysDot" });
  schemes.forEach(([pol, name, tag], si) => {
    const yA = top0 + si * (blockH + gapY);          // arrivals row
    const ySlot = yA + 0.135, yR = (i) => ySlot + 0.08 + i * laneH;
    // rotated scheme name and one square per recipient lane inside a dashed box
    T([{ text: name[0], options: { breakLine: true } }, { text: name[1] }], { x: -0.26 + 0.0, y: yA + blockH / 2 - 0.1, w: 0.72, h: 0.2,
      fontSize: 7, bold: true, align: "center", rotate: 270, wrap: true, lineSpacingMultiple: 0.9 });
    L(0.2, yA + 0.02, 0.2, yA + blockH - 0.03, { color: P.ink, width: 0.6 });
    T("slot", { x: 0.215, y: ySlot - 0.075, w: 0.25, h: 0.12, fontSize: 6.5, align: "center" });
    K.R({ x: 0.225, y: yR(0) - laneH / 2 + 0.008, w: 0.23, h: 4 * laneH - 0.012, fill: null, line: { color: P.ink2, width: 0.5, dashType: "dash" } });
    for (let i = 0; i < 4; i++) {
      K.R({ x: 0.25, y: yR(i) - 0.034, w: 0.18, h: 0.068, fill: "D9D9D9" });
      T(`R${i + 1}`, { x: 0.25, y: yR(i) - 0.04, w: 0.18, h: 0.08, fontSize: 6, align: "center", color: P.ink });
    }
    const mine = rows.filter((e) => e.policy === pol);
    // idle stretches: no recipient has work, so the pipeline and with it the shared GPU sits idle
    const iv = mine.filter((e) => e.row.startsWith("R") && !isNaN(num(e.end_ms)) && num(e.end_ms) > 0 && num(e.start_ms) < TMAX)
      .map((e) => [Math.max(num(e.start_ms), 0), Math.min(num(e.end_ms), TMAX)]).sort((a, b) => a[0] - b[0]);
    const merged = [];
    iv.forEach(([a, b]) => { if (merged.length && a <= merged[merged.length - 1][1]) merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b); else merged.push([a, b]); });
    for (let i = 0; i + 1 < merged.length; i++) {
      const a = merged[i][1], b = merged[i + 1][0];
      if (b - a > 10) {
        K.R({ x: X(a) + 0.01, y: yR(0) - laneH / 2, w: X(b) - X(a) - 0.02, h: 4 * laneH, fill: P.hilite, line: { color: P.hiliteEdge, width: 0.6, dashType: "dash" } });
        T("idle", { x: X(a), y: yR(1.5) - 0.06, w: X(b) - X(a), h: 0.12, fontSize: 6.5, align: "center", color: P.hiliteEdge });
      }
    }
    mine.forEach((e) => {
      let a = num(e.start_ms), b = num(e.end_ms);
      if (a > TMAX || (!isNaN(b) && b < 0)) return;
      if (!isNaN(b) && a < 0 && b < 4) return;          // skip slivers (< 4 ms) of work carried over from before the window
      if (!isNaN(b)) { a = Math.max(a, 0); b = Math.min(b, TMAX); }
      if (e.kind === "admitted") {
        star(X(a), yA + 0.045, 0.08, P.ink, P.white);
        K.A(X(a), yA + 0.09, X(a), ySlot - 0.035, { width: 0.6, hl: 0.035, hw: 0.03 });
      } else if (e.kind === "busy") {
        cross(X(a), yA + 0.045, 0.055, P.bad);
      } else if (e.kind === "held") {
        hbar(a, b, ySlot, HOLD);
        const hold = e.label.includes("|") ? Number(e.label.split("|")[1].replace(" ms", "")).toFixed(0) : "";
        if (hold && b - a > 16) T(hold, { x: X(a), y: ySlot - 0.095, w: X(b) - X(a), h: 0.08, fontSize: 6, align: "center", color: HOLD, bold: true });
      } else {
        const i = Number(e.row.slice(1)) - 1;
        pill(a, b, yR(i), e.kind === "holds_source" ? GREEN : BLUE);
      }
    });
  });
  // time axis
  const ya = bottom + 0.01;
  L(x0, ya, x1, ya, { color: P.ink2, width: 0.6 });
  for (let t = 0; t <= 250; t += 50) {
    L(X(t), ya, X(t), ya + 0.03, { color: P.ink2, width: 0.6 });
    T(String(t), { x: X(t) - 0.2, y: ya + 0.035, w: 0.4, h: 0.12, fontSize: FS.tick, align: "center" });
  }
  T([{ text: "Time since publication " }, { text: "k", options: { italic: true } }, { text: " arrived (ms)" }],
    { x: x0, y: ya + 0.145, w: x1 - x0, h: 0.13, fontSize: FS.label, align: "center" });
}


// ---------------------------------------------------------------------------------------------
// helpers shared by Figs. 3, 5, 6, 7
// ---------------------------------------------------------------------------------------------
// rotated label reading upwards whose lower end sits at (cx, yBottom)
function upLabel(K, text, cx, yBottom, o = {}) {
  const w = o.w || 0.4, h = o.h || 0.1;
  K.T(text, Object.assign({ x: cx - w / 2, y: yBottom - w / 2 - h / 2, w, h, fontSize: o.fs || 6.3, align: "left", rotate: 270,
    color: o.color || P.ink }, o.bold ? { bold: true } : {}));
}
function framedLegend(K, x, y, rows, o = {}) {       // small framed key inside a panel; rows: [draw(x, y, sw), label]
  const fs = o.fs || 6.3, sw = o.sw || 0.2, rh = o.rh || 0.12, pad = 0.035, cg = 0.07;
  const cols = o.cols || 1, nr = Math.ceil(rows.length / cols);
  const colW = [];
  for (let c = 0; c < cols; c++) colW.push(sw + 0.04 + Math.max(...rows.filter((_, i) => i % cols === c).map(([, t]) => tw(t, fs))));
  const W0 = colW.reduce((a, b) => a + b, 0) + (cols - 1) * cg + 2 * pad, H0 = nr * rh + 2 * pad - 0.02;
  const x0 = o.right ? x - W0 : x, y0 = o.bottom ? y - H0 : y;
  K.R({ x: x0, y: y0, w: W0, h: H0, fill: P.white, line: { color: P.rule, width: 0.5 } });
  rows.forEach(([draw, t], i) => {
    const c = i % cols, r = Math.floor(i / cols);
    const lx = x0 + pad + colW.slice(0, c).reduce((a, b) => a + b, 0) + c * cg, ly = y0 + pad + r * rh + rh / 2 - 0.01;
    draw(lx, ly, sw);
    K.T(t, { x: lx + sw + 0.04, y: ly - 0.06, w: tw(t, fs) + 0.05, h: 0.12, fontSize: fs });
  });
}
const PH = 1.08;                                   // panel height of Figs. 5 and 6 (in)
const M = { l: 0.37, r: 0.05, t: 0.05, b: 0.31 };

function legendRowFig(items, W, H = 0.2) {
  return (K) => legendRow(K, W, H, items, { fs: 7, gap: 0.2 });
}

// =============================================================================================
// Fig. 3: read boundaries of graph snapshots (exact operation counts)
// =============================================================================================
function fig3(K, W, H) {
  const { T, R } = K;
  const rows = readCsv("boundaries.csv");
  const snaps = [], models = [];
  rows.forEach((r) => { if (!snaps.includes(r.snapshot)) snaps.push(r.snapshot); if (!models.includes(r.model)) models.push(r.model); });
  const val = {};
  rows.forEach((r) => { val[r.snapshot + "|" + r.model] = [Number(r.prefix_ops), Number(r.total_ops)]; });
  const titles = { "TransFusion head": "TransFusion head", "ResNet-18": "ResNet-18 tail" };
  const names = { Base: "Base graph", "Alias chain": "Add alias chain", "Early source clone": "Clone source early",
    "Middle source clone": "Clone source mid-graph", "Late source clone": "Clone source late", "Late alias read": "Read alias late",
    "Remove late read": "Remove late read", "Private-only probe": "Add private ops" };
  const l0 = 1.02, gapx = 0.17, rr = 0.06, top = 0.36, bot = 0.3;
  const pw = (W - l0 - gapx - rr) / 2, ph = H - top - bot;
  const n = snaps.length, pitch = ph / n, bh = pitch * 0.8;
  // legend
  legendRow(K, W, 0.2, [
    { kind: "patch", fill: P.read, edge: P.readEdge, label: "through the last source read (borrow held)" },
    { kind: "patch", fill: P.priv, edge: P.privEdge, label: "after the last source read" }], { fs: 7, gap: 0.25 });
  models.forEach((m, k) => {
    const x0 = l0 + k * (pw + gapx);
    const ax = axes(K, { x: x0, y: top, w: pw, h: ph, xr: [0, 100], yr: [0, 1], xticks: [0, 50, 100], xtl: ["0", "50", "100"],
      xtlAlign: ["left", "center", "right"] });
    snaps.forEach((sn, i) => {
      const [p, tot] = val[sn + "|" + m];
      const f = 100 * p / tot, yc = top + (i + 0.5) * pitch;
      R({ x: ax.X(0), y: yc - bh / 2, w: ax.X(100) - ax.X(0), h: bh, fill: P.priv });
      if (f > 0) R({ x: ax.X(0), y: yc - bh / 2, w: ax.X(f) - ax.X(0), h: bh, fill: P.read });
      R({ x: ax.X(0), y: yc - bh / 2, w: ax.X(100) - ax.X(0), h: bh, fill: null, line: { color: P.privEdge, width: 0.4 } });
      if (f > 0) K.L(ax.X(f), yc - bh / 2, ax.X(f), yc + bh / 2, { color: P.readEdge, width: 0.6 });
      T(`${p}/${tot}`, { x: ax.X(0), y: yc - 0.06, w: ax.X(97.5) - ax.X(0), h: 0.12, fontSize: 6, align: "right" });
      if (k === 0) T(names[sn] || sn, { x: 0.0, y: yc - 0.06, w: x0 - 0.05, h: 0.12, fontSize: 6.8, align: "right" });
    });
    ax.frame();
    T(titles[m] || m, { x: x0, y: top - 0.15, w: pw, h: 0.13, fontSize: 7, align: "center" });
  });
  T("Last source-read position (% of graph)", { x: l0, y: H - 0.14, w: 2 * pw + gapx, h: 0.13, fontSize: FS.label, align: "center" });
}

// =============================================================================================
// Fig. 5: one-slot delivery, its latency cost, and its cause (rate sweep, 108 runs; late-read test, 36)
// =============================================================================================
const W5 = { a: 1.92, b: 1.74, c: 1.74, d: 1.6 };
const XL = [7.5, 42.5];
const HOLD_BREAK = 1000 / 51;                      // rate at which Full's 51 ms hold exceeds the period
function rateSweep() {
  const rs = readCsv("rate_sweep.csv");
  const rates = [...new Set(rs.map((r) => num(r.rate)))].sort((a, b) => a - b);
  const col = (pol, key) => rates.map((x) => num(rs.find((r) => r.policy === pol && num(r.rate) === x)[key]));
  return { rates, col };
}
function rateAxes(K, W, yr, yticks, ylabel, o = {}) {
  const { rates } = rateSweep();
  return axes(K, Object.assign({ x: M.l, y: M.t, w: W - M.l - M.r, h: PH - M.t - M.b, xr: XL, yr, xticks: rates,
    yticks, xlabel: "Source rate (Hz)", ylabel, ylabelDx: 0.29, H: PH }, o));
}

function fig5a(K, W, H) {
  const { T, R, L, A } = K;
  const { rates, col } = rateSweep();
  const ax = rateAxes(K, W, [0, 100], [0, 20, 40, 60, 80], "Timely results/s");
  R({ x: ax.X(HOLD_BREAK), y: ax.y0, w: ax.x1 - ax.X(HOLD_BREAK), h: ax.y1 - ax.y0, fill: P.shade });
  ax.grid("xy");
  K.path([[ax.X(10), ax.Y(40)], [ax.X(21), ax.Y(84)]], { color: P.ink2, width: 0.7, dash: "sysDot" });
  L(ax.x0, ax.Y(78.4), ax.x1, ax.Y(78.4), { color: P.ink3, width: 0.7, dash: "dash" });
  const bim = col("BIM", "goodput"), man = col("Manual", "goodput"), full = col("Full", "goodput");
  const ratios = { 20: "1.95", 25: "1.50", 30: "1.31", 40: "1.48" };    // stated in the text (exact data)
  rates.forEach((x, i) => {
    if (!ratios[x]) return;
    A(ax.X(x), ax.Y(full[i] + 3), ax.X(x), ax.Y(bim[i] - 3), { color: P.ink3, width: 0.55, both: true, hl: 0.035, hw: 0.03 });
    T(ratios[x], { x: ax.X(x) - 0.15, y: ax.Y(91) - 0.055, w: 0.3, h: 0.11, fontSize: 6.3, align: "center" });
  });
  ["Full", "BIM", "Manual"].forEach((pol) => {
    const ys = col(pol, "goodput"), lo = col(pol, "goodput_ci_lo"), hi = col(pol, "goodput_ci_hi");
    polLine(K, ax, rates, ys, pol);
    rates.forEach((x, i) => { if (!isNaN(lo[i])) errBar(K, ax.X(x), ax.Y(lo[i]), ax.Y(hi[i]), POL[pol].color, 0.015, 0.5); });
  });
  T("Full's hold > period", { x: ax.x1 - 1.0, y: ax.Y(4) - 0.11, w: 0.97, h: 0.11, fontSize: 6.3, align: "right", color: P.ink2 });
  const ang = Math.atan2(ax.Y(40) - ax.Y(84), ax.X(21) - ax.X(10)) * 180 / Math.PI;
  const rad = ang * Math.PI / 180, cx = ax.X(12.0) - 0.055 * Math.sin(rad), cy = ax.Y(49.5) - 0.055 * Math.cos(rad);
  T([{ text: "offered 4" }, { text: "λ", options: { italic: true } }], { x: cx - 0.2, y: cy - 0.1, w: 0.4, h: 0.1, fontSize: 6.3,
    align: "center", color: P.ink2, rotate: 360 - ang });
  ax.frame();
}

function fig5b(K, W, H) {
  const { T, L } = K;
  const { rates, col } = rateSweep();
  const ax = rateAxes(K, W, [20, 110], [20, 40, 60, 80, 100], "Receipt latency (ms)");
  K.R({ x: ax.X(HOLD_BREAK), y: ax.y0, w: ax.x1 - ax.X(HOLD_BREAK), h: ax.y1 - ax.y0, fill: P.shade });
  ax.grid("xy");
  L(ax.x0, ax.Y(100), ax.x1, ax.Y(100), { color: P.ink, width: 0.7, dash: "lgDashDot" });
  T("deadline", { x: ax.X(8.3), y: ax.Y(98.5), w: 0.5, h: 0.11, fontSize: 6.3 });
  polLine(K, ax, rates, col("BIM", "receipt_p95_ms"), "BIM", { width: 0.9, dash: "sysDot", hollow: true });
  ["Full", "Manual", "BIM"].forEach((pol) => polLine(K, ax, rates, col(pol, "receipt_mean_ms"), pol));
  framedLegend(K, ax.x1 - 0.03, ax.y1 - 0.03, [
    [(x, y, sw) => { K.path([[x, y], [x + sw, y]], { color: P.ink2, width: 1.1 }); marker(K, "circle", x + sw / 2, y, 0.05, P.ink2, P.ink2); }, "mean"],
    [(x, y, sw) => { K.path([[x, y], [x + sw, y]], { color: P.bim, width: 0.9, dash: "sysDot" }); marker(K, "circle", x + sw / 2, y, 0.05, P.white, P.bim, 0.7); }, "BIM 95th pct."],
  ], { right: true, bottom: true, cols: 2, fs: 6.1, sw: 0.17 });
  ax.frame();
}

function fig5c(K, W, H) {
  const { T } = K;
  const { rates, col } = rateSweep();
  const top = 75;
  const ax = rateAxes(K, W, [0, top], [0, 25, 50, 75], "Slot hold time (ms)");
  // region above the period: the next arrival finds the slot still held
  const xs = []; for (let i = 0; i <= 120; i++) xs.push(XL[0] + (XL[1] - XL[0]) * i / 120);
  const pts = xs.map((x) => [ax.X(x), ax.Y(Math.min(1000 / x, top))]);
  K.path([...pts, [ax.X(XL[1]), ax.Y(top)], [ax.X(XL[0]), ax.Y(top)]], { fill: P.shade, noLine: true, close: true });
  ax.grid("xy");
  const vis = xs.filter((x) => 1000 / x <= top);
  K.path(vis.map((x) => [ax.X(x), ax.Y(1000 / x)]), { color: P.ink2, width: 0.8, dash: "sysDot" });
  // label sits under the curve's tail at the right edge, the only place it is clear of the band and the lines
  T([{ text: "period 1/" }, { text: "λ", options: { italic: true } }], { x: ax.X(42.2) - 0.5, y: ax.Y(12.5) - 0.055, w: 0.5,
    h: 0.11, fontSize: 6.3, align: "right", color: P.ink2 });
  T([{ text: "next arrival finds", options: { breakLine: true } }, { text: "the slot busy" }], { x: ax.x1 - 0.9, y: ax.Y(72.5), w: 0.87,
    h: 0.2, fontSize: 6.3, align: "right", valign: "top", color: P.ink2, wrap: true, lineSpacingMultiple: 0.9 });
  const band = (lo, hi, fill) => K.path([...rates.map((x, i) => [ax.X(x), ax.Y(hi[i])]),
    ...rates.slice().reverse().map((x, i) => [ax.X(x), ax.Y(lo[rates.length - 1 - i])])], { fill, noLine: true, close: true });
  band(col("BIM", "hold_p5_ms"), col("BIM", "hold_p95_ms"), P.bimLight);
  band(col("Full", "hold_p5_ms"), col("Full", "hold_p95_ms"), P.fullLight);
  ["Full", "BIM", "Manual"].forEach((pol) => polLine(K, ax, rates, col(pol, "hold_mean_ms"), pol));
  K.O(ax.X(HOLD_BREAK), ax.Y(51), 0.1, null, { color: P.ink, width: 0.7 });
  ax.frame();
}

function fig5d(K, W, H) {
  const lr = readCsv("late_read.csv");
  const g = {}; lr.forEach((r) => { g[r.variant + "|" + r.policy] = r; });
  const ax = axes(K, { x: M.l, y: M.t, w: W - M.l - M.r, h: PH - M.t - M.b, xr: [-0.55, 1.55], yr: [0, 110],
    yticks: [0, 20, 40, 60, 80], ylabel: "Timely results/s", ylabelDx: 0.29, noXticks: true, H: PH });
  ax.grid("y");
  const unit = (ax.x1 - ax.x0) / 2.1, w = 0.25 * unit;
  ["base", "late"].forEach((vr, i) => {
    ["BIM", "Manual", "Full"].forEach((pol, j) => {
      const x = ax.X(i + (j - 1) * 0.28), v = num(g[vr + "|" + pol].goodput);
      polBar(K, ax, x, w, 0, v, pol);
      upLabel(K, v.toFixed(1), x, ax.Y(v) - 0.02);
    });
  });
  ax.frame();
  [["base head", "(op 1/287)"], ["late read", "(op 288/289)"]].forEach(([a, b], i) =>
    K.T([{ text: a, options: { breakLine: true } }, { text: b }], { x: ax.X(i) - 0.4, y: ax.y1 + 0.02, w: 0.8, h: 0.23, fontSize: FS.tick,
      align: "center", valign: "top", wrap: true, lineSpacingMultiple: 0.9 }));
}

// =============================================================================================
// Fig. 6: slots versus release policy at 30 Hz (96-run window), and deadline re-scoring
// =============================================================================================
const GROUPS = [["one_slot", "1 slot", "no cap"], ["two_slots", "2 slots", "no cap"], ["two_slots_k4", "2 slots", "K = 4"],
  ["two_slots_k8", "2 slots", "K = 8"]];
const LATE = { BIM: "DEEBF7", Manual: "FBE5D6", Full: "EDEDED" };
function groupAxes(K, W, yr, yticks, ylabel) {
  const ax = axes(K, { x: M.l, y: M.t, w: W - M.l - M.r, h: PH - M.t - 0.36, xr: [-0.5, GROUPS.length - 0.5], yr, yticks,
    ylabel, ylabelDx: 0.29, noXticks: true, H: PH });
  ax.groupLabels = () => GROUPS.forEach(([, a, b], i) => {
    const second = b.startsWith("K") ? [{ text: "K", options: { italic: true } }, { text: b.slice(1) }] : [{ text: b }];
    K.T([{ text: a, options: { breakLine: true } }, ...second], { x: ax.X(i) - 0.3, y: ax.y1 + 0.02, w: 0.6, h: 0.24,
      fontSize: FS.tick, align: "center", valign: "top", wrap: true, lineSpacingMultiple: 0.9 });
  });
  ax.separators = () => [0.5, 1.5, 2.5].forEach((x) => K.L(ax.X(x), ax.y0, ax.X(x), ax.y1, { color: P.grid, width: 0.5 }));
  return ax;
}

function fig6a(K, W, H) {
  const rows = readCsv("slots_30hz.csv");
  const by = {}; rows.forEach((r) => { by[r.config + "|" + r.policy] = r; });
  const ax = groupAxes(K, W, [0, 125], [0, 25, 50, 75, 100, 125], "Results/s");
  ax.grid("y"); ax.separators();
  const unit = ax.X(1) - ax.X(0), bw = 0.24 * unit;
  GROUPS.forEach(([gk], i) => {
    ["BIM", "Manual", "Full"].forEach((pol, j) => {
      const r = by[gk + "|" + pol], x = ax.X(i + (j - 1) * 0.265);
      const tv = num(r.timely), late = num(r.late), lo = num(r.timely_ci_lo), hi = num(r.timely_ci_hi);
      polBar(K, ax, x, bw, 0, tv, pol);
      if (late > 0.3) polBar(K, ax, x, bw, tv, tv + late, pol, { fill: LATE[pol], dashEdge: true });
      if (!isNaN(lo)) errBar(K, x, ax.Y(lo), ax.Y(hi), P.ink, 0.018, 0.6);
      if (late > 20) {                                   // timely value just above its whisker, inside the late segment
        upLabel(K, tv.toFixed(1), x, ax.Y(isNaN(hi) ? tv : hi) - 0.03, { fs: 6.0 });
        upLabel(K, "+" + late.toFixed(1), x, ax.Y(tv + late) - 0.03, { fs: 6.0, color: P.ink2 });
      } else if (late > 3) {                             // a short late segment on top: label the timely part inside the bar
        const ly = ax.Y(Math.min(tv * 0.42, tv - 9));
        K.T(tv.toFixed(1), { x: x - 0.15, y: ly - 0.05, w: 0.3, h: 0.1, fontSize: 6.0, align: "center", rotate: 270,
          color: P.ink, fill: { color: P.white } });
      } else {
        const top = Math.max(tv + late, isNaN(hi) ? tv : hi);
        upLabel(K, tv.toFixed(1), x, ax.Y(top) - 0.035, { fs: 6.0 });
      }
    });
  });
  K.L(ax.x0, ax.Y(78.4), ax.x1, ax.Y(78.4), { color: P.ink3, width: 0.7, dash: "dash" });
  ax.frame(); ax.groupLabels();
}

function fig6b(K, W, H) {
  const rows = readCsv("slots_30hz.csv");
  const by = {}; rows.forEach((r) => { by[r.config + "|" + r.policy] = r; });
  const ax = groupAxes(K, W, [0, 140], [0, 35, 70, 105, 140], "Held source storage (MiB)");
  ax.grid("y"); ax.separators();
  const unit = ax.X(1) - ax.X(0), bw = 0.24 * unit;
  GROUPS.forEach(([gk], i) => ["BIM", "Manual", "Full"].forEach((pol, j) => {
    const x = ax.X(i + (j - 1) * 0.265), mib = num(by[gk + "|" + pol].protected_mib);
    polBar(K, ax, x, bw, 0, mib, pol);
    upLabel(K, mib.toFixed(0), x, ax.Y(mib) - 0.025, { fs: 6.0 });
  }));
  ax.frame(); ax.groupLabels();
}

function fig6c(K, W, H) {
  const dl = readCsv("deadlines_30hz.csv");
  const ax = axes(K, { x: M.l, y: M.t, w: W - M.l - 0.07, h: PH - M.t - 0.36, xr: [75, 205], yr: [0, 100],
    xticks: [80, 100, 120, 150, 200], yticks: [0, 20, 40, 60, 80], xlabel: "Receipt deadline (ms)", ylabel: "Timely results/s", ylabelDx: 0.29,
    H: PH });
  ax.grid("xy");
  K.L(ax.X(100), ax.y0, ax.X(100), ax.y1, { color: P.ink3, width: 0.7, dash: "dash" });
  K.T("deadline in (a)", { x: ax.X(103), y: ax.Y(91) - 0.055, w: 0.7, h: 0.11, fontSize: 6.3, color: P.ink2 });
  const styles = { one_slot: { dash: null, hollow: false, label: "1 slot, no cap" }, two_slots: { dash: "dash", hollow: true, label: "2 slots, no cap" } };
  ["two_slots", "one_slot"].forEach((cfg) => ["Full", "BIM"].forEach((pol) => {
    const pts = dl.filter((r) => r.config === cfg && r.policy === pol).map((r) => [num(r.deadline_ms), num(r.goodput)]).sort((a, b) => a[0] - b[0]);
    polLine(K, ax, pts.map((p) => p[0]), pts.map((p) => p[1]), pol, { dash: styles[cfg].dash, hollow: styles[cfg].hollow, width: 1.15 });
  }));
  framedLegend(K, ax.x1 - 0.03, ax.Y(12), ["one_slot", "two_slots"].map((c) => [(x, y, sw) => {
    K.path([[x, y], [x + sw, y]], { color: P.ink2, width: 1.1, dash: styles[c].dash });
    marker(K, "circle", x + sw / 2, y, 0.05, styles[c].hollow ? P.white : P.ink2, P.ink2, 0.7);
  }, styles[c].label]), { right: true, bottom: true, sw: 0.26 });
  ax.frame();
}

// =============================================================================================
// Fig. 7: jitter, mixed recipients and clone-on-accept (follow-up campaign at 30 Hz, 108 runs)
// =============================================================================================
const G7 = [["periodic", "same"], ["periodic", "mixed"], ["jitter", "same"], ["jitter", "mixed"]];
const PH7 = 1.06;
const POL7 = ["BIM", "Manual", "Full", "Clone"];
function mixedAxes(K, W, yr, yticks, ylabel) {
  const ax = axes(K, { x: M.l, y: M.t, w: W - M.l - M.r, h: PH7 - M.t - 0.37, xr: [-0.5, 3.5], yr, yticks, ylabel, ylabelDx: 0.29,
    noXticks: true, H: PH7 });
  ax.labels = () => {
    G7.forEach(([, mix], i) => K.T(mix === "same" ? "identical" : mix, { x: ax.X(i) - 0.2, y: ax.y1 + 0.02, w: 0.4, h: 0.11, fontSize: FS.tick, align: "center" }));
    [["periodic", 0.5], ["jitter", 2.5]].forEach(([a, c]) => {
      K.T(a, { x: ax.X(c) - 0.3, y: ax.y1 + 0.15, w: 0.6, h: 0.11, fontSize: FS.tick, align: "center", italic: true });
      K.L(ax.X(c - 0.9), ax.y1 + 0.14, ax.X(c + 0.9), ax.y1 + 0.14, { color: P.ink3, width: 0.5 });
    });
    K.L(ax.X(1.5), ax.y1, ax.X(1.5), ax.y1 + 0.26, { color: P.ink3, width: 0.5 });
  };
  return ax;
}
function fig7bars(K, ax, metric, lo, hi, labels) {
  const rows = readCsv("mixed_30hz.csv");
  const unit = ax.X(1) - ax.X(0), bw = 0.19 * unit;
  G7.forEach(([arr, mix], i) => POL7.forEach((pol, j) => {
    const r = rows.find((q) => q.arrival === arr && q.mix === mix && q.policy === pol);
    if (!r) return;
    const x = ax.X(i + (j - 1.5) * 0.205);
    polBar(K, ax, x, bw, 0, num(r[metric]), pol);
    errBar(K, x, ax.Y(num(r[lo])), ax.Y(num(r[hi])), P.ink, 0.014, 0.5);
    if (labels && (pol === "BIM" || pol === "Clone")) upLabel(K, num(r[metric]).toFixed(1), x, ax.Y(num(r[hi])) - 0.022, { fs: 5.8, w: 0.3 });
  }));
}
function fig7a(K, W, H) {
  const ax = mixedAxes(K, W, [0, 122], [0, 25, 50, 75, 100], "Timely publications (%)");
  ax.grid("y");
  K.L(ax.X(1.5), ax.y0, ax.X(1.5), ax.y1, { color: P.grid, width: 0.5 });
  fig7bars(K, ax, "complete_timely_pct", "ct_lo", "ct_hi", true);
  ax.frame(); ax.labels();
}
function fig7b(K, W, H) {
  const ax = mixedAxes(K, W, [0, 120], [0, 30, 60, 90, 120], "99th-pct. latency (ms)");
  ax.grid("y");
  K.L(ax.X(1.5), ax.y0, ax.X(1.5), ax.y1, { color: P.grid, width: 0.5 });
  K.L(ax.x0, ax.Y(100), ax.x1, ax.Y(100), { color: P.ink, width: 0.7, dash: "lgDashDot" });
  fig7bars(K, ax, "p99_ms", "p99_lo", "p99_hi");
  K.T("deadline", { x: ax.X(-0.45), y: ax.Y(101) - 0.11, w: 0.5, h: 0.11, fontSize: 6.3 });
  ax.frame(); ax.labels();
}

module.exports = { axes, marker, polLine, errBar, polBar, legendRow, POL, FS };

if (require.main === module) {
  (async () => {
    const only = process.argv.slice(2);
    // a multi-panel figure on one slide: a framed legend row on top, the panels side by side, and a caption
    // line "(a) ..." under each panel (as the multi-panel figures of the papers we follow)
    const multi = (W, legendItems, panels, o = {}) => {
      const LH = 0.2, gap = o.gap !== undefined ? o.gap : 0.04, CAP = 0.17;
      const H = LH + 0.02 + Math.max(...panels.map((p) => p[2])) + CAP;
      const total = panels.reduce((a, p) => a + p[1], 0) + gap * (panels.length - 1);
      const draw = (K) => {
        legendRow(offset(K, 0, 0), W, LH, legendItems, { fs: 6.8, gap: o.legendGap || 0.2 });
        let x = (W - total) / 2;
        panels.forEach(([fn, w, h, cap], i) => {
          fn(offset(K, x, LH + 0.02), w, h);
          const letter = "(" + "abcdefgh"[i] + ") ";
          K.T([{ text: letter }, ...(Array.isArray(cap) ? cap : [{ text: cap }])], { x, y: LH + 0.02 + h + 0.01, w, h: 0.14,
            fontSize: 7.5, align: "center" });
          x += w + gap;
        });
      };
      return [W, H, draw];
    };
    const legend5 = [
      { kind: "barline", pol: "BIM", label: POL.BIM.label }, { kind: "barline", pol: "Manual", label: POL.Manual.label },
      { kind: "barline", pol: "Full", label: POL.Full.label },
      { kind: "patch", fill: P.bimLight, label: "BIM hold, 5th–95th pct." },
      { kind: "line", color: P.ink2, width: 0.8, dash: "sysDot", label: "offered load / period" },
      { kind: "line", color: P.ink3, width: 0.7, dash: "dash", label: "GPU capacity" }];
    const legend6 = [
      { kind: "barline", pol: "BIM", label: POL.BIM.label }, { kind: "barline", pol: "Manual", label: POL.Manual.label },
      { kind: "barline", pol: "Full", label: POL.Full.label },
      { kind: "patch", fill: LATE.Full, edge: P.fullDark, dashEdge: true, label: "correct but late" },
      { kind: "line", color: P.ink3, width: 0.7, dash: "dash", label: "GPU capacity" }];
    const legend7 = [
      { kind: "bar", pol: "BIM", label: POL.BIM.label }, { kind: "bar", pol: "Manual", label: "Manual-checked" },
      { kind: "bar", pol: "Full", label: "Full" }, { kind: "bar", pol: "Clone", label: POL.Clone.label }];
    const jobs = [
      ["fig2_trace", 3.45, 1.61, fig2],
      ["fig3_boundaries", 3.45, 1.36, fig3],
      ["fig5_delivery", ...multi(7.1, legend5, [
        [fig5a, W5.a, PH, "Timely results with one slot"], [fig5b, W5.b, PH, "Receipt latency"],
        [fig5c, W5.c, PH, "Slot hold time versus the period"], [fig5d, W5.d, PH, "Early vs. late last read (30 Hz)"]], { gap: 0.03, legendGap: 0.13 })],
      ["fig6_slots", ...multi(7.1, legend6, [
        [fig6a, 2.86, PH, "Timely and late results/s by slots and cap"], [fig6b, 2.02, PH, "Held source storage (time average)"],
        [fig6c, 2.14, PH, "Timely results/s at other deadlines"]], { gap: 0.03 })],
      ["fig7_mixed", ...multi(3.45, legend7, [
        [fig7a, 1.72, PH7, "All four results correct and timely"], [fig7b, 1.72, PH7, "99th-percentile latency"]], { gap: 0.0, legendGap: 0.14 })],
    ];
    for (const [name, w, h, fn] of jobs) if (!only.length || only.includes(name)) await build(name, w, h, fn);
  })();
}
