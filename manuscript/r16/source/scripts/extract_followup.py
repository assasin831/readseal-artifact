#!/usr/bin/env python3
"""Regenerate the data of Section V-D (jitter, mixed recipients, clone-on-accept) from the follow-up archives.

    python3 scripts/extract_followup.py <ispa2026-jitter-manual-108.zip> \
                                        <ispa2026-clone-168.zip>

Archive SHA-256: dbd10557648361efd53b1616765c6c179f8787523a5fcffd823a800ced6a6ad8 (follow-up campaign,
108 formal runs) and 9f07b1c1cb85ca2b003387eb9e469225e7805ff6fa730ce27d60d2edc45cf9d1 (earlier clone-on-accept
rate sweep, 168 formal runs). The two campaigns are never pooled or paired with each other.

Writes
  data/mixed_30hz.csv         Fig. 6   condition x policy means and pointwise t95 intervals (n = 6 runs)
  data/mixed_30hz_paired.csv  Sec. V-D paired differences against BIM (n = 6 paired runs)
  data/clone_rates.csv        Sec. V-D earlier campaign: timely results/s by rate, with clone-on-accept

Artifact labels: auto-batched = BIM, manual-checked = Manual-checked (CSV key Manual, checked by ReadSeal's own
binding and stage guards), manual-early = Manual (earlier campaign), manual-full = Full, copy-in = Clone
(clone-on-accept). Every value is copied from the archives' summary files (whose intervals this script also
recomputes from the per-run rows as a check); nothing is digitized or estimated.
"""
import csv
import io
import math
import os
import statistics as st
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
POL = {"auto-batched": "BIM", "manual-checked": "Manual", "manual-early": "Manual", "manual-full": "Full",
       "copy-in": "Clone"}
ORDER = {"Full": 0, "BIM": 1, "Manual": 2, "Clone": 3}
T975_DF5 = 2.570581835636305


def members(zpath):
    z = zipfile.ZipFile(zpath)
    return z, z.namelist()


def read_csv(z, names, suffix):
    hits = [n for n in names if n == suffix or n.endswith("/" + suffix)]
    if len(hits) != 1:
        sys.exit(f"expected one member ending in {suffix}, found {hits}")
    return list(csv.DictReader(io.StringIO(z.read(hits[0]).decode("utf-8"))))


def write(name, header, fields, rows):
    with open(os.path.join(DATA, name), "w", newline="") as f:
        for h in header:
            f.write("# " + h + "\n")
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote data/" + name)


def f4(x):
    return "" if x in ("", None) or (isinstance(x, float) and math.isnan(x)) else f"{float(x):.4f}"


def check_t95(per_run, summary, key_cols, metric_col="metric"):
    """Recompute every mean and pointwise t95 interval of the summary from the per-run rows."""
    worst = 0.0
    for s in summary:
        vals = [float(r[s[metric_col]]) for r in per_run
                if all(r[k] == s[k] for k in key_cols) and r.get(s[metric_col], "") != ""]
        if len(vals) < 2:
            continue
        m = st.mean(vals)
        h = T975_DF5 * st.stdev(vals) / math.sqrt(len(vals))
        for a, b in ((m, s["mean"]), (m - h, s["low"]), (m + h, s["high"])):
            if b != "":
                worst = max(worst, abs(a - float(b)) / max(1.0, abs(float(b))))
    if worst > 1e-9:
        sys.exit(f"summary intervals do not match the per-run rows (relative difference {worst:g})")
    return worst


def main(new_zip, old_zip):
    # ---------------- follow-up campaign: jitter x recipient mix, 30 Hz, one slot ----------------
    z, names = members(new_zip)
    per_run = read_csv(z, names, "per_run.csv")
    summary = read_csv(z, names, "summary_t95.csv")
    paired = read_csv(z, names, "paired_t95.csv")
    if len(per_run) != 108:
        sys.exit(f"expected 108 formal runs, found {len(per_run)}")
    check_t95(per_run, summary, ("condition", "method"))

    S = {(s["condition"], s["method"], s["metric"]): s for s in summary}
    conds = []
    for r in per_run:
        if r["condition"] not in conds:
            conds.append(r["condition"])
    order_c = ["homogeneous-periodic-hz30", "heterogeneous-periodic-hz30", "homogeneous-jitter-hz30",
               "heterogeneous-jitter-hz30", "late-periodic-hz30"]
    rows = []
    for c in order_c:
        mix, arrival = c.split("-")[0], c.split("-")[1]
        for m in ("manual-full", "auto-batched", "manual-checked", "copy-in"):
            if (c, m, "full_publication_timely_fraction") not in S:
                continue
            g = lambda metric, k="mean": S[(c, m, metric)][k]   # noqa: E731
            pct = lambda metric, k: f4(100.0 * float(g(metric, k)))   # noqa: E731
            runs = [r for r in per_run if r["condition"] == c and r["method"] == m]
            rows.append(dict(
                mix={"homogeneous": "same", "heterogeneous": "mixed", "late": "all-late"}[mix], arrival=arrival,
                policy=POL[m],
                complete_timely_pct=pct("full_publication_timely_fraction", "mean"),
                ct_lo=pct("full_publication_timely_fraction", "low"), ct_hi=pct("full_publication_timely_fraction", "high"),
                results_per_s=f4(g("recipient_timely_goodput_hz")), rs_lo=f4(g("recipient_timely_goodput_hz", "low")),
                rs_hi=f4(g("recipient_timely_goodput_hz", "high")),
                p99_ms=f4(g("full_publication_p99_ms")), p99_lo=f4(g("full_publication_p99_ms", "low")),
                p99_hi=f4(g("full_publication_p99_ms", "high")), p50_ms=f4(g("full_publication_p50_ms")),
                incomplete_per_run=f4(g("incomplete_publications")),
                device_peak_mib=f"{float(g('sampled_device_peak_mib')):.0f}",
                runs=len(runs), condition=c))
    write("mixed_30hz.csv", [
        "Follow-up campaign at 30 Hz: one slot, per-recipient queue of 8, no cap, 4 recipients, 100 ms deadline;",
        "10 s warm-up and 30 s measurement per run (900 scheduled publications); 6 runs per cell, frozen random order.",
        "mix: same = four copies of the composition (engine A + view B + graph C); mixed = engine A alone, the head alone,",
        "the composition, and the composition with a late source read; all-late = four late-read compositions.",
        "arrival: periodic, or jitter = each arrival displaced by a frozen uniform offset in [0, 0.8 T], T = 1/30 s.",
        "complete_timely_pct = % of all scheduled publications whose four results are correct and received within",
        "100 ms (drops count against it); results_per_s = correct, timely results/s summed over the four recipients;",
        "p99_ms = mean over runs of the per-run 99th percentile of complete publications' latency; ct/rs/p99 lo, hi =",
        "pointwise 95% t intervals (df 5); device_peak_mib = device memory peak sampled about every 0.5 s.",
        "Generated by scripts/extract_followup.py from ispa_reviewer_results_20260927_final1.zip; do not edit by hand.",
    ], ["mix", "arrival", "policy", "complete_timely_pct", "ct_lo", "ct_hi", "results_per_s", "rs_lo", "rs_hi",
        "p99_ms", "p99_lo", "p99_hi", "p50_ms", "incomplete_per_run", "device_peak_mib", "runs", "condition"], rows)

    prow = []
    want = {"full_publication_timely_fraction": ("complete_timely_pp", 100.0),
            "recipient_timely_goodput_hz": ("results_per_s", 1.0), "full_publication_p99_ms": ("p99_ms", 1.0),
            "sampled_device_peak_mib": ("device_peak_mib", 1.0)}
    for p in paired:
        if p["metric"] not in want:
            continue
        name, sc = want[p["metric"]]
        a, _, b = p["contrast"].partition(" minus ")
        prow.append(dict(condition=p["condition"], contrast=f"{POL[a]} - {POL[b]}", metric=name,
                         mean=f4(sc * float(p["mean"])), lo=f4(sc * float(p["low"])), hi=f4(sc * float(p["high"])),
                         pairs=p["n_observed"]))
    prow.sort(key=lambda r: (order_c.index(r["condition"]), r["contrast"], r["metric"]))
    write("mixed_30hz_paired.csv", [
        "Paired differences (first policy minus BIM) in the follow-up campaign; lo, hi = pointwise 95% t intervals",
        "over 6 paired runs (df 5), not adjusted for multiplicity and not equivalence tests.",
        "complete_timely_pp in percentage points; results_per_s in results/s; p99_ms in ms; device_peak_mib in MiB.",
        "Generated by scripts/extract_followup.py from ispa_reviewer_results_20260927_final1.zip; do not edit by hand.",
    ], ["condition", "contrast", "metric", "mean", "lo", "hi", "pairs"], prow)

    # ---------------- earlier campaign: clone-on-accept across source rates ----------------
    z2, names2 = members(old_zip)
    s2 = read_csv(z2, names2, "formal/analysis/summary_t95.csv")
    p2 = read_csv(z2, names2, "formal/analysis/paired_t95.csv")
    runs2 = read_csv(z2, names2, "formal/analysis/per_run.csv")
    if len(runs2) != 168:
        sys.exit(f"expected 168 formal runs in the earlier campaign, found {len(runs2)}")
    S2 = {(r["condition"], r["method"], r["metric"]): r for r in s2}
    P2 = {(r["condition"], r["a_method"], r["b_method"], r["metric"]): r for r in p2}
    rows2 = []
    for c in ("base-r1-hz10", "base-r1-hz15", "base-r1-hz20", "base-r1-hz25", "base-r1-hz30", "base-r1-hz40",
              "late-r1-hz30"):
        for m in ("manual-full", "auto-batched", "manual-early", "copy-in"):
            t = S2[(c, m, "timely_100ms_hz")]
            d = P2.get((c, m, "auto-batched", "timely_100ms_hz"))
            rows2.append(dict(graph="late-read" if c.startswith("late") else "base", rate=c.split("hz")[1],
                              policy=POL[m], results_per_s=f4(t["mean"]), rs_lo=f4(t["ci95_low"]),
                              rs_hi=f4(t["ci95_high"]),
                              minus_bim=f4(d["mean"]) if d else "", minus_bim_lo=f4(d["ci95_low"]) if d else "",
                              minus_bim_hi=f4(d["ci95_high"]) if d else "",
                              p99_ms=f4(S2[(c, m, "p99_latency_ms")]["mean"]),
                              device_peak_mib=f"{float(S2[(c, m, 'device_peak_mib')]['mean']):.0f}", condition=c))
    write("clone_rates.csv", [
        "Earlier campaign (Sept. 23): one slot, per-recipient queue of 8, no cap, four identical recipients, periodic",
        "arrivals, 10 s warm-up and 30 s measurement, 6 runs per cell (168 runs). graph: base head, or late-read head",
        "(last source read at op 288/289). results_per_s = correct results received within 100 ms of the planned",
        "arrival, per second, summed over the recipients; minus_bim = paired difference to BIM with its pointwise 95%",
        "t interval (df 5). Not pooled or paired with the follow-up campaign of data/mixed_30hz.csv.",
        "Generated by scripts/extract_followup.py from ispa_copyin_performance_results_20260923.zip; do not edit by hand.",
    ], ["graph", "rate", "policy", "results_per_s", "rs_lo", "rs_hi", "minus_bim", "minus_bim_lo", "minus_bim_hi",
        "p99_ms", "device_peak_mib", "condition"], rows2)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
