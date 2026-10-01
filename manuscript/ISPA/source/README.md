# REALBIM LaTeX Source

Source for *REALBIM: A Framework for Safe Early Reuse of Shared GPU Buffers Across Processes*.

## Build

Compile `main.tex` with pdfLaTeX and BibTeX:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Alternatively, run `sh build.sh` or `./build.ps1`. On Overleaf, upload the source ZIP and select `main.tex` and pdfLaTeX. The precompiled figure PDFs are included; rebuilding figures is not required to compile the paper.

## Files

- `main.tex`: manuscript.
- `refs.bib`, `main.bbl`: bibliography source and compiled entries.
- `IEEEtran.cls`, `IEEEtran.bst`: document class and bibliography style.
- `figures/`: the eight figures listed below.
- `figures/src/`: diagram sources, assets and license notices.
- `MANIFEST.json`: SHA-256 and size of each bundled file, excluding the manifest itself.
- `verify_pdf.py`: optional comparison of a rebuild with the published PDF; requires PyMuPDF.

| Figure | File | Content |
|---|---|---|
| 1 | `fig0_scene.pdf` | Shared BEV map and recipients |
| 2 | `fig_lifetimes.pdf` | Storage and frame-identity lifetimes |
| 3 | `fig1_framework.pdf` | BIM and ReadSeal architecture |
| 4 | `fig2_trace.pdf` | One-slot execution trace |
| 5 | `fig3_boundaries.pdf` | Model edits and last-read boundaries |
| 6 | `fig5_delivery.pdf` | Rate, latency and hold time |
| 7 | `fig6_slots.pdf` | Slots, admission caps and deadlines |
| 8 | `fig7_mixed.pdf` | Jitter and mixed recipients |

## Diagram Sources and Licenses

Figures 1-3 have TikZ sources in `figures/src/`: `fig0_scene.tex`, `fig_lifetimes.tex` and `fig1_framework.tex`. They compile with XeLaTeX and the Carlito font. The icon paths are included in `scene_icons.tex` and `fig1_icons.tex`.

Figure 1 uses a nuScenes-mini LiDAR sweep to render a top-down scene and an illustrative feature texture. See `figures/src/NUSCENES-NOTICE.txt` for the source and CC BY-NC-SA 4.0 terms. `render_bev.py` requires the indicated input sweep.

The outline icons come from Lucide 1.49.0 (ISC) and Tabler Icons 3.48.0 (MIT). License texts and icon lists are in `figures/src/ICONS-LICENSE.txt`. `svg2tikz.py` converts the original SVG paths to TikZ; the generated paths are already included.

Experimental data and their mapping to the figures are available in the [ISPA repository](https://github.com/assasin831/readseal-artifact/tree/ISPA).
