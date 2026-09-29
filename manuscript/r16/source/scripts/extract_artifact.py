#!/usr/bin/env python3
"""Regenerate the figure data in data/ from the public artifact.

    python3 scripts/extract_artifact.py <ispa2026-rate-slots-evidence.zip | extracted directory>

The preserved rate/slots archive is in the artifact repository
(https://github.com/assasin831/readseal-artifact/tree/ispa2026-r15/archives). It contains the rate-sweep
and late-read campaigns (E1/E2, 144 runs), their per-publication and per-recipient timelines, and the
earlier 96-run slots window with its eight-cutoff deadline re-scoring (prior_v11/evidence).

Writes
  data/rate_sweep.csv      Fig. 4a-c  one slot, no cap, 10-40 Hz               (E1, 108 runs)
  data/late_read.csv       Fig. 4d    base head vs. last read at op 288/289    (E2, 36 runs)
  data/slots_30hz.csv      Fig. 5a/b  slots x cap x policy at 30 Hz            (96-run window)
  data/deadlines_30hz.csv  Fig. 5c    goodput re-scored at 80-200 ms deadlines (same 96 runs)
  data/trace_20hz.csv      Fig. 2     one-slot trace, 20 Hz, repetition 0, window starting 1,000 ms
                                      after the measured cohort begins

Artifact labels: auto-batched = BIM, manual-early = Manual, manual-full = Full.
Every value is copied or averaged from the artifact; nothing is digitized or estimated.
"""
import csv
import io
import json
import os
import statistics as st
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
POL = {"auto-batched": "BIM", "manual-early": "Manual", "manual-full": "Full"}
ORDER = {"BIM": 0, "Manual": 1, "Full": 2}
TRACE_T0_MS = 1000.0      # start of the plotted trace window, ms after the measured cohort starts
TRACE_SPAN_MS = 255.0


class Source:
    """Reads members of the V12 archive from the zip file or from an extracted directory."""

    def __init__(self, path):
        self.zip = zipfile.ZipFile(path) if zipfile.is_zipfile(path) else None
        self.dir = None if self.zip else path
        names = self.zip.namelist() if self.zip else [
            os.path.relpath(os.path.join(d, f), path) for d, _, fs in os.walk(path) for f in fs]
        self.names = names

    def _find(self, suffix):
        hits = [n for n in self.names if n.replace("\\", "/").endswith(suffix)]
        if len(hits) != 1:
            sys.exit(f"expected exactly one archive member ending in {suffix}, found {hits}")
        return hits[0]

    def text(self, suffix):
        name = self._find(suffix)
        if self.zip:
            return self.zip.read(name).decode("utf-8")
        with open(os.path.join(self.dir, name), encoding="utf-8") as f:
            return f.read()

    def csv(self, suffix):
        return list(csv.DictReader(io.StringIO(self.text(suffix))))

    def json(self, suffix):
        return json.loads(self.text(suffix))


def write(name, header_lines, fields, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="") as f:
        for line in header_lines:
            f.write("# " + line + "\n")
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote", os.path.relpath(path, ROOT), f"({len(rows)} rows)")


def r3(x):
    return f"{x:.3f}"


def main(src_path):
    src = Source(src_path)
    means = src.csv("E1_E2/E1_E2_method_means.csv")
    holds = src.csv("gpu_independent_local/E1_E2_hold_diagnostics.csv")

    # per-run 5th/95th percentiles of the source hold, averaged over the six runs of a condition
    hq = {}
    for h in holds:
        key = (h["experiment"], h["late"], int(h["rate_hz"]), POL[h["method"]])
        hq.setdefault(key, []).append((float(h["hold_p05_ms"]), float(h["hold_p95_ms"])))
    hq = {k: (st.mean(a for a, _ in v), st.mean(b for _, b in v)) for k, v in hq.items()}

    # ---- rate sweep (E1) ----
    rows = []
    for m in means:
        if m["experiment"] != "e1" or m["method"] not in POL:
            continue
        pol, rate = POL[m["method"]], int(m["rate_hz"])
        p5, p95 = hq[("e1", "False", rate, pol)]
        rows.append(dict(rate=rate, policy=pol, goodput=r3(float(m["goodput_hz_mean"])),
                         goodput_ci_lo=r3(float(m["goodput_pointwise_ci95_low"])),
                         goodput_ci_hi=r3(float(m["goodput_pointwise_ci95_high"])),
                         hold_mean_ms=r3(float(m["source_hold_mean_ms_mean"])), hold_p5_ms=r3(p5), hold_p95_ms=r3(p95),
                         receipt_mean_ms=r3(float(m["receipt_mean_ms_mean"])),
                         receipt_p95_ms=r3(float(m["receipt_p95_ms_mean"])),
                         src="artifact V12 E1_E2_method_means.csv; hold percentiles from E1_E2_hold_diagnostics.csv"))
    rows.sort(key=lambda r: (r["rate"], ORDER[r["policy"]]))
    write("rate_sweep.csv", [
        "One slot, no explicit cap; rate-sweep campaign E1 (108 formal runs, 6 paired runs per condition).",
        "goodput = correct, timely results/s (100 ms deadline); ci = pointwise 95% paired-bootstrap interval.",
        "hold = source hold, commit to last borrow return (ms); p5/p95 = per-run percentiles averaged over runs.",
        "receipt = mean planned-arrival-to-sink latency (ms); receipt_p95 = mean of per-run 95th percentiles.",
        "Generated by scripts/extract_artifact.py from the public artifact; do not edit by hand."],
        ["rate", "policy", "goodput", "goodput_ci_lo", "goodput_ci_hi", "hold_mean_ms", "hold_p5_ms",
         "hold_p95_ms", "receipt_mean_ms", "receipt_p95_ms", "src"], rows)

    # ---- late read (E2) ----
    rows = []
    for m in means:
        if m["experiment"] != "e2" or m["method"] not in POL:
            continue
        late = m["late"] == "True"
        pol = POL[m["method"]]
        rows.append(dict(variant="late" if late else "base", last_read="op 288/289" if late else "op 1/287",
                         policy=pol, goodput=r3(float(m["goodput_hz_mean"])),
                         goodput_ci_lo=r3(float(m["goodput_pointwise_ci95_low"])),
                         goodput_ci_hi=r3(float(m["goodput_pointwise_ci95_high"])),
                         hold_mean_ms=r3(float(m["source_hold_mean_ms_mean"])),
                         src="artifact V12 E1_E2_method_means.csv (E2)"))
    rows.sort(key=lambda r: (r["variant"] != "base", ORDER[r["policy"]]))
    write("late_read.csv", [
        "Late-read campaign E2 at 30 Hz, one slot, no cap (36 formal runs, 6 paired runs per condition).",
        "Generated by scripts/extract_artifact.py from the public artifact; do not edit by hand."],
        ["variant", "last_read", "policy", "goodput", "goodput_ci_lo", "goodput_ci_hi", "hold_mean_ms", "src"], rows)

    # ---- slots window (96 runs) ----
    grouped = src.json("prior_v11/evidence/grouped.json")
    cfg = {"r1-cap0": ("one_slot", 1, "none"), "r2-cap0": ("two_slots", 2, "none"),
           "r2-cap4": ("two_slots_k4", 2, "4"), "r2-cap8": ("two_slots_k8", 2, "8")}
    rows = []
    for c in grouped["primary"]["conditions"]:
        name, slots, cap = cfg[c["condition"]]
        for meth, v in c["methods"].items():
            if meth not in POL:
                continue
            L = v["losses"]
            secs = 12.0 * len(v["goodput_hz"]["runs"])
            rows.append(dict(config=name, slots=slots, cap=cap, policy=POL[meth],
                             timely=r3(v["goodput_hz"]["mean"]), late=r3(L["correct_late"] / secs),
                             not_enqueued=r3((L["arrivals"] - L["publications"]) / secs),
                             timely_ci_lo=r3(v["goodput_hz"]["interval"][0]),
                             timely_ci_hi=r3(v["goodput_hz"]["interval"][1]),
                             protected_mib=r3(v["mean_protected_mib"]["mean"]),
                             device_peak_mib=f"{v['device_peak_mib']['mean']:.0f}",
                             src="artifact prior_v11/evidence/grouped.json"))
    rows.sort(key=lambda r: (list(cfg.values()).index(next(x for x in cfg.values() if x[0] == r["config"])),
                             ORDER[r["policy"]]))
    write("slots_30hz.csv", [
        "Slots x cap x policy at 30 Hz (120 results/s offered); separate 96-run window, 6 runs per condition.",
        "timely/late/not_enqueued in results/s; ci = pointwise 95% paired-bootstrap interval for timely goodput;",
        "protected_mib = time-averaged protected source storage; device_peak_mib = measured device-memory peak.",
        "Generated by scripts/extract_artifact.py from the public artifact; do not edit by hand."],
        ["config", "slots", "cap", "policy", "timely", "late", "not_enqueued", "timely_ci_lo", "timely_ci_hi",
         "protected_mib", "device_peak_mib", "src"], rows)

    # ---- deadline re-scoring of the same 96 runs ----
    dl = src.json("prior_v11/evidence/deadlines_v7.json")
    rows = []
    for s in dl["summary"]:
        name = cfg[s["condition"]][0]
        for meth, vals in s["means"].items():
            if meth not in POL:
                continue
            for d, g in zip(dl["deadlines_ms"], vals):
                rows.append(dict(config=name, policy=POL[meth], deadline_ms=d, goodput=r3(g),
                                 src="artifact prior_v11/evidence/deadlines_v7.json"))
    write("deadlines_30hz.csv", [
        "Timely goodput of the 96-run slots window re-scored at receipt deadlines of 80-200 ms (unchanged executions;",
        "post-hoc cutoff sensitivity, not deadline-aware scheduling).",
        "Generated by scripts/extract_artifact.py from the public artifact; do not edit by hand."],
        ["config", "policy", "deadline_ms", "goodput", "src"], rows)

    # ---- one-slot trace at 20/s, repetition 0 ----
    # Arrivals are those planned inside the window. Slot holds and recipient intervals are drawn for every
    # admitted publication whose interval overlaps the window, including work carried over from publications
    # admitted before it (their private computation can still be running when the window opens).
    pubs = src.csv("gpu_independent_local/E1_E2_publication_timeline.csv")
    recs = src.csv("gpu_independent_local/E1_E2_recipient_timeline.csv")
    rows = []

    def overlaps(a, b):
        return b >= 0.0 and a <= TRACE_SPAN_MS

    for meth, pol in (("manual-full", "Full"), ("auto-batched", "BIM")):
        sel = sorted((p for p in pubs if p["experiment"] == "e1" and p["rate_hz"] == "20" and p["repeat"] == "0"
                      and p["method"] == meth), key=lambda p: float(p["scheduled_relative_ms"]))
        for p in sel:
            t = float(p["scheduled_relative_ms"]) - TRACE_T0_MS
            if 0 <= t <= TRACE_SPAN_MS:
                rows.append(dict(policy=pol, row="arrivals", kind="busy" if p["drop_reason"] else "admitted",
                                 start_ms=f"{t:.1f}", end_ms="", label=""))
        admitted = [p for p in sel if not p["drop_reason"]]
        seq0 = min(int(p["sequence"]) for p in admitted
                   if float(p["scheduled_relative_ms"]) - TRACE_T0_MS >= 0)
        rec_by_seq = {}
        for q in recs:
            if q["experiment"] == "e1" and q["rate_hz"] == "20" and q["repeat"] == "0" and q["method"] == meth:
                rec_by_seq.setdefault(q["sequence"], []).append(q)
        for p in admitted:
            seq = int(p["sequence"])
            a = float(p["commit_relative_ms"]) - TRACE_T0_MS
            b = float(p["last_release_relative_ms"]) - TRACE_T0_MS
            name = "k" if seq == seq0 else f"k{seq - seq0:+d}"
            if overlaps(a, b):
                rows.append(dict(policy=pol, row="slot", kind="held", start_ms=f"{a:.2f}", end_ms=f"{b:.2f}",
                                 label=f"{name}|{float(p['source_hold_ms']):.2f} ms"))
            for q in sorted(rec_by_seq.get(p["sequence"], []), key=lambda q: int(q["consumer"])):
                adm = float(q["admission_relative_ms"]) - TRACE_T0_MS
                rel = float(q["release_end_relative_ms"]) - TRACE_T0_MS
                out = float(q["output_done_relative_ms"]) - TRACE_T0_MS
                rr = f"R{int(q['consumer']) + 1}"
                if overlaps(adm, rel):
                    rows.append(dict(policy=pol, row=rr, kind="holds_source", start_ms=f"{adm:.2f}",
                                     end_ms=f"{rel:.2f}", label=""))
                if out - rel > 0.2 and overlaps(rel, out):
                    rows.append(dict(policy=pol, row=rr, kind="private", start_ms=f"{rel:.2f}",
                                     end_ms=f"{out:.2f}", label=""))
    write("trace_20hz.csv", [
        "One-slot trace at 20 Hz, E1 repetition 0; times in ms since the arrival planned 1,000 ms after",
        "the measured cohort starts (the window shown in Fig. 2). slot/held = commit to last borrow return;",
        "R1-R4 = recipients 0-3: holds_source = admission to source return, private = source return to output.",
        "Generated by scripts/extract_artifact.py from the public artifact (E1_E2_*_timeline.csv); do not edit by hand."],
        ["policy", "row", "kind", "start_ms", "end_ms", "label"], rows)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
