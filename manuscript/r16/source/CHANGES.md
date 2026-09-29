# Revision 16 Change Record

## Scope

Readability revision of r15 based on the next round of reader feedback. No new experiment, statistical reanalysis, or figure redraw is performed. The nine figure-data CSVs and all six PDF/PPTX/PNG figure sets are unchanged.

## Advice Applied

| Concern | Change |
|---|---|
| Title promises an automotive middleware evaluation | Retitled the paper "BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes." Driving remains the motivating application; the established BIM name is retained. |
| Two lifetimes compete with admission as the main claim | Aligned the abstract, introduction, and conclusion around ending storage use before result delivery. Admission is an operational consequence. |
| Why not double buffer? | Stated the one-slot assumption early and introduced the measured two-slot Full alternative in the introduction. Kept the 64 MiB saving in the context of an approximately 5 GiB measured peak, without inventing scaling results. |
| Why not copy? | Explained in Section II that a queued copy is a pending source read. The evaluated copying policy uses recipient registration and releases at copy completion; equivalent coordination is possible in other designs. |
| Too many terms arrive at once | Used frame in running prose; mapped publication to the retained figure/artifact label. Defined recipient as a process and reader as a component in that process. Introduced prefix, suffix, and binding tokens where used. |
| Stream-only sounds like a data-stream policy | Introduced it as CUDA stream-only release and mapped the shorter figure label explicitly. |
| Manual and Manual-checked sound redundant | Explained that one is a separately implemented baseline, while the other holds the runtime and binding checks fixed to isolate boundary placement. |
| Innovation is obscured by concessions | Motivated automatic boundary maintenance directly and brought the distinction from within-program last-use analysis and application-placed release fences into the introduction. |
| Repeated rhetorical formulas | Reduced triad repetition, shortened the library analogy, replaced several verdict run-ins with descriptive headings, and used causal explanations. |
| Evaluation repeats many plotted numbers | Kept decisive comparisons and explanations in prose, with the remaining plotted values available in the unchanged figures and CSVs. Adverse two-slot and copying results remain. |
| Deadline and drop policy are unexplained | Explained the common 100 ms benchmark budget, deadline re-scoring, and fixed offered-load schedule. No vehicle safety deadline is asserted. |
| Model-state cloning appears to be free | Explained plan-owned weight/buffer copies, their purpose, one-time construction, and retained storage; distinguished them from per-frame source copies. |
| Maintenance counts sound like developer edits | Rechecked the saved transition table and corrected the wording as detailed below. |

## Maintenance Evidence Correction

The public rate/slot archive contains E3/E3_maintenance_16_transitions.csv:

- Thirteen transitions change the runtime-boundary field.
- The two alias-chain edits shift displayed indices but leave that field unchanged.
- Batch-normalization folding leaves the first source read in place and refreshes the graph binding. Its separate output validation uses the recorded tolerance.
- The controlled public ResNet-18 to ResNet-50 substitution changes the boundary and graph binding.
- All 16 stale manual reviews fail the saved graph-binding checks. The public-model substitution uses a CPU check; the folding record retains its corrected independent validation and failed-campaign provenance. The evidence does not show these guarded cases silently producing wrong outputs.
- Changed review fields are not measured human edits, patch lines, or developer error rates.
- ReadSeal's zero-annotation count concerns source-reader/boundary annotations. Export, topology, native contracts, operator review, and output dependencies remain separate work.

These are corrections to the interpretation of preserved records, not changes to the records. Table I now identifies the guarded Manual case consistently.

## Preserved Evidence and Figures

The two-reader engine/graph composition remains a controlled workload. BEVFusion's two-head architecture is motivation, not a claim that the benchmark executes those two heads across TensorRT and PyTorch. The complete-frame denominator includes all scheduled frames and intended recipients. The separate 168-run campaign remains recipient-level evidence, with its copying advantage and late latency/freshness costs preserved.

Six reconstructed vector figures, editable PPTX files, and 600 dpi PNGs are carried forward exactly from r15. Four equations and the algorithm's operations are unchanged; terminology and grammar are clarified. The final PDF retains searchable text, vector figures, and lossless stream expansion above 1 MiB.

## Suggestions Requiring New Evidence

No ROS 2/Orin/Jetson/DRIVE measurement, recipient-scaling study, real model-history transition, or new detection/segmentation split was performed. None is described as completed. Bibliography entries are preserved without a fresh reference audit. Earlier releases and experimental archives remain intact.
