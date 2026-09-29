# Revision 15 Change Record

## Scope

Readability and presentation revision of r14, with all six figures reconstructed from their original editable definitions. Experiments, plotted values, baselines, intervals, and adverse findings are unchanged.

## Advice Applied

| Reader concern | Revision |
|---|---|
| Abstract becomes an inventory of measurements | Focused on the problem, two-lifetime idea, BIM/ReadSeal roles, sustained delivery gain, and latency cost. Included tail-latency cost alongside the mean. |
| Manual matches BIM, so ReadSeal's contribution is unclear | Added an introduction paragraph distinguishing last-read reuse performance from automatic boundary derivation, maintenance, and execution checks. |
| Synonyms and unexplained implementation terms | Standardized the derived point as a read boundary; explained operator variants, tuple selection, binding tokens, and completion events. Expanded RCU on first use. |
| A and C appear before they are explained | Identified TensorRT engine A and exported graph C in Fig. 1's caption. Removed the unnecessary adapter letter B from the prose. |
| Two-reader composition sounds like a prevalence claim | Described the controlled composition without asserting that mixed-framework splits are common. |
| Results/s becomes publication percentage without warning | Defined a recipient result, four offered results per frame, and the all-scheduled-publication denominator together in V-A. Added the transition at V-D; removed the approximate results/s-to-frames/s conversion. |
| Manual and Manual-checked are confusing | Described both implementations together and named their respective campaigns. Moved saved labels to CAMPAIGNS.md. |
| Mean, p95, and p99 look interchangeable | Specified the population and per-run statistic of each study. Kept campaign settings and inference rules separate. |
| Two uncapped BIM slots perform worse than Full | Retained 24.9 versus 72.3 results/s and connected the loss to excess admission and queueing; separated pool size from request cap. |
| Repeated concessions dominate the story | Reduced repetition in the abstract, introduction, contributions, discussion, and conclusion. Kept comparisons beside the evidence and a compact policy discussion. |
| Scope qualifications recur throughout | Consolidated platform, saved BEV workload, and excluded front-end/ROS/embedded execution in V-A. |
| Run counts interrupt the argument | Retained replicate/interval definitions in the paper; collected totals and non-plotted confirmation records in CAMPAIGNS.md. |
| Ordered failures are conflated with safe under-load results | Reported the six ordered tests and 109,592 checked results as separate facts. |
| Proposition restates runtime premises | Focused Proposition 1 on conservative source-read analysis under sound summaries and analyzed execution order; stated runtime obligations separately. |
| Model updates sound like natural model history | Marked 14 of 16 transitions as constructed edits at first mention. |
| Intro contribution is a prior-work catalog | Described directly what BIM and ReadSeal do; retained comparisons in Related Work. |
| Last page is unbalanced | Balanced bibliography columns without reducing the body font size. |

## Deliberately Preserved

- All figure panels, including Fig. 5b's held-source-storage panel. Feedback suggested deletion, but the author requested one-to-one reconstruction.
- The opening, wrong-frame example, two lifetimes, library-loan analogy, and slice-versus-convolution explanation.
- The 1.95x period-alignment explanation, sustained 1.31-1.50x range, and private-suffix condition.
- Every plotted value, error bar, label, line, marker, color, hatch, and native drawing coordinate.
- Algorithm 1, Table I, four equations, author list, title, and bibliography entries.
- A100-only scope, late-reader copying advantage, extra latency, and adverse uncapped-two-slot result.

## Figure and PDF Delivery

All six PPTX slide XML trees match their r14 originals exactly. New PDFs use embedded fonts and no image downsampling. The paper uses vector PDFs, not PNG previews; each figure also has a 600 dpi PNG.

The final paper uses a lossless uncompressed export larger than 1 MiB. This is a packaging choice, not a claim that a larger file inherently has better resolution. No blank pages, filler bytes, or hidden attachments were added.

## Not Performed

No new inference, experiment selection, statistical reanalysis, acceptance prediction, or embedded validation. Existing archives and historical tags are preserved. Bibliographic records were retained, not subjected to a fresh reference audit.
