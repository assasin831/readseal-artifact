# Revision 17 Change Record

## Current Revision

Readability and figure-label revision of r16 using the supplied non-specialist
review. Measurements, equations, algorithm operations, and all nine CSVs are
unchanged. No new inference or statistical reanalysis was run.

| Advice | r17 edit |
|---|---|
| Clarify what is new | Introduction and contributions attribute per-consumer release to existing systems and foreground pending-reader registration, automatic last-read placement, and execution bindings. |
| Put copying and full retention in the same story | Introduction treats last read, copy completion, and output completion as alternate borrow endpoints under the same registration requirement. |
| Avoid defensive double-buffer framing | Replaced the objection-oriented paragraph with the measured one-slot versus capped two-slot result after the contributions. Section V-C retains the modest 64 MiB difference relative to roughly 5 GiB. |
| Untangle terminology | Defined reader with the first multi-head example; producer schedules arrivals and axes say Frame rate. Figures say frame, not publication. Engine A and graph B replace the missing-letter A/C pair. |
| Distinguish manual policies | Added Manual-checked to Table I and explained the independent versus shared checked runtimes. |
| Alias-chain indices look inconsistent | Fig. 3 caption explains inserted storage-sharing views versus the unchanged runtime release point. The variant code inserts two aten.alias operations before existing users. |
| Similar conditions have slightly different numbers | Fig. 4 caption explicitly distinguishes its runs from the slot campaign of Fig. 5. |
| Jitter's mixed-recipient increase is unexplained | Reported the two measured changes and gave an arrival-gap interpretation as consistency, not a proven phase-lock diagnosis. |
| The 168-run comparison is not shown | Added actual base-25 and late-30 recipient goodputs, paired pointwise intervals, and late-tail/peak costs from unchanged clone_rates.csv. |
| Maintenance prose is opaque | Rewrote as 13/16 changed runtime boundaries, 16 rejected stale manual plans, manual refresh versus automatic construction, with the CPU substitution scope stated. |
| Too many repeated caveats | Removed the publication bridge, repeated automation-scope notes, redundant benchmark-deadline disclaimer, and formulaic paragraph conclusions; compressed model-state copies without implying that they are free. |
| Real-time buffer work is missing | Added a short four-slot/NBW/CAB paragraph and four references, including the primary SRI analysis. See qa/REFERENCE_CHECK_R17.md. |

The suggested 30 Hz stream-only wrong-frame rate requires new experimental
evidence and was not added. No memory-component breakdown, SoC scaling
measurement, funding number, or embedded result was invented. The existing six
ordered stream-only tests remain the stated evidence for that failure.

## Figure Revision

Four native editable PPTX files have text-node substitutions only. Their
non-text ZIP members and all non-text slide attributes are preserved. Matching
vector PDFs change only the corresponding text lines; the 300 dpi pixel
comparison finds no change outside those label regions. Calibri subsets remain
embedded, and 600 dpi companions are regenerated from the vector PDFs.
Figures 3 and 5 are byte-identical to r16 in all three formats.

Current proof: qa/label_revision_validation.json. The earlier raw collision
reports and r14-to-r15 reconstruction proof remain explicitly historical.
The current reviewer handoff uses the new immutable ispa2026-r17 tag; r15,
r16, and experimental evidence remain unchanged.

---

# Historical Revision 16 Change Record

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
