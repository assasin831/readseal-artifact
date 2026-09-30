# Revision 21 Change Record

This revision starts from the supplied BIM_ReadSeal_ISPA2026_r20 source ZIP and PDF. It is a
writing revision for readers outside GPU systems, prompted by a reviewer-style reading from the
point of view of a general parallel and distributed systems reviewer, and by the authors' request
to rewrite the abstract around the paper's story and contributions. No experiments, statistics,
figures, equations, algorithm, table, or references change. Every edit is an exact-match
replacement in qa/r21/edit_r21.py; the unified diff is qa/main_r20_to_r21.diff and a latexdiff
PDF is qa/r21/BIM_ReadSeal_ISPA2026_r21_changes.pdf.

## Abstract

- Opens with the common setting (ROS 2 stacks whose processes consume the same data, which is
  increasingly one large GPU tensor that ROS 2 has begun to share in GPU memory) instead of
  asserting that perception processes "often share one large GPU tensor".
- States the release problem once, as a trade-off (too early reads the wrong frame; too late drops
  frames while the GPU idles), instead of two sentences on the baselines' failures.
- Tells the story in order: key observation, BIM, ReadSeal, results. The latency cost stays as one
  clause (8-11 ms mean); the 95th-percentile increment and the stream-only ordered-test sentence
  move out of the abstract and remain in Sections V-B and V-E.
- 281 to 271 words.

## Accessibility and flow

| Reader obstacle | r21 change |
|---|---|
| The asynchronous-GPU fact behind the problem appeared only in Section II | One sentence in the introduction's second paragraph |
| Novelty relative to BufferQueue/NvSciStream was implicit | One sentence: a borrow starts at publication and ends at a derived, checked last read |
| Running example switched to engine A + graph B without saying why | Section II says the readers run on different runtimes, each with its own completion signal; Fig. 1b caption says why these two readers decide reuse |
| "request", "output sink", "accept", "tail" used before or without definition | Defined at first use (Sections III, IV-B, I) |
| "buffers" meant PyTorch module state in IV-C | "weights and other state, such as normalization statistics" |
| Operator summaries and binding tokens assumed compiler/PyTorch background | IV-A ties the summaries to the sets in Eq. (2) and names what is rejected in plain terms; IV-C says which substitutions fail the check |
| GPU-capacity line in Figs. 4a/5a was never explained | V-B: four results per 51 ms, about 78 results/s, and why gains start at 20 Hz |
| Two slots doing worse than one was unexplained | V-C: queueing delay, as with bufferbloat |
| V-D switched metrics twice in one paragraph | Complete-frame metric defined where V-D uses it; the 168-run per-result study starts its own paragraph |
| "ordered-overwrite cases exact against unsplit references" | V-E states what each case checks |

## Page budget

The additions were offset by removing repetition, so the paper stays at eight pages with every
float on its r20 page: the Section V roadmap now names three questions instead of repeating the
subsection titles; the Discussion and Conclusion no longer restate V-D's percentages; the
introduction's results paragraph is shorter; and a few words were trimmed where a paragraph ended in
a nearly empty line. The last column ends at 680 pt instead of 706 pt (column bottom 719 pt), about
three lines of margin for MiKTeX/TeX Live line-breaking differences. The r20 source builds to the
same last-column position under both engines. Both acknowledgment settings build to eight pages.

## For the authors to confirm

1. V-E now reads "the source was overwritten once the regenerated boundary had completed, and every
   output still matched the unsplit model's exactly". This is our reading of "ordered-overwrite
   cases exact against unsplit references"; please confirm it matches the experiment.
2. V-E still says "two methods" without naming them; naming them would help readers.
3. The abstract no longer mentions the 95th-percentile latency increment or the ordered tests in
   which stream-only release computed on the wrong frame. If reviewers at this venue expect the
   safety result in the abstract, a short clause can return.

## Verification

qa/verification_r21.json: eight pages; floats on the same pages as r20; equations, algorithm, table,
figure includes, and refs.bib unchanged; the only new number is 78 (the capacity line already drawn at
78.4 in Figs. 4a and 5a); 65 other files byte-identical to r20. The final PDF was produced by
scripts/finalize_pdf.py (now writing r21 names) in a scratch copy, so figure PNGs were not
re-exported; qa/export_validation_r21.json is its report. The AI-use acknowledgment setting is
unchanged at the authors' request.

---

# Revision 20 Change Record

This revision starts from the supplied BIM_ReadSeal_ISPA2026_r19-1.pdf and
BIM_ReadSeal_ISPA2026_r19_source(1).zip, not the other r19 previously published
on GitHub. The PDF inside the supplied ZIP exactly matches the supplied PDF.

Only five locations in main.tex change:

1. Split the abstract's comparison into three sentences and attach the latency
   increments explicitly to the one-buffer full-retention baseline.
2. Mark the first Section V-D study's switch to complete frames and state that
   all four results must be correct and timely.
3. Mark the separate 168-run study's return to recipient-level timely results.
4. Update the artifact link from ispa2026-r17 to the existing ispa2026-r19 tag.
5. Remove the supplementary Rushby four-slot model-checking citation from the
   three-source citation group. The Simpson and NBW original references remain.
   The first build overflowed to nine pages; removing this one citation returns
   the paper to eight pages and reduces the rendered bibliography from 27 to 26.
   The unused BibTeX entry remains in the unchanged reference database.

All other manuscript wording, equations, algorithm, table, and captions remain
unchanged. All nine CSVs and eighteen PDF/PPTX/PNG figure files are byte-identical
to the supplied source. No measurements or statistical quantities change, and no
experiments are run. Only output naming and revision documentation are updated
outside main.tex. The exact source diff is qa/main_r19_1_to_r20.diff.

All eight final pages were rendered with Poppler and visually checked for
clipping, overlap, and figure placement. The existing 10-point body size, margins,
and figure dimensions are unchanged. Verification records are
qa/verification_r20.json and qa/export_validation_r20.json. Historical checks
below are preserved as historical records. No GitHub publication is performed
in this local revision.

---

# Historical Revision 19 Change Record

## Scope

Writing revision of r18 prompted by a third-party writing review (nine points)
and a reviewer-style reading. Goals: check which review claims are real, fix
those that are, define each term once and use it consistently, tell the story
in one line of argument, and gather caveats in one place instead of scattering
them. No experiment, inference, or statistical analysis was run. All nine CSVs
and all figure files (PPTX, PDF, PNG) are byte-identical to r18; equation
bodies and algorithm operations are unchanged. qa/r19/ contains the unified
diff of main.tex and refs.bib and a latexdiff PDF of the changes.

## The Writing Review, Checked Against the Source

| Review claim | Verdict | r19 action |
|---|---|---|
| recipient / reader / consumer / subscriber mixed | Partly real. "Consumer" named BIM's own recipients twice (IV-B "two consumer levels", Discussion "each consumer's hold"); the abstract used "reader" and "recipient" for the same unstarted party without defining either. | Recipient and reader are defined together in the first paragraph; the abstract says recipient only; consumer/subscriber now appear only when describing BufferQueue, NvSciStream, and ROS 2. |
| source / shared tensor / buffer / slot / storage mixed | Partly real: the abstract used "slot" undefined. | Abstract says buffer; the introduction defines slot and source. |
| release / return borrow / clear bit not distinguished | Partly real. | Section III defines release rule, return (clear the bit), and reusable slot; "frees the slot" became "releases" or "makes reusable"; "without freeing" became "without deallocating". |
| Missing comma before "and at 20 Hz" | Not real: the comma was present. | Sentence recast with a semicolon. |
| "three questions have answers" | Style. | "three questions can be answered". |
| BufferQueue "where it should do so" | Real. | "at which point in its computation to return it". |
| "While the first operation is right..." | Real. | Rewritten as two failure modes: stale versus wrong from the start. |
| "This difference in hold time" | Real (weak antecedent). | "so ReadSeal's shorter hold admits more of the arriving frames". |
| 25 Hz dip unexplained | Real. | Explained: the 40 ms period is shorter than BIM's 95th-percentile hold (43.754 ms, rate_sweep.csv), so a refused frame leaves the slot waiting a full period. |
| Algorithm 1 lacks title, I/O, end, indentation | Mostly not real: it has a title and indentation; [noend] is deliberate. Symbols were undefined. | Caption defines b_{s,j}, U_j, T; U renamed U_j to match Eq. (4); line 2 now reads "cap K has no room for k", matching Section III. |
| done_u / cancelled_u types unclear | Partly real. | Defined as predicates that become true. |
| beta undefined when Q_r is empty | Real (formal gap). | beta = 0 when Q_r is empty. |
| Table I double-dagger note has no subject | Real. | "Stream-only release cannot wait for readers that have not submitted GPU work." |
| "TABLEI" missing space | Not real: a text-extraction artifact; the PDF renders "TABLE I". | None. |
| Dagger unexplained | Not real: explained in the caption. | Manual and Manual-checked merged into one "Hand-placed" row whose dagger points to Section V-A. |
| Captions overloaded | Partly real. | Figs. 2-5 captions shortened; "not work-conserving" moved to Section II and device peaks to Section V-C. |
| Fig. 1 glyphs inconsistent with the main text | Not real: figure and caption use the same black circled digits; the main text uses none. | None. |
| Contributions unnumbered and unmappable | Not real: bullets with section pointers. | Unchanged structure. |
| Related Work at the end overlaps Discussion | Minor. | Kept at the end (common in systems papers); Discussion no longer repeats the case for derivation. |
| No evaluation roadmap | Real (r18 had removed it). | One-sentence roadmap opens Section V. |
| Numbers without comparison targets | Partly real. | "BIM delivers 1.95x Full's timely results"; baselines described by the question each answers. |
| "Early reads may be common" from nine tails | Real. | "A small static survey suggests..." |
| BEV, IPC, DAG, MPS, RCU not expanded | Mostly not real: BEV, DAG, MPS, and RCU are expanded at first body use. IPC appeared in the keywords and Fig. 1 before its expansion. | IPC expanded in the first paragraph; TensorRT glossed as NVIDIA's inference runtime. |
| Web citation format inconsistent | Real. Rushby and Buttazzo printed "[Online]. Available:" while every other web reference prints a bare URL; four web references have no year; none has an access date. | Rushby and Buttazzo now use the bare-URL style. Years and access dates not added (see below). |
| zero-copy / cross-process hyphenation | Not real: consistent throughout. | None. |
| K (cap) versus k (frame) | Real but not changed. | Fig. 4 and Fig. 5 print "K" and "k" inside the figure art; renaming needs regenerated figures. The text always says "request cap K". |
| Colloquial "hand the next frame", "sits idle" | Real in the abstract. | Rephrased. |

## Story and Tone

- Abstract: names both release rules and what goes wrong with each; says
  "buffer" throughout; ends with the ordered-test result as a concrete event.
- Introduction: "Two common release rules err in opposite directions"; the
  two-lifetime observation leads into the three questions; a new sentence
  contrasts compiler last-use analysis, which sees one program, with a producer
  that sees neither the recipients' programs nor their unsubmitted reads; BIM is
  mapped to question (2) across processes and ReadSeal to the rest inside each
  recipient; the results paragraph adds the pool-sizing finding (second slot,
  no cap: BIM timely results 78.5 -> 24.9 per second).
- Evaluation: baselines are introduced by purpose, without campaign
  chronology; result subsections lead with topic sentences instead of bold
  run-in heads; "worsens freshness" (an undefined metric) and "(540 output
  tensors)" were removed.
- Discussion: "Why derive the boundary?" and "Deployment" were folded into the
  introduction and one Limitations paragraph, which now holds the caveats that
  were scattered through r18 (one A100 without MPS and replayed features; 64 MiB
  against a 5 GiB peak and unmeasured shared-DRAM platforms; ordered tests show
  possibility, not frequency; declared topologies; slow or crashed recipients).
  The "benchmark threshold, not a vehicle requirement" aside was removed; V-A
  states that Fig. 5c re-scores the runs at 80-200 ms.
- Conclusion: states lessons (where a borrow should end; copies for late
  reads; derived boundaries rebuilt automatically) and generality, then future
  work.

## Numbers

An automated comparison of every numeral in the r18 and r19 bodies finds one
new value and one removed value; all others are carried over.

- New, from a CSV: BIM's 95th-percentile hold at 25 Hz, 43.754 ms ->
  "44 ms" (rate_sweep.csv, hold_p95_ms).
- New, derived arithmetic (not a measurement): four private copies at 30 Hz
  read and write 63.3 MiB x 2 x 4 x 30 = 15,192 MiB/s = 14.8 GiB/s ->
  "about 15 GiB/s".
- Newly placed in the introduction: 78.5 -> 24.9 timely results/s
  (slots_30hz.csv: one_slot BIM 78.500, two_slots BIM 24.931).
- Removed: "540 output tensors".

## Unchanged by Design

- Figures, CSVs, equation bodies, algorithm operations; the artifact link
  stays on the ispa2026-r17 tag because no data changed.
- K/k notation (figure art), Related Work position.
- Reference years and access dates: not added, because they require the
  authors to open each link. IEEE style gives web sources an "Accessed:"
  date; add one to every web entry after checking the links.
- The optional acknowledgment remains off (\aidisclosurefalse). Both settings
  build to eight pages with no overfull boxes or undefined references (page 8
  columns end at 718/706 pt off and 719/703 pt on).

## To Confirm Before Submission

- Admission under the cap: Section III and Algorithm 1 line 2 now say a frame
  is admitted only if "the cap has room for it". r18's algorithm said "K
  requests are outstanding". Confirm the implementation admits a frame only
  when all four of its requests fit under K; the K = 4 result (53-54 results/s,
  below one-slot Full's 60) is consistent with that reading.
- The derived 15 GiB/s figure in the introduction.

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
