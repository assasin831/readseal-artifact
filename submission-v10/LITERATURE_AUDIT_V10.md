# Primary-source literature check, 15 September 2026

| Added paper | Venue / published pages | Primary sources | Supported comparison |
| --- | --- | --- | --- |
| Welder: Scheduling Deep Learning Memory Access via Tile-graph | OSDI 2023, 701-718 | https://www.usenix.org/conference/osdi23/presentation/shi | Tile-level memory-access planning inside tensor execution, not a substitute for registering external future readers. |
| PyTorch 2: Faster Machine Learning Through Dynamic Python Bytecode Transformation and Graph Compilation | ASPLOS 2024, vol. 2, 929-947; DOI 10.1145/3620665.3640366 | https://docs.pytorch.org/assets/pytorch2-2.pdf ; https://api.crossref.org/works/10.1145/3620665.3640366 | Section 3.3 explicitly checks dynamic properties through guards before reuse of a compiled artifact. ReadSeal is not the inventor of executable guards. |
| GMLake: Efficient and Transparent GPU Memory Defragmentation for Large-scale DNN Training with Virtual Memory Stitching | ASPLOS 2024, vol. 2, 450-466; DOI 10.1145/3620665.3640423 | https://www.cs.sjtu.edu.cn/~leng-jw/pubs/guo2024asplos-gmlake.html ; https://api.crossref.org/works/10.1145/3620665.3640423 | Allocation fragmentation and virtual-memory stitching differ from when an externally shared input can be returned. |
| Orion: Interference-aware, Fine-grained GPU Sharing for ML Applications | EuroSys 2024, 1075-1092; DOI 10.1145/3627703.3629578 | https://2024.eurosys.org/accepted-papers.html ; https://www.research-collection.ethz.ch/items/6751d4b6-de56-40e3-ba70-e3f5740c5eef ; https://anakli.inf.ethz.ch/papers/orion_eurosys24.pdf | Operator-granularity interference-aware scheduling motivates separating admission and execution effects from safe storage return. |
| Colocating ML Inference and Training with Fast GPU Memory Handover (SIRIUS) | USENIX ATC 2025, 1657-1675 | https://www.usenix.org/conference/atc25/presentation/wang-jiali | Inference/training memory reclamation and latency-aware handover; no unsupported head-to-head performance comparison. |

Author order, venue, DOI and published page ranges were checked against official
conference, author-institution, project-paper and DOI registration sources.
PyTorch 2's long author list is abbreviated with BibTeX `and others`; other
entries retain their source author lists. Metadata verification is not a claim
to have reproduced those systems.

School name verified against the official English introduction:
https://xxxyen.lzu.edu.cn/introduction/index.html

The two user-supplied NPC examples concern federated learning. Their prose and
irrelevant references are not reproduced in ReadSeal. No citation is added
solely because it is associated with NPC, an author affiliation or a publisher.
