# Revision 19 Change Record

## Scope

Local clarity corrections to the supplied r18, preserving the paper's argument,
innovation, numerical results, and adverse findings. No inference, experiment,
or statistical reanalysis is performed. The six figure sets and nine plotting
CSVs are byte-preserved. The final paper remains eight pages at the existing
10-point IEEE conference body size, with no margin reduction.

| Verified concern | Revision |
|---|---|
| Recipient versus reader | Abstract, contribution 2, IV-B, mixed-recipient explanation, and release-fence comparison distinguish receiving processes from their reader components. |
| Abstract jargon | Replace undefined slot and request cap with shared buffer and limit on outstanding requests; explicitly name the latency comparator. |
| Ambiguous pronoun and boundary example | State that the application chooses when each consumer returns its buffer. Explain that the first-operation boundary is correct for TransFusion but already wrong for the ResNet tail. |
| Provenance terminology | Define provenance lifetime directly as preservation of frame identity until delivery. |
| Reuse versus deallocation | Figure 1 caption says the slot can hold the next frame, not that BIM frees it. The diagram itself is unchanged. |
| Missing symbols | Define b_(s,j), use U_j consistently, and state the algorithm's request-cap test in words. Keep conventional, locally defined distinctions K/k, N/n, S(v)/s, and T/t rather than rename all notation. |
| Empty read set | Define beta as max({0} union operation indices), explicitly giving an empty prefix for an empty read set; avoid an undefined operation zero in the proof. This is a formal convention, not a new measured runtime case. |
| Input versus operation index | Use h for input positions in Eq. (2), retaining i for operation positions in Eq. (3). |
| Evaluation roadmap | Restore the five questions in one short paragraph. |
| 1.95x and 25 Hz dip | Name BIM/Full explicitly. Verify six 75.0 results/s runs from the original E1 run table and describe the 40 ms next-opportunity delay after refusal. No new phase-lock diagnosis is claimed. |
| Abbreviation | Expand non-blocking write (NBW) at first use. |
| Web references | Use url fields and a consistent access date; retain existing publication years where available and do not invent missing years. Abbreviate RTSS consistently. |
| Broken or moving reference links | Pin the NITROS composable-graph documentation to release 3.2, use the current Lyrical buffer-backend documentation path, and pin PyTorch multiprocessing documentation to 2.1. The NITROS wording describes its composable path, not every available bridge. |
| Page budget | Shorten repeated performance recaps in the introduction, discussion, and conclusion instead of shrinking text or deleting necessary definitions. Full adverse comparisons remain in Section V. |

## Advice Not Applied

Already-correct commas, algorithm numbering/indentation, done/cancelled
definitions, Table I markers, circled step numbers, contribution bullets, and
hyphenation were retained. Related Work remains at the end. Captions retain
the definitions necessary to read their plots. No new experiments, broad
defensive paragraphs, or altered experimental conditions were introduced.

## Checks

See qa/revision_validation_r19.json for input hashes, preserved CSV/figure
hashes, the six original 25 Hz run values, approximate source-word-count
changes, page bounds, and build diagnostics. See qa/export_validation_r19.json
for pixel/text equivalence between the compiled and delivered PDFs. Reference
access details and the visual review are recorded in qa/REVIEW_R19.md.
Historical checks below are not presented as new r19 experimental results.

---

# Historical Revision 18 Change Record

## Scope

Writing revision of r17 requested by the authors: fewer AI-sounding
constructions, smoother prose, a fuller Conclusion, less defensive framing, and
a story that leads with the contributions. Measurements, equations, algorithm
operations, figures, and all nine CSVs are unchanged. No experiment, inference,
or statistical analysis was run. qa/r18/edit_r18.py applies every text change
to the r17 main.tex as exact-match replacements, so the edits can be audited
and reproduced.

| Goal | r18 edit |
|---|---|
| Lead with the idea | Abstract opens with the reuse question, states the two lifetimes as the key insight, and ends with the ordered-test finding instead of a checklist. |
| Say what is new | Introduction credits per-consumer release to BufferQueue/NvSciStream in one clause, then states the split: the producer knows processes (BIM registers them at publication), each process knows its components (ReadSeal enrolls them, derives boundaries, binds plans). |
| Make the case for automation | A hand-placed boundary can go stale (one late read moves the head's boundary to the second-to-last operation) or be wrong from the start (ResNet-18's residual reads the source at operation 12); a version check catches only the first. Repeated in a new Discussion paragraph, "Why derive the boundary?". |
| One story for all policies | The copying paragraph became "three choices of where a borrow ends" (outputs, private copy, last read); Section II opens with the same framing, so contribution 1 now points to Sections I-II. |
| Results up front | The stand-alone two-slot sentence became an introduction results paragraph, including the late-read limitation. |
| Remove defensive or bookkeeping text | Removed or folded: the drop-versus-block justification in Section III (now one sentence in V-A), the Fig. 4 campaign note, "per-plan allocations are separate...", "Section V-E distinguishes...", "Table I summarizes...", "Manual-checked supplies...", the evaluation roadmap, "with untrained weights", the Table I refresh note (kept in V-E). |
| Reduce AI-style patterns | Colon reveals split into sentences; "left to the application" now appears once (was three times); the library-book analogy moved into the key insight; count-first sentences in V-E now lead with the finding; the V-B and V-C paragraphs lead with the comparison. |
| Clarify baselines | Policies paragraph says Manual comes from the earlier rate/slot campaigns and Manual-checked from the later jitter/mixed campaign. |
| Expand Discussion and Conclusion | Discussion adds "Why derive the boundary?" and a release-policy guide (early vs. late reads, memory, pool sizing and the request cap). Conclusion grows from about 95 to about 190 words: problem, mechanism, headline results, late-read limit, survey evidence that early reads are common, and future work. |
| Fill eight pages | Both columns of page 8 now reach the bottom margin (718/715 of 719 pt); \IEEEtriggeratref is no longer needed. |

## Numbers Rechecked Against the CSVs

- 1.95x at 20 Hz and 1.31-1.50x at 25-40 Hz: rate_sweep.csv.
- Mean and per-run p95 latency increase: +9.09/+7.91/+10.85/+11.44 ms and
  +15.27/+14.84/+19.40/+17.86 ms at 20/25/30/40 Hz, so 8-11 ms and 15-19 ms
  hold for both 20-40 Hz and 25-40 Hz (rate_sweep.csv).
- Mixed recipients, BIM minus Full: 0.26 (periodic) and 0.93 (jitter)
  percentage points, so "less than one point" holds (mixed_30hz.csv).
- New in the text: with early readers, BIM minus cloning is +0.44, +0.68, and
  +0.94 results/s at 20, 30, and 40 Hz (paired t intervals exclude zero), and
  cloning leads by 2.75 at 25 Hz (clone_rates.csv). r17 reported only 25 Hz.
- Two slots, K=4: 53.2-54.2 results/s; two slots without a cap: BIM 24.9
  timely plus 54.1 late (slots_30hz.csv).
- One slot without a cap: BIM has 0.000 late results/s (slots_30hz.csv), the
  basis of the pool-sizing sentence in Section VI.

## Citations

Added \cite{resnet} for the ResNet-18 tail and \cite{legion,starpu} for the
task-runtime contrast in Related Work. All three entries were already in
refs.bib; the paper now cites 27 references (r17: 24). No bibliography entry
was edited, and the inherited bibliography is not represented as newly audited.

## Unchanged by Design

- The artifact link stays on the ispa2026-r17 tag because no data changed.
- The optional acknowledgment remains off (\aidisclosurefalse). Its text now
  names both tools and the kinds of use, without internal revision numbers.
  Turning it on also drops the Legion/StarPU sentence (wrapped in
  \ifaidisclosure\else ... \fi), so the paper stays at eight full pages in
  both settings (page 8 columns end at 718/715 pt off and 719/712 pt on).
- scripts/verify_revision.py and the qa/ records other than
  export_validation.json describe r17 and earlier revisions.
- Build check: eight pages, no overfull boxes or undefined references, all
  fonts embedded; the three underfull warnings are in bibliography URLs.

---

# Historical Revision 17 Change Record

## Scope

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
