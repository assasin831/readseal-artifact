# Manuscript-to-evidence mapping

## NPC V12 experimental results, 15 September 2026

Evidence tag: `npc-results-v12`. Start with [NPC_V12_RESULTS.md](./NPC_V12_RESULTS.md).
This is the author-designated latest results package. It does not include a new
manuscript PDF or LaTeX source archive, and does not replace the older evidence.

| Delivered file | SHA-256 |
| --- | --- |
| `readseal_npc_v12_results_20260915.zip` | `d775f1b5be0eace0b4a338dd3b5c4fa116085f22fefacd600b31fccd39f8d47c` |

The byte-identical upload is 13,722,193 bytes and contains 104 files, including
the 103-entry internal checksum inventory. Its E1/E2 windows contain 108 and
36 formal runs respectively, plus six separate smoke runs. E3/E4/E6/E7 provide
bounded analyses and records; E5 is explicitly not run. Full raw blobs and
external model/runtime dependencies are not included in this compact package.
Archive verification before publication checked CRCs and all internal hashes,
not a new experimental replication. Scope and accounting are documented in
the [writing results](./results-v12/RESULTS_FOR_WRITING.md) and
[data dictionary](./results-v12/DATA_DICTIONARY.md).

## NPC V10, 15 September 2026

Evidence tag: `npc-submission-v10`. Start with [NPC_V10_GUIDE.md](./NPC_V10_GUIDE.md).
The manuscript is now titled ReadSeal: Checked Borrowing Plans for Asynchronous
GPU Tensor Sharing. This revision reorganizes the narrative and references,
defines the diagram's component roles and expands the conclusion. It adds
Sicheng Wu before Rui Zhou, identifies Rui Zhou and Qingguo Zhou as
co-corresponding authors, and uses the confirmed school affiliation.
All experiment files are unchanged from V9.

| Delivered file | SHA-256 |
| --- | --- |
| `readseal_npc_2026_v10.pdf` | `9cf0ed71f72db44af989e58f10c2e59aedd127f0b5f7e9363916bfb659226a5b` |
| `readseal_npc_2026_latex_v10.zip` | `c80f39b48b5ba0c528898d118b044bfd6c108f0a3334fc3191a90114bb230aa5` |

These files are delivered separately, not hosted here in full. The PDF remains
12 pages with unmodified official LNCS typography: 12 TeX point body baseline,
21 embedded font entries and no Type 3 fonts. It cites 18 academic papers and
five exact interface sources; seven papers are from 2023-2025. The abstract has
168 whitespace-delimited tokens and the two-paragraph conclusion 159.

V10 passes 124 source/PDF checks and the unchanged 2,230-check saved-evidence
reconstruction. All 12 pages were visually inspected. Clean extraction verifies
68 source inputs and recompiles to identical extracted text and page pixels at
a 1,300-pixel long edge. [NPC_V10_REPRODUCTION.json](./NPC_V10_REPRODUCTION.json)
records the result. The current diagrams, inputs and checks are inventoried in
[submission-v10/manifest.json](./submission-v10/manifest.json).

## NPC V9, 15 September 2026

Submission evidence tag: `npc-submission-v9`.
Start with [NPC_V9_GUIDE.md](./NPC_V9_GUIDE.md) and the updated
[claim-to-evidence map](./ARTIFACT.md). Existing experiment archives and tags are
unchanged. The paper links to this tag, not to a moving default branch.

| Delivered file | SHA-256 |
| --- | --- |
| `readseal_npc_2026_v9.pdf` | `44702447e8f00d98279b5eea40755f8b6af91173d87129dabf7b36113fc3aa4e` |
| `readseal_npc_2026_latex_v9.zip` | `dcff4b614ce3a0b8250a75bd921d25919612445e7f684db2cfd5db9e8fbdfadf` |

These files were delivered separately; this table is an identity record, not a
claim that the full manuscript or source ZIP is hosted in this repository.

The PDF has 12 pages including references. It uses the unmodified official
September 2026 LNCS class and the sample's Times font configuration; no compressed
line spacing remains. Measured body baseline is 11.955 PDF points (12 TeX points),
with 21 embedded font entries, no Type 3 fonts, 22 resolved/cited references and
minimum diagram text approximately 7.02 PDF points. The abstract contains 186
whitespace-delimited tokens. The confirmed no-competing-interests declaration and
factual AI-assistance disclosure are present.

The local saved-evidence reconstruction passes 2,230 checks, including all 192
original report/sink files. The graph-count audit reconciles the 8/85 and 12/123
ResNet records without executing a model. Source/PDF QA passes 83 mechanical
checks; every page was visually inspected. Clean extraction verifies all 66
inventoried source inputs and recompiles with pdfLaTeX/BibTeX. All 12 pages have
identical extracted text and pixels at a 1,300-pixel long edge; the rebuilt PDF
has a different byte hash. See
[NPC_V9_REPRODUCTION.json](./NPC_V9_REPRODUCTION.json).

This is neither a new GPU experiment nor an independent-team replication. Missing
historical CPU/OS/Python-patch/driver provenance is explicitly documented in the
guide rather than filled with current-machine information.

## NPC V4, 14 September 2026

Evidence tag: [`npc-evidence-v3`](https://github.com/assasin831/readseal-artifact/tree/npc-evidence-v3)

Evidence commit: `ddbb51613909857a3a6442f2202033ba5109de30`

Evidence archive: `readseal_npc_2026_reviewer_artifact_v3.zip`, 10,675,190 bytes.
SHA-256: `6deb8c63f74563b9a42280695cc8f5dbc88070e9b2be0bdc1eb36014ea2ceeb0`.
The tag and an anonymous archive download were verified on 14 September 2026.

The separately delivered V4 manuscript/source have these hashes. They are not
included in the older evidence archive and are not download links on this page:

| File | SHA-256 |
| --- | --- |
| `readseal_npc_2026_v4.pdf` | `f812984e1a8db05fe9ada3fab4a6ef914c35a601036f9dddbe4d5fa6f8c46f5c` |
| `readseal_npc_2026_latex_v4.zip` | `dd031af97750c63fbfb21b2fa216bc683e0b5b563888b4559846479e182bdd37` |
| V4 `figures/architecture.pdf` | `1ef437c35eff3f5967b0dd478f3207283c89f8f4199222c108c90417c9492f14` |
| V4 `figures/architecture.drawio` | `07f8181664a194207f3417cd89cdc3a64005e5611b72ef295b381e11f3d55682` |

V4 changes only presentation, bibliography, the main diagram and local manuscript
checks. Its 24 evidence JSON files, 90 runtime files, eight binding-output/reference
files, and Fig. 2 are byte-identical to V3. The 26 CUDA cases remain four accepted
and 22 rejected; the accepted cases yield 22 checked output tensors.

Local QA passed 196 manuscript checks and 651 aggregate/statistical checks.
All 171 inventoried source-package inputs were verified before a clean build.
The rebuilt 12-page PDF has identical extracted text and rendered page pixels
at the QA resolution. No new inference or independent-team replication is claimed.

The paper is not a conference submission receipt or an acceptance guarantee.
