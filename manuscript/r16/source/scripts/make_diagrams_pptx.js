// Diagrams of the BIM paper as editable PowerPoint slides (one slide per figure, at its printed size).
//
//   node scripts/make_diagrams_pptx.js
//     -> figures/fig1_overview.pptx       Fig. 1   (a) BIM architecture and publication protocol;
//                                                   (b) two lifetimes and three release rules.
// Optional --legacy generates the unused historical mechanism drawing.
//   sh scripts/export_figures_pdf.sh      -> the matching PDFs used by main.tex
//
// Panel captions are part of the slide. Original icons are preserved in assets/ (see its README).

const tb = { TbZoomCode: { name: "TbZoomCode" } };
const pi = { PiGraphicsCardBold: { name: "PiGraphicsCardBold" } };
const { P, offset, build } = require("./figkit");

// =============================================================================================
// Fig. 1a: BIM architecture (OFFLINE | ONLINE split, processes on top with their queues,
// the middleware box in the middle, the GPU at the bottom, colored layer names on the right)
// =============================================================================================
function fig1a(K0, W, H) {
  const K = scaleY(K0, 0.95, 0.14);                 // drawn on a 2.1-in grid, printed 5% shorter below the headers
  const { T, R, L, A, O, I, step, kt } = K;
  const thick = { width: 1.5, head: ["med", "med"] };

  // ---- headers and separators ----
  T("OFFLINE", { x: 0.05, y: 0.02, w: 0.8, h: 0.12, fontSize: 7.5, charSpacing: 0.4 });
  T("ONLINE", { x: 1.1, y: 0.02, w: 0.8, h: 0.12, fontSize: 7.5, charSpacing: 0.4 });
  L(1.0, 0.03, 1.0, 1.42, { color: P.rule, width: 1.0, dash: "dash" });
  L(1.02, 0.505, 3.72, 0.505, { color: P.rule, width: 1.0, dash: "sysDot" });
  L(1.02, 1.345, 3.72, 1.345, { color: P.rule, width: 1.0, dash: "sysDot" });

  // ---- offline column: exported graphs -> alias analysis -> plans ----
  const cx0 = 0.5;
  [[0.10, 0.22], [0.05, 0.27], [0.0, 0.32]].forEach(([dx, y], i) => {
    R({ x: 0.2 + dx, y, w: 0.56, h: 0.27, fill: P.appCard, line: { color: P.appDark, width: 0.75 }, radius: 0.035 });
    if (i === 2) T([{ text: "exported", options: { breakLine: true } }, { text: "graphs" }],
      { x: 0.2, y, w: 0.56, h: 0.27, fontSize: 7, align: "center", wrap: true, lineSpacingMultiple: 0.9 });
  });
  A(cx0 - 0.02, 0.61, cx0 - 0.02, 0.86, Object.assign({ color: P.muted }, thick));
  I(tb.TbZoomCode, cx0 - 0.16, 0.88, 0.3, P.ink);
  T("Alias analysis", { x: 0.02, y: 1.19, w: 0.96, h: 0.16, fontSize: 9, align: "center" });
  A(cx0 + 0.18, 1.03, 1.06, 1.03, Object.assign({ color: P.muted }, thick));
  K.can({ x: 1.07, y: 0.86, w: 0.4, h: 0.36, fill: P.blue });
  T([{ text: "ReadSeal", options: { bold: true, breakLine: true } }, { text: "plans" }],
    { x: 1.07, y: 0.93, w: 0.4, h: 0.27, fontSize: 6.5, color: P.white, align: "center", wrap: true, lineSpacingMultiple: 0.9 });
  A(1.48, 1.07, 1.63, 1.07, Object.assign({ color: P.blue }, thick));

  // ---- processes: producer and four recipients ----
  const top = 0.14, bh = 0.31;
  const box = (x, w, fill, small, big, bigFs = 7.5) => {
    R({ x, y: top, w, h: bh, fill, radius: 0.035 });
    T([{ text: small, options: { fontSize: 6, breakLine: true } }, { text: big, options: { fontSize: bigFs } }],
      { x, y: top + 0.01, w, h: bh - 0.02, color: P.white, align: "center", wrap: true, lineSpacingMultiple: 0.95 });
  };
  box(1.06, 0.46, P.appDark, "Producer", "BEV fusion", 7);
  const names = ["Detection", "Tracking", "Planning", "Logging"];
  const rw = 0.465, rg = 0.08, rx0 = 1.6;
  const cxs = names.map((_, i) => rx0 + i * (rw + rg) + rw / 2);
  names.forEach((n, i) => box(rx0 + i * (rw + rg), rw, P.app, `Recipient ${i + 1}`, n));

  // producer: write k into a free slot and commit it through the runtime
  A(1.5, 0.46, 1.72, 0.955, Object.assign({ color: P.app }, thick));
  step(1, 1.13, 0.62); T(kt("write k"), { x: 1.205, y: 0.565, w: 0.3, h: 0.11, fontSize: 6 });
  step(2, 1.13, 0.78); T("commit", { x: 1.205, y: 0.725, w: 0.3, h: 0.11, fontSize: 6 });

  // recipients: accept k and enroll readers A and C (queue), return the borrow after the last read
  const qw = 0.22, qc = 0.09, qy = 0.57;
  const content = [["C", "A"], ["C"], ["C", "A"], ["C"]];      // top to bottom; A's read already done in 2 and 4
  const full = { A: "engine A", C: "graph C" };                // recipient 1 names its readers; the others are simplified
  cxs.forEach((cx, i) => {
    A(cx, top + bh + 0.01, cx, qy - 0.01, Object.assign({ color: P.app }, thick));
    const w = i === 0 ? 0.33 : qw, qx = i === 0 ? cx + 0.03 : cx;          // wider queue, clear of the producer's arrow
    const x0 = qx - w / 2, x1 = qx + w / 2, yb = qy + 3 * qc;
    L(x0, qy, x0, yb, { color: P.ink2, width: 0.75 });
    L(x1, qy, x1, yb, { color: P.ink2, width: 0.75 });
    L(x0, yb, x1, yb, { color: P.ink2, width: 0.75 });
    L(x0, qy + qc, x1, qy + qc, { color: P.ink2, width: 0.75 });
    L(x0, qy + 2 * qc, x1, qy + 2 * qc, { color: P.ink2, width: 0.75 });
    const items = content[i];
    items.forEach((lab, j) => {
      const cell = 3 - items.length + j;                         // fill from the bottom cell up
      const cy = qy + cell * qc + qc / 2, s = 0.076;
      if (i === 0) {
        const bw = w - 0.03;
        R({ x: qx - bw / 2, y: cy - s / 2, w: bw, h: s, fill: P.sqC });
        T(full[lab], { x: qx - bw / 2, y: cy - s / 2, w: bw, h: s, fontSize: 5.5, bold: true, color: P.white, align: "center" });
      } else {
        R({ x: cx - s / 2, y: cy - s / 2, w: s, h: s, fill: P.sqC });
      }
    });
    A(cx, yb + 0.01, cx, 0.955, Object.assign({ color: P.blue }, thick));
  });
  step(3, cxs[0] + 0.275, 0.6);
  step(4, cxs[0] + 0.275, 0.86);
  step(6, rx0 + 3 * (rw + rg) + rw - 0.07, top - 0.065, 0.12);
  T(kt("result still carries identity k"), { x: 2.475, y: 0.02, w: 1.08, h: 0.11, fontSize: 6.5, bold: true, align: "right" });

  // ---- the middleware box ----
  R({ x: 1.64, y: 0.965, w: 2.06, h: 0.285, fill: P.runtime, radius: 0.05 });
  T([{ text: "BIM runtime", options: { fontSize: 9, breakLine: true } },
    { text: "track publications · hold borrows · reuse slots", options: { fontSize: 6.2 } }],
  { x: 1.64, y: 0.975, w: 2.06, h: 0.265, color: P.white, align: "center", wrap: true, lineSpacingMultiple: 0.95 });

  // ---- GPU layer: slot pool in shared device memory ----
  const gx = 2.25;
  A(gx, 1.26, gx, 1.515, Object.assign({ color: P.blue }, thick));
  [["A", P.sqC], ["C", P.sqC]].forEach(([lab, fill], j) => {
    const s = 0.076, x = gx + 0.07 + j * 0.09, y = 1.35;
    R({ x, y, w: s, h: s, fill });
    T(lab, { x, y, w: s, h: s, fontSize: 5.5, bold: true, color: P.white, align: "center" });
  });
  T(kt("read k through a mapped view (CUDA IPC)"), { x: gx + 0.26, y: 1.34, w: 1.4, h: 0.1, fontSize: 6.2, color: P.ink2 });
  I(pi.PiGraphicsCardBold, 1.1, 1.44, 0.46, P.ink, 0.46);
  R({ x: 1.66, y: 1.525, w: 2.04, h: 0.37, fill: P.white, line: { color: P.ink2, width: 0.75 }, radius: 0.04 });
  R({ x: 1.71, y: 1.555, w: 1.24, h: 0.31, fill: P.pubK, line: { color: "BF9000", width: 0.75 }, radius: 0.02 });
  T([{ text: "slot 0: publication ", options: { fontSize: 7 } }, { text: "k", options: { fontSize: 7, italic: true, breakLine: true } },
    { text: "1×512×180×180 fp32 · 63.3 MiB", options: { fontSize: 6, color: P.muted } }],
  { x: 1.71, y: 1.56, w: 1.24, h: 0.3, color: P.ink, align: "center", wrap: true, lineSpacingMultiple: 0.95 });
  R({ x: 3.0, y: 1.555, w: 0.65, h: 0.31, fill: P.white, line: { color: P.rule, width: 0.75, dashType: "dash" }, radius: 0.02 });
  T([{ text: "slot 1", options: { fontSize: 6.5, breakLine: true } }, { text: "optional", options: { fontSize: 6 } }],
    { x: 3.0, y: 1.56, w: 0.65, h: 0.3, color: P.muted, align: "center", wrap: true, lineSpacingMultiple: 0.95 });
  step(5, 1.745, 1.99);
  T([{ text: "slot 0 now stores " }, { text: "k", options: { italic: true } }, { text: "+1: every borrow returned" }],
    { x: 1.83, y: 1.935, w: 1.9, h: 0.11, fontSize: 6.5, bold: true });

  // key for the reader squares
  const key = (y, lab, fill, text) => {
    const s = 0.076;
    R({ x: 0.08, y, w: s, h: s, fill });
    T(lab, { x: 0.08, y, w: s, h: s, fontSize: 5.5, bold: true, color: P.white, align: "center" });
    T(text, { x: 0.18, y: y - 0.02, w: 0.85, h: 0.11, fontSize: 6, color: P.ink2 });
  };
  key(1.83, "", P.sqC, "pending reader (enrolled)");
  step(3, 0.118, 2.008, 0.1); T("enroll readers", { x: 0.18, y: 1.95, w: 0.55, h: 0.11, fontSize: 6, color: P.ink2 });
  step(4, 0.755, 2.008, 0.1); T("return borrow", { x: 0.815, y: 1.95, w: 0.55, h: 0.11, fontSize: 6, color: P.ink2 });

  // ---- layer names ----
  T("Processes", { x: 3.8, y: 0.22, w: 0.6, h: 0.16, fontSize: 9, color: P.app });
  T("example roles", { x: 3.8, y: 0.37, w: 0.6, h: 0.1, fontSize: 6.3, color: P.app });
  T([{ text: "BIM +", options: { bold: true, breakLine: true } }, { text: "ReadSeal", options: { bold: true } }],
    { x: 3.8, y: 0.96, w: 0.6, h: 0.3, fontSize: 9, color: P.blue, wrap: true, lineSpacingMultiple: 0.9 });
  T("GPU", { x: 3.8, y: 1.63, w: 0.6, h: 0.16, fontSize: 9, color: P.gpu });
}

// =============================================================================================
// Fig. 1b: two lifetimes and three release rules (blocks, braces and captions)
// =============================================================================================
function fig1b(K0, W, H) {
  const K = scaleY(K0, 0.95, 0.04);
  const { T, R, L, A, hatch, kt, ktb } = K;
  const { tw } = require("./figkit");
  const X0 = 0.74, X1 = W - 0.05, X = (t) => X0 + t * (X1 - X0);
  const bh = 0.17;
  const edge = { color: P.blockEdge, width: 0.6 };
  const block = (t0, t1, y, fill, text, o = {}) => {
    R({ x: X(t0), y, w: X(t1) - X(t0), h: bh, fill, line: o.line || edge });
    if (o.hatch) hatch(X(t0), y, X(t1) - X(t0), bh, o.hatch, 0.04, 0.45);
    if (text) T(kt(text), { x: X(t0), y, w: X(t1) - X(t0), h: bh, fontSize: o.fs || 6.5, align: "center", color: o.color || P.ink,
      bold: !!o.bold });
  };
  const dots = (t, y) => T("•••", { x: X(t) - 0.08, y, w: 0.16, h: bh, fontSize: 6, align: "center", color: P.ink });
  const lane = (y, text, o = {}) => T(text, Object.assign({ x: 0.0, y, w: X0 - 0.06, h: bh, fontSize: 7.5, align: "right" }, o));
  const reader = (y, letter, what) => T([{ text: letter, options: { bold: true, fontSize: 7.5, breakLine: true } },
    { text: what, options: { fontSize: 6, color: P.ink2 } }],
  { x: 0.0, y: y - 0.04, w: X0 - 0.06, h: bh + 0.08, align: "right", wrap: true, lineSpacingMultiple: 0.88 });
  const fitF = (str, w, f0) => { let f = f0; while (f > 5.2 && tw(str, f) > w) f -= 0.2; return f; };

  const tA = 0.16, tC0 = 0.33, tC1 = 0.49;
  // ---- two readers in one recipient process ----
  const yA = 0.05, yC = 0.28;
  reader(yA, "A", "TensorRT engine");
  reader(yC, "C", "exported graph");
  block(0, tA, yA, P.read, "read k");
  block(tA, 0.42, yA, P.priv, "private");
  block(0, tC0, yC, P.white, "not yet submitted", { line: { color: P.muted, width: 0.6, dashType: "dash" }, color: P.muted, fs: 6 });
  block(tC0, tC1, yC, P.read, "read k");
  block(tC1, 0.83, yC, P.priv, "private suffix");
  dots(0.88, yC);
  block(0.91, 1.0, yC, P.priv, "");
  // both lifetimes start with the work on k; storage ends at the last read, identity only at delivery
  const yS = yC + bh + 0.13, yI = yS + 0.2, lw = X(1) - X(0);
  const sLab = "storage lifetime: until the last read completes", iLab = "provenance lifetime: identity k kept until delivery";
  T(kt(sLab), { x: X(0), y: yS - 0.12, w: lw, h: 0.1, fontSize: fitF(sLab, lw, 6.2), color: P.readEdge });
  L(X(0), yS, X(tC1), yS, { color: P.readEdge, width: 1.0 });
  L(X(0), yS - 0.03, X(0), yS + 0.03, { color: P.readEdge, width: 1.0 });
  L(X(tC1), yS - 0.03, X(tC1), yS + 0.03, { color: P.readEdge, width: 1.0 });
  T(kt(iLab), { x: X(0), y: yI - 0.12, w: lw, h: 0.1, fontSize: fitF(iLab, lw, 6.2), color: P.bimDark });
  L(X(0), yI - 0.03, X(0), yI + 0.03, { color: P.bimDark, width: 1.0 });
  A(X(0), yI, X(1) + 0.03, yI, { color: P.bimDark, width: 1.0 });
  T("Two readers in one recipient process", { x: 0, y: yI + 0.07, w: W, h: 0.13, fontSize: 7, align: "center" });

  // ---- slot 0 under three release rules ----
  const y1 = 1.08, y2 = y1 + 0.235, y3 = y2 + 0.235;
  lane(y1, "stream-only", { color: P.bad });
  lane(y2, "BIM", { color: P.blue, bold: true });
  lane(y3, "Full");
  block(0, tA, y1, P.pubK, "k", { bold: true });
  block(tA, 1.0, y1, P.pubK1, "");
  T(kt("k+1"), { x: X(tA) + 0.03, y: y1, w: 0.3, h: bh, fontSize: 6.5, bold: true });
  R({ x: X(tC0), y: y1 - 0.01, w: X(tC1) - X(tC0), h: bh + 0.02, fill: null, line: { color: P.bad, width: 1.0 } });
  T(kt("✗ C reads k+1"), { x: X(tC1) + 0.03, y: y1, w: 0.8, h: bh, fontSize: 6.5, color: P.bad, bold: true });
  block(0, tC1, y2, P.pubK, "k", { bold: true });
  block(tC1, 1.0, y2, P.pubK1, "");
  T(kt("✓ free for k+1"), { x: X(tC1) + 0.03, y: y2, w: 0.8, h: bh, fontSize: 6.5, color: P.blue, bold: true });
  block(0, tC1, y3, P.pubK, "k", { bold: true });
  block(tC1, 1.0, y3, P.pubK, "", { hatch: "BF9000" });
  { const lw2 = 0.52, cxm = (X(tC1) + X(1.0)) / 2;
    T("held, unread", { x: cxm - lw2 / 2, y: y3 + 0.035, w: lw2, h: bh - 0.07, fontSize: 6.5, align: "center", fill: { color: P.pubK } }); }
  const g0 = 0.04, g1 = y3 + bh + 0.03;
  [[tA, "A finishes\nreading", P.bad], [tC1, "last source read\ncompletes", P.blue], [1.0, "outputs\ncomplete", P.ink2]].forEach(([t, lab, col]) => {
    L(X(t), g0, X(t), (t === tA ? yA : yC) + bh + 0.02, { color: col, width: 0.6, dash: "sysDot" });
    L(X(t), y1 - 0.03, X(t), g1, { color: col, width: 0.6, dash: "sysDot" });
    const [a, b] = lab.split("\n");
    const right = t === 1.0;
    T([...ktb(a), ...kt(b)], { x: right ? X(t) - 0.7 : X(t) - 0.35, y: g1 + 0.01, w: 0.7,
      h: 0.2, fontSize: 6, align: right ? "right" : "center", color: col, wrap: true, lineSpacingMultiple: 0.9 });
  });
  T("What slot 0 holds under three release rules", { x: 0, y: g1 + 0.21, w: W, h: 0.13, fontSize: 7, align: "center" });
}

// a view of the kit that maps y to y0 + (y - y0) * f below y0 (heights scale by f; fonts do not)
function scaleY(K, f, y0) {
  const Y = (y) => (y <= y0 ? y : y0 + (y - y0) * f);
  const box = (o) => Object.assign({}, o, { y: Y(o.y), h: Y(o.y + o.h) - Y(o.y) });
  return Object.assign({}, K, {
    T: (t, o = {}) => K.T(t, "y" in o ? box(o) : o),
    R: (o) => K.R(box(o)),
    L: (x1, y1, x2, y2, o) => K.L(x1, Y(y1), x2, Y(y2), o),
    A: (x1, y1, x2, y2, o) => K.A(x1, Y(y1), x2, Y(y2), o),
    path: (pts, o) => K.path(pts.map((p) => (Array.isArray(p) ? [p[0], Y(p[1])] : { q: [p.q[0], Y(p.q[1])], to: [p.to[0], Y(p.to[1])] })), o),
    O: (cx, cy, d, fill, line, dy) => K.O(cx, Y(cy), d, fill, line, dy),
    I: (Comp, x, y, s0, color, sy) => K.I(Comp, x, Y(y), s0, color, (sy || s0) * f),
    can: (o) => K.can(box(o)),
    step: (n, cx, cy, d) => K.step(n, cx, Y(cy), d),
    brace: (xa, xb, y, depth = 0.1, o) => K.brace(xa, xb, Y(y), depth * f, o),
    hatch: (x0, y0, w, h, color, d, width, dir) => K.hatch(x0, Y(y0), w, Y(y0 + h) - Y(y0), color, d, width, dir),
  });
}

// =============================================================================================
// Legacy mechanism drawing: how ReadSeal changes a recipient's invocation (original behavior on the
// left, modified behavior on the right, with a dotted region for what is built once and cached)
// =============================================================================================
function fig4(K0, W, H) {
  const K = scaleY(K0, 0.85, 0.2);
  const { T, R, L, A, path, kt } = K;
  const { tw } = require("./figkit");
  const fs = 6.5, edge = { color: P.ink, width: 0.75 };
  const lines = (...ls) => ls.flatMap((l, i) => { const runs = kt(l);
    if (i < ls.length - 1) runs[runs.length - 1] = Object.assign({}, runs[runs.length - 1],
      { options: Object.assign({}, runs[runs.length - 1].options, { breakLine: true }) });
    return runs; });
  const fitFs = (strs, w, f0) => { let f = f0; while (f > 5.2 && Math.max(...strs.map((x) => tw(x, f))) > w - 0.05) f -= 0.25; return f; };
  const bx = (x, y, w, h, strs, o = {}) => {
    R({ x, y, w, h, fill: P.white, line: o.dash ? { color: P.ink, width: 0.75, dashType: "dash" } : edge,
      radius: o.round ? Math.min(0.05, h / 2) : 0.012 });
    T(lines(...strs), { x, y, w, h, fontSize: fitFs(strs, w, o.fs || fs), align: "center", wrap: true, lineSpacingMultiple: 0.92,
      color: o.color || P.ink });
  };
  const note = (strs, o) => T(lines(...strs).map((r) => Object.assign({}, r, { options: Object.assign({}, r.options, { italic: true }) })),
    Object.assign({ fontSize: fitFs(strs, o.w + 0.05, o.fs || 6.0), color: P.ink, wrap: true, lineSpacingMultiple: 0.92 }, o));

  // ---- divider and headers ----
  L(1.18, 0.04, 1.18, 2.28, { color: P.ink, width: 0.75 });
  T("Stream-only release", { x: 0.02, y: 0.02, w: 1.14, h: 0.16, fontSize: 8.5, italic: true });
  T("With ReadSeal", { x: 1.26, y: 0.02, w: 1.0, h: 0.16, fontSize: 8.5, italic: true });

  // ---- left: stream-only release tracks submitted work only ----
  bx(0.30, 0.30, 0.56, 0.15, ["publication k"], { round: true });
  A(0.58, 0.455, 0.58, 0.60);
  bx(0.04, 0.60, 1.10, 0.26, ["invocation on k: A runs,", "C not yet submitted"]);
  A(0.58, 0.865, 0.58, 1.03);
  bx(0.04, 1.03, 1.10, 0.26, ["track submitted work only", "(A's stream events)"]);
  A(0.58, 1.295, 0.58, 1.46);
  bx(0.04, 1.46, 1.10, 0.26, ["A's stream idle:", "slot takes k+1"]);
  note(["✗ no event exists for C,", "which then reads k+1"], { x: 0.04, y: 1.80, w: 1.10, h: 0.26, color: P.bad, align: "center" });

  // ---- right: the plan, built once per model version (dotted) ----
  R({ x: 2.30, y: 0.24, w: 1.12, h: 1.0, fill: null, line: { color: P.ink, width: 0.75, dashType: "sysDot" } });
  T("Plan, once per model version", { x: 2.33, y: 0.255, w: 1.06, h: 0.11, fontSize: 6.0, italic: true, align: "right" });
  bx(2.36, 0.42, 0.46, 0.15, ["graph C"]);
  bx(2.88, 0.375, 0.50, 0.22, ["reader set: A, C", "binding tokens"], { fs: 6 });
  A(2.59, 0.575, 2.59, 0.74);
  note(["alias analysis"], { x: 2.63, y: 0.61, w: 0.6, h: 0.11 });
  bx(2.36, 0.74, 1.03, 0.26, ["prefix | private suffix", "prefix: through the last source read"], { fs: 6 });

  // ---- right: one invocation on k ----
  bx(1.46, 0.30, 0.56, 0.15, ["publication k"], { round: true });
  A(1.74, 0.455, 1.74, 0.56);
  bx(1.26, 0.56, 0.96, 0.26, ["execution", "matches plan?"], { round: true });
  A(1.40, 0.825, 1.40, 1.10);
  note(["binding tokens checked at", "acceptance and stage entry;", "else reject"], { x: 1.45, y: 0.835, w: 0.80, h: 0.26 });
  bx(1.26, 1.10, 0.96, 0.15, ["enroll A and C"]);
  A(1.61, 1.255, 1.61, 1.36);
  path([[2.05, 1.255], [2.05, 1.305], [2.35, 1.305], [2.35, 1.36]], { arrow: true });
  path([[2.70, 1.005], [2.70, 1.335]], { arrow: true, dash: "dash" });
  note(["run"], { x: 2.73, y: 1.13, w: 0.25, h: 0.1 });
  bx(1.26, 1.36, 0.70, 0.15, ["A: TensorRT engine"]);
  bx(2.04, 1.36, 0.62, 0.15, ["C: prefix"]);
  A(2.665, 1.435, 2.735, 1.435);
  bx(2.74, 1.36, 0.68, 0.15, ["C: private suffix"]);
  // the two completion events; C's suffix goes on regardless
  A(1.61, 1.515, 1.61, 1.60);
  bx(1.26, 1.60, 0.70, 0.26, ["input-consumed", "event"], { round: true });
  A(2.35, 1.515, 2.35, 1.60);
  bx(2.04, 1.60, 0.62, 0.26, ["prefix-completion", "event"], { round: true });
  A(3.08, 1.515, 3.08, 1.60);
  bx(2.74, 1.60, 0.68, 0.26, ["publish result", "with identity k"]);
  A(1.61, 1.865, 1.74, 2.0);
  A(2.35, 1.865, 2.20, 2.0);
  bx(1.26, 2.0, 1.40, 0.26, ["both source reads complete:", "return this recipient's borrow"]);
}

(async () => {
  // Fig. 1 on one slide: (a) and (b) side by side with their captions underneath
  await build("fig1_overview", 7.12, 2.18, (K, W, H) => {
    fig1a(offset(K, 0, 0), 4.4, 2.0);
    fig1b(offset(K, 4.52, 0), 2.6, 2.0);
    K.T("(a) BIM architecture and per-publication protocol", { x: 0, y: 2.03, w: 4.4, h: 0.14, fontSize: 7.5, align: "center" });
    K.T([...K.kt("(b) Two lifetimes of publication k and three release rules")], { x: 4.52, y: 2.03, w: 2.6, h: 0.14, fontSize: 7.5,
      align: "center" });
  });
  if (process.argv.includes("--legacy")) await build("fig4_readseal", 3.45, 2.0, fig4);
})();
