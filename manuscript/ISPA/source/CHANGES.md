# r33: outside reviewer, sixth round; expanded conclusion; fewer references

Built from the r32 source. No experiment was rerun and no measured number changed: every number in the r33
body also appears in r32 and vice versa (one repeated mention of 78.6 was dropped). Eight pages, page 8 full
(about two lines spare). References 30 -> 25. Algorithm 1 is still printed. Marked-up changes:
qa/r33_vs_r32_latexdiff.pdf.

The goals were less AI-sounding and less defensive prose, contributions stated plainly, and a paper an outsider
can follow. The review's points, in the order it raised them:

## "Early" and "late"
- "Late" now means a missed deadline only ("correct but late"). Where a read falls in a graph is said with
  "boundary", "last read comes early", or "at the graph's end". Reordered readers are "the second reader".
- The abstract no longer uses "reads late" or "the late reader". Fig. 8's caption says "one with its last read
  at the graph's end".
- Figure labels are unchanged (Fig. 5 "Add late read", "Remove late read", "Read alias late"; Fig. 6d "late
  read"). The text cites them as edit names. See "Please confirm" 5.

## Abstract
- The "REAd-Last BIM" expansion is gone from the abstract and kept in Section I. Names now arrive with what they
  do: "Its cross-process layer, Borrow-in-Memory (BIM), ... Its in-process layer, ReadSeal, ...".
- "Refuses a stale plan" becomes "refuses to run if the code, model, or input layout has changed".
- The "Too early, and ...; too late, and ..." antithesis is replaced by one plain sentence.
- The scope condition goes with the headline number ("with recipients whose models stop reading the map
  early"), and the latency cost stays as one clause. The copy comparison is now a positive result ("matches
  per-recipient copies without their 256 MiB"), and the "a copy delivers more" case moved to Section VI.
- The safety sentence says "the second reader", per the review's wording.

## Introduction
- The meta-definition "we say slot when we mean ... and source when we mean ..." is gone. The source is now
  defined in one clause: "the tensor in a slot, which we call the source".
- The "just add a second buffer" objection is answered in paragraph 3: "A second slot recovers most of these
  frames but costs another 64 MiB per shared tensor; we show that one slot, released at the right moment,
  delivers as many results as two (Section V-C)."
- The key observation gets evidence beyond one head: "each of the nine torchvision model tails that our
  analysis accepts stops reading its input within its first 12 operations (Section V-F)". The wording says
  "accepts" deliberately, because five models were rejected.
- Results paragraph: early last reads, 1.31-1.50x at 8-11 ms, matches copies, never the wrong frame, and
  re-planning after 16 model changes in 0.08-0.21 s. It ends on "Section VI discusses when a private copy is
  the better choice", so the contributions no longer follow the case where copying wins.
- Contributions: (1) the two-lifetime split is now a bullet; (2) BIM leads with what is new (protection for
  recipients that have not submitted any GPU work, "as no event-based policy can"), and the relation to
  ipc_shared_ptr stays in Related Work; (3) ReadSeal. The old third bullet, which read like an evaluation
  result, is gone; its numbers are in the results paragraph.

## Background, Sections III-IV
- Section II opens with one signposting sentence.
- The running example now states its point: "So when A's event completes, B has submitted nothing and there is
  no event to wait on: stream-only release makes the slot reusable while B still needs it."
- The descriptor paragraph is folded into "Life of a frame". Algorithm 1's BuildPlan is two lines instead of
  three.

## Evaluation
- Section V opens by saying outright that the hand-placed baselines match REALBIM's delivery by design: the
  throughput gain comes from where the borrow ends, and derivation pays off in safety (Section V-E, including
  the ResNet-18 residual read).
- Fig. 6's caption says the same: "Hand-placed releases at the same point as REALBIM by design".
- The baselines have distinct names in the text, Table II, and the plots. "Hand-placed" is the standalone
  runtime (Figs. 6-7). "REALBIM (hand-placed)" is REALBIM with a hand-placed boundary (Fig. 8 legend relabeled
  by figures/src/relabel_r33.py; the entry moved 17 pt left, no pixel below the legend changed). Table II:
  H and Rh replace Hs and Hr.
- Defensive asides removed: "(78.6 in Fig. 6d, from separate runs)" and "a two-slot rate sweep that we do not
  plot".
- V-C's held-storage result now ends on itself ("memory that an allocator could lend to other work"). The
  fixed-pool caveat and the device peaks (5,078 / 5,142 MiB) moved to Limitations, so the caveat is stated
  once, where it belongs.
- "As with bufferbloat ..., this adds delay but not throughput" is now a plain sentence that leads into the
  numbers.

## Discussion
- "Borrow or copy" leads with the decision rule, not with "where memory is plentiful, copies are simpler".
- New "Beyond the A100" paragraph argues why the result should transfer. The delivery gain depends on how the
  hold compares with the frame period (Eq. 1), not on memory capacity. What an SoC changes is the price of the
  alternatives, so "we expect borrowing to save more on an SoC". This is reasoning, not a measurement; see
  "Please confirm" 1.

## Conclusion (131 -> 224 words)
- Three paragraphs:
  1. The problem and the insight: two lifetimes; one mechanism ending a borrow at different points.
  2. What REALBIM adds and the headline results: 1.31-1.50x, one slot matches two under full retention, no
     wrong frame, re-planning within 0.21 s.
  3. What the derived boundary enables (the borrow-or-copy choice; the message property ROS 2 timing analyses
     assume), then future work.

## References (30 -> 25)
- Dropped, no longer cited:
  - UniAD (CVPR'23): BEVFusion already makes the several-readers point.
  - Teper et al. (RTSS'22) and Li et al. (RTSS'22): the ROS 2 survey [3] covers chain latency, data age, and
    time disparity.
  - Pearce (TOPLAS'21): Descend already covers borrow checking, over GPU memory.
  - Bakita and Anderson (RTAS'23): "partition" dropped from the GPU-sharing sentence; REEF and Orion remain.
- Shorter entries: the Orin data sheet is cited by document number (DS-10662-001) without its URL; the ROS 2
  CUDA buffer backend title is shortened, which fixes its badly spaced three-line entry.

## Style pass
- Fewer stacked clauses: sentences over 35 words 18 -> 17, mean sentence 21.2 -> 20.9 words (same counter for
  both revisions; see qa/r33_build_check.json).
- Analogies kept: library book, bufferbloat, RCU.

## Please confirm
1. The "Beyond the A100" paragraph (Section VI) argues why the result should transfer to an SoC and says "we
   expect". It adds no measurement. Keep it, or cut it to the Limitations sentence?
2. Contribution 2 and the Conclusion claim that no event-based policy can protect a recipient that has not
   submitted GPU work. This rests on Section II: a CUDA event marks only enqueued work.
3. Section I generalizes the early last read from the survey in V-F: nine accepted torchvision tails, all with
   boundaries in their first 12 operations.
4. Fig. 8 legend: "REALBIM (hand-placed)". Figs. 6-7 keep "Hand-placed" for the standalone runtime.
5. Figure labels still use "late read" for graph position (Figs. 5 and 6d). Relabeling them to, e.g., "Add end
   read" needs the same PDF legend edit as Fig. 8. Say if you want it.
6. The five dropped references.

# r32: outside reviewer, fifth round

Built from the r31 source. No experiment was rerun and no measured number changed (every number in the
source compared with r31). Eight pages, page 8 full; references unchanged (30). Algorithm 1 is printed
again: the shorter introduction made room for it.

## Introduction, reordered
- Order: cost of copying, the two failing policies, the two lifetimes, the three questions (each with its
  example: the ResNet-18 residual read for question 1, the added late read for question 3), REALBIM's
  two layers, the results, the contributions.
- Moved out: the RCU comparison (now in Related Work, pointing to Section III's commit), the memory-planner
  comparison (Related Work), "a second slot helps only under an admission cap" (Section V-C already says
  it), the A100 platform caveat (Limitations), and the paragraph that repeated the full-retention point.
- No term is used before it is defined: no "commit" or "admission cap" in Section I, and no Fig. 5 bar
  labels.
- Results paragraph states the condition with the number: with early-reading recipients, 1.31-1.50x the
  timely results of full retention at 8-11 ms more mean latency; because REALBIM derives each reader's last
  read, it identifies the late readers for which a private copy delivers more.
- Contribution 1 leads with what is new ("BIM extends the per-recipient borrow bits of reference-counted
  transports [13] to GPU slots, clearing them with GPU completion events ..."). Contribution 3 is now "A
  derived release point that stays correct as models change".

## Abstract
- Copies in the middle, safety result last; the baseline in the safety sentence is named ("a common policy,
  which releases the buffer once all submitted GPU work completes"); latency kept.

## Less defensive, fewer habits
- The "deriving costs nothing" refrain is gone from the contribution title, the opening of Section V, V-B,
  and V-D; those places now end on the number (within 0.2 results/s; within 0.13 points).
- Maxims removed or turned into plain statements ("Releasing too early fails silently" heading is now
  "Stream-only release"; "A boundary is only as good as ..."; "Copying helps where early reuse cannot";
  "the derived last read tells the two cases apart"); "which organizes the paper" dropped.
- V-B explains the 30-34 ms hold as part of the description, not as a rebuttal.
- Stacked absolutes thinned in V-E ("the 109,592 results", "the outputs matched").
- The Discussion's borrow-or-copy paragraph ends on Fig. 6d and Section V-D.

## Tables and names
- Table I keeps the conceptual rows (stream-only, full retention, clone-on-accept, hand-placed, REALBIM);
  the two-slot row is gone (V-C gives its numbers), and K and the baseline footnote no longer appear there.
- The baselines are "Hand-placed (standalone)" and "Hand-placed (REALBIM runtime)" in the text and
  Table II (Hs, Hr). Each plot shows one of them and labels it "Hand-placed"; captions say which.
  Figs. 6-7 legends: "Manual" -> "Hand-placed", with the "Full" entry moved right to make room
  (figures/src/relabel_r32.py; nothing below the legend changed). Fig. 8: "REALBIM-manual" -> "Hand-placed".

## Please confirm
1. The reworded safety sentence calls stream-only release "a common policy"; Section I names it
   stream-only release.
2. Contribution 3 cites the 16 replayed model changes and the 0.08-0.21 s rebuild time from Section V-E.

# r31: outside reviewer, fourth round; Fig. 1 redrawn; tone

Built from the r30 source. No experiment was rerun and no measured number changed (every number in the
source compared with r30). Eight pages, page 8 full; references unchanged (30).

## Fig. 1 (right half redrawn)
- The BEV map is a stack of channel slices whose front face carries a feature texture rendered from the
  same nuScenes sweep (render_bev.py, bev_feat.png; an illustration, not a model output, as the caption
  says). Dimensions 180 x 180 x 512 sit on the stack; the size is a badge under the title.
- Shaded GPU-memory panel, soft shadows under the panels and reader cards, a round camera badge on the
  fusion arrow, a rounded branching connector, and the open question set as a coral callout.
- Caption: "four recipients" (the four processes), not "four readers".

## Plots (figures/src/relabel_r31.py; no data touched)
- Fig. 8: REALBIM-manual is now a blue hatch (a hatched REALBIM) instead of the orange hatch that Manual
  uses in Figs. 6-7.
- Figs. 6-7: legend "Full retention" becomes "Full", matching Fig. 8 and the text.
- Fig. 5: "Clone source early/mid-graph/late" become "Add early/mid-graph/late read", pairing with "Remove
  late read" and no longer echoing Clone-on-accept. Text references updated.

## Text
- Abstract: the reordering result is stated plainly (one reader finished before another submitted; the
  late reader computed on the next frame every time; REALBIM kept it on the correct frame and refused all
  22 plans run against changed code, model state, or inputs). The copy sentence carries its cost (256 MiB)
  and ends on the thesis: the derived last read tells early and late readers apart.
- Running example: engine A stands in for a second head compiled to TensorRT (as when BEVFusion's
  detection and segmentation heads read one map), graph B is the detection head; no longer "a deliberate
  stress test".
- IV-C opens with the failure the check prevents (a boundary that falls before a read the running program
  performs), then says why each token is in T, including input layout (aliasing depends on strides).
- Concessions reframed: "the gain comes from the release point, and deriving it automatically gives none of
  it up"; Section V calls the hand-placed baselines a yardstick. BIM is claimed the same way in the
  contributions and Related Work (per-recipient bits as in reference-counted transports, plus frame
  identities and bits cleared by GPU completion events), with no "foundation, not novelty".
- Contribution 3 names what the evaluation shows. V-E points back to the ResNet-18 residual read, where a
  hand-placed boundary after the first read would fail unnoticed.
- Table II gains a Policies column. "Served" becomes "computed on". Intro says on the spot that a second
  slot helps only under an admission cap (Section V-C). Limitations end on the next platform to measure.
- Tone pass: hedges and self-undercutting phrases removed; long sentences split (sentences over 35 words:
  21, over 45: 3, all three counter artifacts).

## Please confirm
1. IV-C's reason for input layout in T: aliasing depends on strides (a reshape returns a view only when the
   strides allow it). This is PyTorch's behavior; please confirm it is why the prototype binds the layout.
2. The new framing of engine A as a stand-in for a second compiled head (the experiments are unchanged).
3. The artifact link still points to tag ispa2026-r19; please confirm that tag reproduces these numbers.
4. Table I's footnote on stream-only release was dropped to make room; Section II states the same point.

# r30: outside reviewer, third round

Built from the r29 source. No experiment was rerun and no measured number changed (checked by comparing
every number in the source with r29). Eight pages, page 8 full; references unchanged (30).

## What is new, and what the results credit
- Novelty paragraph just before the contributions: zero-copy transports end a reference when the
  application drops it; nothing tells the application where a GPU reader's reads end, whether a reader
  that has not submitted work still needs the data, or whether that answer survives a model change;
  REALBIM answers all three, so the reference can end at the last read.
- Contributions: BIM is presented as the foundation ("as in reference-counted transports"), ReadSeal as
  the new layer, and the evaluation as separating the value of early release from what REALBIM adds.
- Related Work echoes it: BIM's bits work like Agnocast's (foundation, not novelty); the difference is
  where a reference ends. PyTorch 2 guards: a failed guard recompiles, a failed binding refuses to run.
- Section V opens by saying which results credit what: delivery and latency measure releasing at the
  last read, which hand-placed baselines also achieve by design; REALBIM's contribution is releasing
  there safely without hand placement, tested in V-E. V-B says the gain belongs to early release.
- Abstract rewritten: one safety result (reordered reads: stream-only release served the next frame in
  every test, REALBIM the admitted one; all 22 substitutions rejected), one throughput result, and the
  trade-off sentence. "A stale plan is refused before it runs" replaces "can never free the buffer early";
  "early-reading recipients" and "a tuned cap on outstanding requests" are gone.
- Discussion opens with "Borrow or copy": where the last read falls decides whether to borrow or copy,
  and REALBIM computes that point. The conclusion ends on the same thesis.

## Figures
- New Fig. 2 (column width): the two-lifetime timeline, beside the key-observation paragraph, with a
  slot row (frame k, then frame k+1 may enter), readers A and B, both lifetimes, and where stream-only
  release, REALBIM, and full retention free the slot. Built only from terms defined in Section I.
- The architecture figure (now Fig. 3) loses the timeline, drops to two slots, and is 37 pt shorter;
  it is defined in Section II so it lands on the page where Section III begins. Its caption no longer
  gives reading directions.
- Fig. 5's bars are named where Section I cites them (Read alias late, Clone source late, ResNet panel).
- Fig. 8 legend: "Manual-checked" relabeled "REALBIM-manual" (figures/src/relabel_r30.py; no pixel
  outside the label box changed, qa/relabel_r30_report.json).

## Vocabulary
- Slot and source: "the source is the tensor a slot holds: we say slot when we mean memory to reuse and
  source when we mean data that operations read."
- New "Life of a frame" paragraph in Section III walks frame k through admit, commit, descriptor,
  accept, check, enroll, last read, borrow returned, slot reused, and results delivered, using the
  numbered steps of Fig. 3.
- Baselines: Manual (a standalone runtime) and REALBIM-manual (REALBIM with a hand-placed boundary);
  Table I's row is now "Hand-placed".
- RCU: "read-side section, the interval in which it may read".

## Evaluation setup
- New Table II, one row per experiment (rate, slots and K, runs, metric, where), replaces most of the
  runs paragraph; the paragraph keeps queue limits, durations, and why each interval method is used.
- Metric bridge: "65.5% of frames, i.e., 78.6 of the 120 results/s offered, the GPU's capacity".
- 78.5 (Fig. 7a) vs 78.6 (Fig. 6d): "from separate runs".

## Running example and smaller points
- Section II now says the A+B composition is a deliberate stress test, why such mixes arise, and what
  each reader produces (A: pooled features; B: the detections); V-A no longer repeats it.
- The intro parenthetical "(the hold still drops only from 51 to 30-34 ms)" is gone; V-B already
  explains it.
- IV-C: "the check asks something else: is the model the caller is about to run still the one the plan
  was built from?"

## Made room for the above
- Algorithm 1 is no longer printed: the life-of-a-frame paragraph, Fig. 3, and Sections III-IV give every
  step. It stays in main.tex as a comment and can be restored by uncommenting it (about 16 lines).
- Shorter abstract (255 words), conclusion, contribution bullets, captions of Figs. 1-3, CUDA-backend
  sentence, and several paragraph endings; NvSciStream moved from Section I to Related Work.

## Please confirm
1. Table II, "Vs. copies" row: one slot and no cap are inferred (REALBIM's 5,078 MiB device peak and its
   60.0 results/s match the one-slot, uncapped runs); the paper does not state them for that study.
2. Table II, campaigns "6 (+12)": six runs per bar plus the 12 all-late runs that the original text
   counted in the campaigns.
3. "78.6 in Fig. 6d, from separate runs": Fig. 6d's base-head bars come from the late-read runs (the 144
   rate and late-read runs are 108 sweep runs plus 36 late-read runs), not from the slot study.
4. Reader outputs in Section II: engine A "produces pooled features" (global average pooling) and graph B
   "produces the detections".
5. Removing Algorithm 1 from the printed paper.

# r29: Fig. 1 redrawn around a real LiDAR sweep

Built from the r28 source. Only Fig. 1 and its caption changed; no experiment was rerun and no number
changed. Eight pages, page 8 full; references unchanged (30).

## Fig. 1
- The cartoon road scene is replaced by a real nuScenes-mini LiDAR sweep seen from above (72 m across,
  ego vehicle at the center, points colored by height above the ground, 10 m scale bar, faint 6 m grid).
  It is drawn with `figures/src/render_bev.py`; source and license in `figures/src/NUSCENES-NOTICE.txt`.
- The BEV map is drawn as one 512 x 180 x 180 tensor (dimensions on its edges) inside a "GPU memory" box,
  with its size (63.3 MiB) under the label.
- One horizontal flow line runs from the sweep through the fusion step and the map to the readers; the
  four readers hang off a single branch line instead of a fan of dotted arrows.
- Detail fixes: the panel, the GPU-memory box, and the reader boxes share top and bottom edges; labels
  no longer overlap points or each other; icons sit on matching tiles; the open question is
  left-aligned with the GPU-memory box. The unused radar icon was dropped.
- Caption: "Fusing each LiDAR sweep (left, from nuScenes [6]) with camera images yields a 63.3 MiB map
  in GPU memory." The sweep is not claimed to be one of the three evaluated frames.
- nuScenes is now first cited in this caption, so it moves from [24] to [6]: r28's [6]-[23] become
  [7]-[24], and [25]-[30] keep their numbers. The bibliography itself is unchanged.

# r28: response to an outside reader's review; scenario figure

Built from the r27 source. No experiment was rerun and no measured number changed, with one exception
noted below (a count in V-E that contradicted Fig. 4 was removed, not replaced). Eight pages, page 8 full.
References 38 -> 30.

## Names and vocabulary
- REALBIM is expanded once (REAd-Last BIM), in the abstract and in Section I.
- BIM now stands for Borrow-in-Memory, so the name no longer ties the layer to BEV maps; the conclusion
  says that nothing in either layer is specific to BEV maps.
- The two hand-placed baselines are labeled by runtime: Manual (own runtime) and Manual-checked
  (REALBIM's runtime), in Section V-A and in Table I's footnote.
- Section V-A defines pending (queued, not yet accepted) and in flight (accepted, results not delivered).

## What is new, stated early
- The RCU contrast moved from Related Work into Section I with its contrast clause: RCU protects only
  readers that announced themselves; BIM's commit opens every recipient's read-side section on its
  behalf, and ReadSeal closes it at the last read.
- The two-lifetime view is now the organizing idea ("Our key observation, which organizes the paper"),
  not a contribution; the contributions are BIM, ReadSeal, and the evaluation.
- New paragraph in Section I with the three-way trade: against full retention REALBIM wins on
  throughput; against copies it delivers about as much with early readers without their memory, but
  copies win when any recipient reads late; against stream-only it never serves the wrong frame. It
  says plainly that the target is shared-DRAM SoCs and that the measurements are on a discrete A100.
- The abstract reports the comparison with copies.
- The SoC argument is numeric: the 15 GiB/s of copy traffic is about 8% of an AGX Orin-class module's
  204.8 GB/s (NVIDIA data sheet, new reference [7]).

## Figures
- New Fig. 1 (column width): a top-down driving scene on a BEV grid, one 63.3 MiB BEV map in GPU memory,
  four reader processes, and the question of when frame k+1 may overwrite it. Paragraph 1 cites it
  instead of the architecture figure.
- The architecture figure is now Fig. 2; its caption first tells readers to start with the timeline at
  the bottom of (b) and to treat the rest as a map of Sections III-IV.

## Evaluation setup (Section V-A)
- K is off except in the slot study (Fig. 6), which compares no cap, K=4, and K=8.
- The interval methods carry a reason: the sweeps report ratios and paired differences (paired bootstrap),
  the campaigns report per-policy fractions (t intervals).
- The 168-run comparison with Clone-on-accept and the 12 all-late runs are introduced in the setup.

## Smaller snags
- Section I: "nothing flags the mistake"; half a sentence foreshadows the 30-34 ms hold (Section V-B).
- Abstract: the binding check's purpose ("so a stale release point can never free the buffer early");
  "a tuned cap on outstanding requests" instead of the undefined "admission cap".
- IV-C: why T includes the model state although the boundary depends only on the graph.
- V-D: 65.5% is the GPU's ceiling (about 78.6 of the 120 results/s offered at 30 Hz).
- V-C: what time-averaged held storage means when the device peak is the same for every policy.
- V-A: the engine A + graph B composition is called a stress test, with where such mixes arise.
- V-E: "the point at which the borrow is returned moves in 13 of them" contradicted Fig. 4, where the
  private-op edits leave the last read at operations 1 and 12. The sentence now says which edits move
  it and which do not, without a count.

## Space
To fit the scenario figure and the new text in eight pages: Related Work was compressed (it repeated
the introduction's positioning); the Discussion's release-policy paragraph became one sentence; several
paragraphs were tightened; and eight references cited only for breadth in Related Work were removed
(Blass et al. RTSS'21, Paella, RT-Swap, vLLM, Capuchin, PEBR, Martinez et al., Buttazzo), as was the
Legion visibility paper. The NVIDIA Orin data sheet was added.

## Please confirm
- "Pending" and "in flight" are defined as above; check that "four in flight" excludes queued requests.
- The rationale for bootstrap vs. t intervals is inferred from what each analysis reports; replace it if
  the real reason differs.
- The 168-run comparison is described as early readers at 20-40 Hz and all readers late at 30 Hz, from
  the conditions V-D reports; correct it if the design was different.
- V-E: restore an exact count of transitions whose release point moves, from the artifact, if wanted.
- "Such mixes arise when part of a model is compiled to an inference engine and the rest stays in the
  framework" is a general statement without a citation.
- The Orin data sheet reference gives the product page URL; DS-10662-001 lists 204.8 GB/s for the 64 GB
  module.

