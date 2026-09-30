"""Reproduce the r21 main.tex from the r20 main.tex with exact-match replacements.

Usage: python qa/r21/edit_r21.py path/to/r20/main.tex path/to/r21/main.tex
Each old string must occur exactly once, so the script fails loudly on any other input.
"""

import sys
from pathlib import Path

EDITS = [
    # 1. Abstract: open with the common situation, state the challenge once, then tell the
    #    story (insight -> BIM -> ReadSeal -> results) and keep the trade-off to one clause.
    (r"""Processes in a perception pipeline often share one large GPU tensor rather than giving each a private copy. The producer must then decide when it may overwrite the shared buffer with the next frame. CUDA stream-only release reuses the buffer once all submitted GPU work has finished, so a recipient that has not started can silently compute on the next frame. Full retention is safe but waits for every result, refusing new frames while the GPU is idle. We observe that a shared tensor has two lifetimes: its storage is needed only until the last read completes, whereas its frame identity must last until every result is delivered. BEV-in-Memory (BIM) registers every recipient process when a frame is published, so no recipient loses its frame before it starts reading. Inside each recipient, ReadSeal analyzes storage sharing in the model graph to find the last operation that reads the shared tensor, and refuses to run a plan that no longer matches the executing code, weights, or inputs. Recipients then finish on private intermediate results while the buffer already holds the next frame. In an A100 pipeline with four early-reading recipients, one BIM buffer delivers 1.31--1.50$\times$ as many correct, timely results as one-buffer full retention at 25--40\Hz. Relative to that baseline, mean latency increases by 8--11\ms{} and 95th-percentile latency by 15--19\ms. At 30\Hz, one BIM buffer also matches the timely delivery of full retention with two buffers and a tuned cap on outstanding requests. Derived read boundaries deliver as much as hand-placed ones and are rebuilt automatically when the model changes. In ordered tests, a reader that submitted its work late computed on the next frame under stream-only release, but never under BIM.""",
     r"""Autonomous-driving and robotics software runs as many processes, such as ROS~2 nodes, and several of them often consume the same sensor data. As perception moves to the GPU, that data is increasingly one large tensor, such as a bird's-eye-view (BEV) feature map, and ROS~2 has begun to support sharing it in GPU memory instead of copying it for each recipient. The producing process must then decide when to overwrite the shared buffer with the next frame: too early, and a recipient that has not yet started can read the wrong frame; too late, and new frames are dropped while the GPU idles. Our key observation is that a shared tensor has two lifetimes: its storage is needed only until the last operation that reads it, whereas its frame identity must last until every result is delivered. BEV-in-Memory (BIM) builds on this by registering every recipient process when a frame is published, protecting each one before it starts reading. Inside each recipient, ReadSeal analyzes storage sharing in the model graph to find the last operation that reads the shared tensor, and it runs the plan only while the code, weights, and inputs still match. Recipients then finish on private data while the buffer already holds the next frame. In an A100 pipeline with four early-reading recipients at 25--40\Hz, one BIM buffer delivers 1.31--1.50$\times$ as many correct, timely results as a buffer held until all results are ready, for 8--11\ms{} more mean latency; at 30\Hz, it matches two such buffers with a tuned request cap. Automatically derived release points deliver as many results as hand-placed ones and follow model changes without manual updates."""),

    # 2. Introduction, first paragraph: start from the common multi-process setting.
    (r"""Consider a driving stack built on Autoware or another framework based on ROS~2, the Robot Operating System~\cite{autoware,ros2}. A camera--LiDAR fusion node publishes a bird's-eye-view (BEV) feature map, a top-down grid of features around the vehicle, and separate processes for 3D detection, tracking, motion planning, and data recording read it on their own schedules (Fig.~\ref{fig:overview}a).""",
     r"""Autonomous-driving stacks such as Autoware run as many processes on ROS~2, the Robot Operating System~\cite{autoware,ros2}, and several of them often consume the same data. A camera--LiDAR fusion node, for example, publishes a bird's-eye-view (BEV) feature map, a top-down grid of features around the vehicle, and separate processes for 3D detection, tracking, motion planning, and data recording read it on their own schedules (Fig.~\ref{fig:overview}a)."""),

    # 3. Introduction: state the asynchronous-GPU fact the whole problem rests on.
    (r"""Two common release rules err in opposite directions (Section~\ref{sec:motivation}). \emph{CUDA stream-only release}""",
     r"""Two common release rules err in opposite directions (Section~\ref{sec:motivation}). GPU work is asynchronous: other processes can wait only for work already submitted. \emph{CUDA stream-only release}"""),

    # 4. Introduction: say plainly what is new relative to per-consumer release.
    (r"""We present BEV-in-Memory (BIM), a cross-process borrowing contract motivated by BEV sharing,""",
     r"""We present BEV-in-Memory (BIM), a cross-process borrowing protocol motivated by BEV sharing,"""),
    (r"""but they leave the application to decide at which point in its computation to return it and how to cover components that have not started reading.""",
     r"""but they leave the application to decide at which point in its computation to return it and how to cover components that have not started reading. BIM and ReadSeal settle both: a borrow starts at publication and ends at a derived, checked last read."""),

    # 4b. Introduction: tighten the results summary (the details follow in Section V).
    (r"""With early source reads, one BIM slot delivers 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz{} and, at 30\Hz, matches two full-retention slots with a tuned request cap while using one fewer 64\MiB{} buffer; mean latency rises by 8--11\ms. Early release also changes how a pool should be sized: given a second slot and no cap, BIM admits more work than the GPU can finish in time, and its timely results fall from 78.5 to 24.9 per second. Derived boundaries deliver as much as hand-placed ones and follow model changes automatically. When a recipient reads the source late, early release gains nothing, and per-recipient copies are the better choice if memory allows.""",
     r"""With early source reads, one BIM slot delivers 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz, for 8--11\ms{} more mean latency, and at 30\Hz{} matches two full-retention slots with a tuned request cap while using one fewer 64\MiB{} buffer. Derived boundaries deliver as much as hand-placed ones and follow model changes automatically. Early release also changes pool sizing: a second slot then needs a request cap. When a recipient reads the source late, per-recipient copies are the better choice if memory allows."""),

    # 5. Introduction: define "tail" at first use.
    (r"""but in a ResNet-18 tail~\cite{resnet} the residual connection reads the source again at operation~12.""",
     r"""but in a ResNet-18 tail, the network after its first layers~\cite{resnet}, a residual connection reads the source again at operation~12."""),

    # 6. Fig. 1 caption: say why panel (b) shows these two readers.
    (r"""(b)~TensorRT engine~A and exported graph~B are the two readers of the last recipient still holding a borrow; time runs left to right.""",
     r"""(b)~TensorRT engine~A and exported graph~B, the two readers of the last recipient still holding a borrow, decide when the slot can be reused; time runs left to right."""),

    # 7. Section II: explain why one recipient has readers on two runtimes.
    (r"""The same gap can open inside a recipient that combines a TensorRT engine (NVIDIA's inference runtime) with a framework graph. In our running example (Fig.~\ref{fig:overview}b), the two readers are TensorRT engine~A, which signals an input-consumed event after reading its input~\cite{tensorrt}, and exported graph~B. An adapter forwards a view to the graph without reading the source itself.""",
     r"""The same gap can open inside one recipient whose readers run on different runtimes, each with its own completion signal. In our running example (Fig.~\ref{fig:overview}b), the two readers are TensorRT engine~A (NVIDIA's inference runtime), which signals an input-consumed event after reading its input~\cite{tensorrt}, and exported graph~B, which receives a view of the source from an adapter that does not read it."""),

    # 8. Section III: define request and output sink before the cap uses them.
    (r"""An optional request cap~$K$ bounds the recipient requests outstanding between admission and receipt at the output sink; a frame is admitted only if a slot is free and the cap has room for it.""",
     r"""Each admitted frame gives every recipient one \emph{request}, outstanding until its result reaches the \emph{output sink}, the process that collects results. An optional cap~$K$ bounds outstanding requests across the pipeline; a frame is admitted only if a slot is free and the cap has room for it."""),

    # 9. Section IV-A: describe the graph and the operator summaries without compiler jargon.
    (r"""The analysis runs on each graph, a fixed-shape, functional directed acyclic graph (DAG) of operations.""",
     r"""The analysis runs on each reader's exported graph: a directed acyclic graph (DAG) of operations with fixed tensor shapes."""),
    (r"""Operator summaries cover 42 reviewed operator variants in ATen, PyTorch's operator library, plus fixed-index tuple selection. Each summary counts every operand as read and treats an output as sharing storage whenever the operator's declared signature permits aliasing with an input. Plan construction rejects unsupported mutation, opaque callbacks, and source views that escape the graph.""",
     r"""The sets $\mathcal{A}_o$ and $\mathcal{R}_o$ come from reviewed summaries of 42 operator variants in ATen, PyTorch's operator library, plus fixed-index tuple selection. Each summary conservatively counts every input as read and lets an output share storage whenever the operator's declared signature permits it. Plan construction rejects what it cannot analyze: unsupported in-place updates, calls into code it cannot inspect, and source views that leave the graph."""),

    # 10. Section IV-B: define "accept".
    (r"""When that process accepts a frame, ReadSeal registers, or \emph{enrolls}, all of its readers before any of them submits GPU work.""",
     r"""When that process \emph{accepts} a frame, taking its request from the queue, ReadSeal registers, or \emph{enrolls}, all of its readers before any of them submits GPU work."""),

    # 11. Section IV-C: avoid the second meaning of "buffer" and make the tokens concrete.
    (r"""copies the model's parameters and buffers once into plan-owned storage,""",
     r"""copies the model's weights and other state, such as normalization statistics, once into plan-owned storage,"""),
    (r"""identifiers and metadata for code and globals, model storage and version, input layout, and compiled stages. At acceptance and at each stage entry it compares them with the values $\hat T$ for the execution about to run and proceeds only if $\hat T=T$.""",
     r"""identifiers and metadata for code and global variables, model storage and version, input layout, and compiled stages. At acceptance and at each stage entry it compares them with the values $\hat T$ for the execution about to run and proceeds only if $\hat T=T$, so other code, weights, or input layouts fail the check."""),

    # 12. Section V-A: define the recurring terms used in the evaluation.
    (r"""Without NVIDIA's Multi-Process Service (MPS), recipient kernels take turns on the GPU.""",
     r"""Without NVIDIA's Multi-Process Service (MPS), recipient kernels take turns on the GPU rather than running concurrently."""),
    (r"""A pretrained ResNet-18 tail~\cite{resnet}, the residual stages and classifier with saved stem activations as the source,""",
     r"""A pretrained ResNet-18 tail~\cite{resnet}, its residual stages and classifier reading saved activations of the first layers as the source,"""),
    (r"""All policies share the pool, workloads, queues, and admission settings. BIM uses ReadSeal,""",
     r"""All policies share the pool, workloads, queues, and admission settings. \emph{BIM} uses ReadSeal,"""),

    # 13. Section V-B: explain the GPU-capacity line and why the gain appears from 20 Hz.
    (r"""Early reuse pays off once the frame period drops below full retention's hold time (Fig.~\ref{fig:delivery}a). Both policies keep up at 10 and 15\Hz. At 20\Hz, where Full accepts only every other frame, BIM delivers 1.95$\times$ Full's timely results, and at 25--40\Hz{} it delivers 1.31--1.50$\times$ as many, running near the GPU's capacity.""",
     r"""Early reuse pays off once the frame period drops below full retention's hold time (Fig.~\ref{fig:delivery}a). Because the recipients take turns on the GPU and Full's 51\ms{} hold spans nearly all of their computation, the GPU can finish at most about four results per 51\ms, or 78 results/s (dashed line). Both policies keep up at 10 and 15\Hz. From 20\Hz{} on, the offered load reaches this capacity, so each frame Full refuses leaves GPU time unused. At 20\Hz, where Full accepts only every other frame, BIM delivers 1.95$\times$ Full's timely results, and at 25--40\Hz{} it delivers 1.31--1.50$\times$ as many, running near capacity."""),
    (r"""The gain comes from a shorter hold. Full holds the slot for about 51\ms, nearly the entire computation of the four recipients, whereas BIM returns it after their source reads, in 30--34\ms{} (Fig.~\ref{fig:delivery}c).""",
     r"""The gain comes from a shorter hold: Full holds the slot for about 51\ms, whereas BIM returns it after the source reads, in 30--34\ms{} (Fig.~\ref{fig:delivery}c)."""),

    # 14. Section V-C: name the queueing effect behind the two-slot drop.
    (r"""A second slot removes that pacing and lets requests queue before the GPU can start them.""",
     r"""A second slot removes that pacing and lets requests queue before the GPU can start them; as with bufferbloat in networks, the longer queue adds delay but not throughput."""),

    # 15. Section V-D: separate the per-result copying study from the complete-frame study.
    (r"""with identical early-reading recipients it completes about two points fewer. A separate 168-run study returns to recipient-level measurement, counting individual timely results rather than complete frames.""",
     r"""with identical early-reading recipients it completes about two points fewer.

A separate 168-run study compares BIM with cloning by the per-result metric of Sections~\ref{sec:eval-delivery} and~\ref{sec:eval-slots}, timely results/s."""),

    # 16. Section V-E: say what an ordered-overwrite case checks, and explain folding.
    (r"""We then change the models. Across eight graph snapshots per model, three inputs, and two methods, regenerated boundaries kept all 96 ordered-overwrite cases exact against unsplit references, and binding validation rejected""",
     r"""We then change the models. In 96 ordered-overwrite cases (eight graph snapshots per model, three inputs, and two methods), the source was overwritten once the regenerated boundary had completed, and every output still matched the unsplit model's exactly. Binding validation rejected"""),
    (r"""one batch-normalization folding, and a public ResNet-18 to ResNet-50 substitution,""",
     r"""one folding of batch normalization into the preceding convolution, and a public ResNet-18 to ResNet-50 substitution,"""),

    # 17. Section V-F: "tails" of models.
    (r"""A static survey of 14 torchvision tails accepts nine,""",
     r"""A static survey of the tails of 14 torchvision models accepts nine,"""),

    # 18. Page budget: remove repetition so the added explanations fit in eight pages.
    # 18a. Section V roadmap: the subsection titles already name each question.
    (r"""Section~\ref{sec:eval-delivery} measures what ending borrows at the last read gains under load and costs in latency; Section~\ref{sec:eval-slots} compares one early-released slot with two fully retained ones; Section~\ref{sec:eval-mixed} adds jitter, a late reader, and copying; Section~\ref{sec:eval-safety} tests safety under reordering and model changes; and Section~\ref{sec:eval-cost} measures what the checks cost.""",
     r"""We measure what early reuse gains and costs under load (Sections~\ref{sec:eval-delivery}--\ref{sec:eval-mixed}), whether it stays safe under reordering and model changes (Section~\ref{sec:eval-safety}), and what its checks cost (Section~\ref{sec:eval-cost})."""),
    # 18b. The cap is now defined in Section III.
    (r"""When set, the cap~$K$ limits outstanding requests across the pipeline; $K{=}8$ accommodates two full groups of four.""",
     r"""A cap of $K{=}8$ accommodates two full groups of four requests."""),
    # 18c. Define the complete-frame metric once, where Section V-D switches to it.
    (r""" Section~\ref{sec:eval-mixed} also reports the \emph{complete-frame timely fraction}: the share of scheduled frames, refused and partially admitted ones included, whose four results are all correct and timely.""",
     r""""""),
    (r"""This study measures complete frames rather than individual recipient results (Fig.~\ref{fig:mixed}). A frame is timely only if all four results are correct and timely.""",
     r"""Instead of individual results, this study reports the \emph{complete-frame timely fraction}: the share of scheduled frames, refused and partially admitted ones included, whose four results are all correct and timely (Fig.~\ref{fig:mixed})."""),
    # 18d. Discussion: state the guidance once instead of repeating Section V's numbers.
    (r"""\textbf{Choosing a release policy.} With early reads, one BIM slot matched two full-retention slots with a tuned cap and delivered about as much as per-recipient copies without their 256\MiB. With a late read, early reuse gains nothing (Fig.~\ref{fig:delivery}d), and copying completed 22--32 points more mixed-recipient frames on time than BIM, at 20--25\ms{} more tail latency. Where memory is plentiful, extra slots or copies are simpler; early reuse fits systems whose memory capacity and bandwidth are too scarce for per-recipient copies.""",
     r"""\textbf{Choosing a release policy.} Early reuse fits systems whose memory capacity and bandwidth are too scarce for per-recipient copies: with early reads, one BIM slot matched two fully retained slots with a tuned cap and delivered about as much as copies without their 256\MiB. Where memory is plentiful, extra slots or copies are simpler, and when a read falls late (Fig.~\ref{fig:delivery}d), copies deliver more."""),
    # 18e. Conclusion: keep the headline result without restating every figure.
    (r"""In our A100 pipeline, where the detection head reads the shared map only in its first operation, ending borrows there let one slot deliver 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz{} and, at 30\Hz, as many as two full-retention slots with a tuned request cap, for 8--11\ms{} more mean latency.""",
     r"""In our A100 pipeline, where the detection head reads the shared map only in its first operation, ending borrows there let one slot deliver 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz{} and match two fully retained slots at 30\Hz."""),

    # 19. Page budget: trim a few words where a paragraph ends in a nearly empty line.
    (r"""frame identity, and it places full retention, copying, and early reuse on one axis.""",
     r"""frame identity, and places full retention, copying, and early reuse on one axis."""),
    (r"""computes the remaining results in private intermediate storage. If no operation reads the source, $Q_r$ is empty and we set $\beta=0$. Fig.~\ref{fig:boundaries} labels each graph snapshot with""",
     r"""computes the remaining results in private storage. If no operation reads the source, $Q_r$ is empty and we set $\beta=0$. Fig.~\ref{fig:boundaries} labels each snapshot with"""),
    (r"""Every enrolled reader takes part in this condition, including one that has enqueued nothing: when A's event completes, B's read is still pending, so the bit stays set. Once all recipients have returned their borrows, the producer can write the next frame while $j$'s private suffix keeps computing results labeled~$k$.""",
     r"""Every enrolled reader takes part in this condition, even one that has enqueued nothing: when A's event completes, B's read is still pending, so the bit stays set. Once all recipients have returned their borrows, the producer can write the next frame while $j$'s suffix keeps computing results labeled~$k$."""),
    (r"""new operators require reviewed summaries.""",
     r"""new operators need reviewed summaries."""),
    (r"""so the source storage held by outstanding borrows averages 52.3\MiB{} against Full's 86.4\MiB{} (Fig.~\ref{fig:slots}b). Returning a borrow makes a slot reusable without deallocating it, so the device peak is the same under every policy:""",
     r"""so source storage held by borrows averages 52.3\MiB{} against Full's 86.4\MiB{} (Fig.~\ref{fig:slots}b). Returning a borrow makes a slot reusable without deallocating it, so every policy has the same device peak:"""),
    (r"""adding a late read likewise made Manual-checked's old boundary fail its check until the boundary was moved,""",
     r"""adding a late read made Manual-checked's old boundary fail its check until it was moved,"""),
    (r"""and ReadSeal closes it at the derived last read.""",
     r"""and ReadSeal closes it at the last read."""),
    (r"""and use each reader's derived boundary to decide, recipient by recipient, whether to borrow or copy.""",
     r"""and use each reader's derived boundary to decide whether to borrow or copy."""),
]


def main():
    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    text = source.read_text(encoding="utf-8")
    for number, (old, new) in enumerate(EDITS, 1):
        count = text.count(old)
        assert count == 1, f"Edit {number}: expected one match, found {count}"
        text = text.replace(old, new)
    target.write_text(text, encoding="utf-8")
    print(f"Applied {len(EDITS)} edits to {target}")


if __name__ == "__main__":
    main()
