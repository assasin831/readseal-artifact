"""Vector sensitivity plots from validated measurements, never synthetic data."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    load = json.loads((ROOT / 'evidence/loadscan_v7.json').read_text())
    cut = json.loads((ROOT / 'evidence/deadlines_v7.json').read_text())
    assert load['status'] == cut['status'] == 'COMPLETE'
    assert len(load['rows']) == 72 and len(cut['rows']) == 96
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['DejaVu Serif'],
        'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8.5,
        'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'legend.fontsize': 7.1,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'axes.spines.top': False,
        'axes.spines.right': False, 'axes.linewidth': .6,
        'mathtext.fontset': 'dejavuserif'})
    fig, axes = plt.subplots(1, 2, figsize=(4.8, 2.46))
    ax = axes[0]
    for method, field, color, marker, short in [
            ('auto-batched', 'a_mean', '#0072B2', '^', 'Grouped'),
            ('manual-full', 'b_mean', '#333333', 's', 'Full')]:
        for cap, style in [(0, '--'), (8, '-')]:
            ys = [next(s for s in load['summary'] if s['condition'] == f'r2-cap{cap}-hz{r}')
                  ['metrics']['goodput_hz'][field] for r in (20, 30, 40)]
            ax.plot([20, 30, 40], ys, color=color, marker=marker,
                markerfacecolor='white' if cap == 0 else color, markersize=5.0 if method == 'auto-batched' else 3.0,
                linewidth=1.1, linestyle=style, label=f'{short}, $K=' + (r'\infty$' if cap == 0 else '8$'))
    ax.set(title='(a) New load scan: R=2', xlabel='Publications/s', ylabel='Timely bundles/s')
    ax.set_xticks([20, 30, 40])
    ax.set_ylim(0, 90)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.legend(loc='upper left', bbox_to_anchor=(-.02, -.37), frameon=False, borderaxespad=0, labelspacing=.2,
              handlelength=1.9, handletextpad=.5)
    ax = axes[1]
    x = np.asarray(cut['deadlines_ms'])
    for condition, color, marker, label in [
            ('r1-cap0', '#A05A17', '^', r'$R=1, K=\infty$'),
            ('r2-cap0', '#0072B2', 'o', r'$R=2, K=\infty$'),
            ('r2-cap8', '#555555', 's', r'$R=2, K=8$')]:
        v = next(s for s in cut['summary'] if s['condition'] == condition)['grouped_minus']['manual-full']
        y, ci = np.asarray(v['mean']), np.asarray(v['ci95'])
        ax.fill_between(x, ci[:, 0], ci[:, 1], color=color, alpha=.13, linewidth=0)
        ax.plot(x, y, color=color, marker=marker, markersize=3.0,
                linewidth=1.05, label=label)
    ax.axhline(0, color='.45', linewidth=.6, zorder=0)
    ax.axvline(100, color='.65', linestyle=':', linewidth=.7, zorder=0)
    ax.set(title='(b) Fixed primary traces', xlabel='Receipt cutoff D (ms)',
           ylabel='Grouped - Full (bundles/s)', ylim=(-62, 28), xlim=(77, 203))
    ax.set_xticks([80, 100, 150, 200])
    ax.set_yticks([-60, -30, 0, 20])
    ax.legend(loc='upper left', bbox_to_anchor=(-.02, -.37), frameon=False, borderaxespad=0,
              labelspacing=.3, handlelength=1.5, handletextpad=.4)
    for ax in axes:
        ax.grid(axis='y', color='.91', linewidth=.45)
        ax.set_axisbelow(True)
    fig.subplots_adjust(left=.095, right=.986, bottom=.41, top=.89, wspace=.42)
    fig.savefig(ROOT / 'figures/sensitivity.pdf', metadata={'CreationDate': None})
    fig.savefig(ROOT / 'figures/sensitivity.png', dpi=230)
    plt.close(fig)
    manifest = dict(status='COMPLETE', inference_executed=False,
        sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [ROOT/'evidence/loadscan_v7.json', ROOT/'evidence/deadlines_v7.json']},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        outputs={name:hashlib.sha256((ROOT/'figures'/name).read_bytes()).hexdigest()
                 for name in ['sensitivity.pdf', 'sensitivity.png']})
    (ROOT/'figures/sensitivity_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
