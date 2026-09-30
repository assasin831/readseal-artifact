# R19 Editorial and Visual Review

## Scope and Decisions

The supplied r18 manuscript and reader's advice were compared before editing.
The advice-to-edit record is in CHANGES.md. Changes preserve the paper's story
and contributions while clarifying the two registration levels, frame identity,
reuse versus deallocation, algorithm symbols, the ResNet boundary example,
evaluation questions, and the measured 25 Hz dip. Repeated result recaps were
shortened to retain eight pages at the original font size and margins.

No GPU job, experimental campaign, or statistical reanalysis was run. The
original six 25 Hz BIM observations were read from the public saved rate archive.
The empty-read-set definition is a formal convention, not a newly tested case.
All nine plotting CSVs and all eighteen PDF/PPTX/PNG figure files match r18.
Figure 1's caption changes its reuse wording; its artwork does not change.

## Visual Review

All eight final pages were rendered and inspected in reading order. Figures,
captions, table, four equations, algorithm, and references are legible at their
intended two-column placements. No clipped or overlapping text was observed.
The normal IEEE conference body size and margins are retained. Six underfull-box
warnings remain in body/reference lines and page balancing; no overfull box or
unresolved reference remains. Page-bound checks supplement, rather than replace,
inspection.

The finalizer checks extracted-text and 144 dpi rendered-pixel identity between
the compiled paper and its lossless expanded-stream delivery. The larger file
does not claim additional image information or sharper content than the vector
source. Companion figure PNGs remain 600 dpi.

## Reference Access

Reference checks were performed on September 29, 2026 (local date). Fourteen
cited web resources now use BibTeX URL fields and consistent access dates.
Existing publication years were retained where present; absent years were not
invented. This is an access/format check of these resources, not a complete
author/title/DOI audit of all references.

- The old NITROS path returned 404. The official release-3.2 composable-graph
  page returned content, including its same-process description. The prose now
  specifies that path rather than generalizing to every NITROS bridge.
- The ROS 2 buffer-backend page uses the current Lyrical interface path. Direct
  access returned an anti-bot page; the actual documentation was checked through
  the official ros2/ros2_documentation Lyrical source. A successful HTTP status
  from the challenge page was not treated as content validation.
- The PyTorch multiprocessing link is pinned to 2.1, matching the recorded
  environment. The pinned official page was retrieved successfully.
- Autoware's direct response also presented a challenge; its actual home-page
  content was retrieved with the browsing tool.
- The other checked links resolved to the official documentation, source, or
  author-hosted PDFs. Raw retrieval records, including initial unsuccessful
  paths, are retained in web_reference_access*.json.

## Reproduction

After building, run scripts/verify_r19.py with --prior-zip pointing to the
author-provided r18 source ZIP and --rate-evidence pointing to the public
archives/ispa2026-rate-slots-evidence.zip. It checks preserved bytes, the saved
six-run observation, equation-change scope, references, page bounds, fonts,
and build diagnostics. Its source-word comparison is an approximate token
count, not a publication word count. Older QA records are explicitly historical.

A clean source-ZIP rebuild also matches all eight delivered pages in extracted
text and 144 dpi rendered pixels. See clean_build_verification_r19.json. PDF
metadata and document IDs differ between builds, so their file hashes can differ
without a visible or textual difference.
