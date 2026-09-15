"""Regenerate LNCS-width vector figures from frozen, validated aggregates.

V7: enlarges method labels and focuses on delivery; protected-storage
estimates remain in the text and frozen data. It shows, on a shared condition
axis, (i) where every offered bundle goes and (ii) the paired effect of checked
early reuse. Reads only evidence/*.json; runs no inference.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "evidence"
OUT = ROOT / "figures"

C_FULL = "#1d3f57"
C_MAN = "#555555"
C_TIMELY = "#21695c"
C_LATE = "#7fb2a6"
C_UNADM = "#c9c9c9"

LABEL = {
    "r1-cap0": "$R{=}1$\n$K{=}\\infty$",
    "r1-cap8": "$R{=}1$\n$K{=}8$",
    "r2-cap0": "$R{=}2$\n$K{=}\\infty$",
    "r2-cap4": "$R{=}2$\n$K{=}4$",
    "r2-cap8": "$R{=}2$\n$K{=}8$",
}
METHODS = [("auto-early", "O"), ("auto-batched", "G"),
           ("manual-early", "M"), ("manual-full", "F")]
SERIES = [("auto-batched_minus_manual-full", "vs. Full retention", C_FULL, "D"),
          ("auto-batched_minus_manual-early", "vs. Manual early", C_MAN, "^")]
ROWS = [("goodput_hz", "$\\Delta$ goodput\n(bundles/s)", (-60, 30))]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_verified(name):
    path = DATA / f"{name}.json"
    proof = json.loads((DATA / f"{name}_validation.json").read_text())
    assert proof["status"] == "COMPLETE", name
    assert proof["analysis_sha256"] == sha(path), name
    data = json.loads(path.read_text())
    assert data["status"] == "COMPLETE", name
    return data


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 8,
        "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 7.2,
        "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False,
        "axes.spines.right": False, "axes.linewidth": .6,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
        "mathtext.fontset": "dejavuserif",
    })


def draw_accounting(ax, conds, show_methods):
    width = .78 / len(show_methods)
    for ci, c in enumerate(conds):
        for mi, (method, short) in enumerate(show_methods):
            L = c["methods"][method]["losses"]
            n = L["arrivals"]
            assert L['producer_late'] == 0
            assert n == sum(L[k] for k in ('timely','correct_late','pool_exhausted','credit_exhausted','queue_loss'))
            xpos = ci + (mi - (len(show_methods) - 1) / 2) * width
            segments = [
                (L["timely"] / n * 120, C_TIMELY, None),
                (L["correct_late"] / n * 120, C_LATE, "///"),
                ((L["pool_exhausted"] + L["credit_exhausted"]
                  + L["queue_loss"]) / n * 120, C_UNADM, None),
            ]
            base = 0.
            for value, color, hatch in segments:
                ax.bar(xpos, value, width=width * .88, bottom=base, color=color,
                       edgecolor="white", linewidth=.3, hatch=hatch, zorder=2)
                base += value
            ax.text(xpos, -4, short, ha="center", va="top", fontsize=7.5,
                    color=".15")
    ax.set_ylim(0, 124)
    ax.set_yticks([0, 60, 120])
    ax.axhline(120, color=".55", linestyle=":", linewidth=.7, zorder=1)


def draw_effect(ax, conds, metric, rng):
    ax.axhline(0, color=".35", linewidth=.7, zorder=1)
    for si, (key, label, color, marker) in enumerate(SERIES):
        off = (si - .5) * .30
        for xi, c in enumerate(conds):
            rec = c["paired_differences"].get(key)
            if rec is None:
                continue
            v = rec[metric]
            runs = np.asarray(v["runs"], dtype=float)
            jit = (rng.random(runs.size) - .5) * .13
            ax.plot(np.full(runs.size, xi + off) + jit, runs, ".", color=color,
                    alpha=.75, markersize=2.8, markeredgewidth=0, zorder=2)
            lo, hi = v["interval"]
            ax.plot([xi + off] * 2, [lo, hi], "-", color=color, linewidth=1.1,
                    solid_capstyle="butt", zorder=3)
            ax.plot([xi + off], [v["mean"]], marker, color=color, markersize=3.4,
                    markeredgecolor="white", markeredgewidth=.5, zorder=4,
                    label=label if xi == 0 else None)


def main():
    setup()
    grouped = read_verified("grouped")
    confirmatory = read_verified("confirmatory")
    assert len(grouped["rows"]) == 96
    rng = np.random.default_rng(20260914)

    panels = [(grouped, "(a) Primary window, 96 runs", METHODS),
              (confirmatory, "(b) Independent, 54 runs", METHODS[1:])]
    ncond = [len(p[0]["primary"]["conditions"]) for p in panels]

    fig, axes = plt.subplots(
        2, 2, figsize=(4.8, 2.80), sharey="row",
        gridspec_kw={"width_ratios": ncond, "height_ratios": [1.12, 1],
                     "wspace": .06, "hspace": .28})

    for col, (data, title, show_methods) in enumerate(panels):
        conds = data["primary"]["conditions"]
        draw_accounting(axes[0][col], conds, show_methods)
        for row, (metric, _, ylim) in enumerate(ROWS, start=1):
            draw_effect(axes[row][col], conds, metric, rng)
            axes[row][col].set_ylim(*ylim)
        for row in range(2):
            ax = axes[row][col]
            ax.set_xticks(np.arange(len(conds)),
                          [LABEL[c["condition"]] for c in conds]
                          if row == 1 else [""] * len(conds))
            ax.set_xlim(-.60, len(conds) - .40)
            ax.tick_params(axis="x", length=0, pad=8 if row == 0 else 2)
            ax.yaxis.grid(True, color=".90", linewidth=.5)
            ax.set_axisbelow(True)
            if col > 0:
                ax.tick_params(axis="y", length=0)
                ax.spines["left"].set_visible(False)
        axes[0][col].set_title(title, loc="left", pad=3)

    axes[0][0].set_ylabel("Offered bundles/s\nby outcome", linespacing=1.2)
    for row, (_, ylabel, _) in enumerate(ROWS, start=1):
        axes[row][0].set_ylabel(ylabel, linespacing=1.2)

    bar_legend = [Patch(facecolor=C_TIMELY, label="Correct, timely"),
                  Patch(facecolor=C_LATE, hatch="///", label="Correct, late"),
                  Patch(facecolor=C_UNADM, label="Not enqueued")]
    marker_handles, marker_names = axes[1][0].get_legend_handles_labels()
    fig.legend(handles=bar_legend, loc="upper left", bbox_to_anchor=(.145, 1.010),
               ncol=3, frameon=False, columnspacing=.9, handlelength=1.1,
               handletextpad=.35)
    fig.legend(marker_handles, marker_names, loc="upper left",
               bbox_to_anchor=(.145, .938), ncol=2, frameon=False,
               columnspacing=1.4, handletextpad=.3)
    fig.subplots_adjust(left=.160, right=.985, bottom=.140, top=.790)
    fig.savefig(OUT / "delivery.pdf", metadata={"CreationDate": None})
    fig.savefig(OUT / "delivery.png", dpi=220)
    plt.close(fig)

    # Keep figures/manifest.json consistent with what this script rewrote.
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest["status"] = "COMPLETE"
    manifest["generator_sha256"] = sha(Path(__file__))
    manifest["inputs"] = {p.name: sha(p) for p in sorted(DATA.glob("*.json"))}
    manifest["outputs"] = {p.name: sha(p) for p in sorted(OUT.iterdir())
                           if p.suffix in {".pdf", ".png", ".csv"}}
    manifest["scope"] = ("No inference run. delivery.pdf combines the validated "
                         "96-run primary and 54-run independent-window records: "
                         "outcome accounting from per-condition loss counts, and "
                         "paired Grouped-minus-baseline effects with their "
                         "precomputed bootstrap intervals.")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "COMPLETE", "figures": ["delivery"]}))


if __name__ == "__main__":
    main()
