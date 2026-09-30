"""Rewrite main.tex for r18 with exact-match replacements.

Every edit must match exactly once, so equations, the algorithm, figures,
labels, and numbers outside the edited spans cannot change by accident.
"""
import sys
from pathlib import Path

path = Path(sys.argv[1])
tex = path.read_text(encoding="utf-8")


def rep(old, new):
    global tex
    n = tex.count(old)
    assert n == 1, f"expected 1 match, found {n}: {old[:70]!r}"
    tex = tex.replace(old, new)


def span(start, end, new):
    """Replace from a unique start marker through the first end marker after it."""
    global tex
    assert tex.count(start) == 1, f"start not unique: {start[:70]!r}"
    i = tex.index(start)
    j = tex.index(end, i) + len(end)
    tex = tex[:i] + new + tex[j:]


# ---------------------------------------------------------------- abstract
span(r"Processes in perception pipelines share large GPU tensors",
     r"rejection of stale plans.",
     r"""Processes in a perception pipeline often share one large GPU tensor instead of copying it for every recipient. When may the producer overwrite the shared buffer with the next frame? CUDA stream-only release waits only for submitted GPU work, so it can hand the next frame to a reader that has not started. Full retention waits for every result and refuses new frames while the GPU sits idle. Our key insight is that a shared tensor has two lifetimes: its storage is needed only until the last read completes, but its frame identity must last until every result is delivered. BEV-in-Memory (BIM) registers every recipient when a frame is published, protecting recipients that have not started. ReadSeal analyzes storage sharing in each model graph to find where the model stops reading the shared tensor, and refuses to run a plan that no longer matches execution. Recipients then finish on private intermediate results while the buffer already holds the next frame. In an A100 pipeline with four early-reading recipients, one BIM slot delivers 1.31--1.50$\times$ the correct, timely results of one-slot full retention at 25--40\Hz{} and, at 30\Hz, matches two full-retention slots with a tuned request cap, at 8--11\ms{} more mean and 15--19\ms{} more 95th-percentile latency. Derived boundaries deliver as much as hand-placed ones and are rebuilt automatically after model changes. Ordered tests show that stream-only release serves a pending reader the next frame, while BIM does not.""")

# ------------------------------------------------------------ introduction
rep(r"This motivates sharing on automotive systems-on-chip whose GPU shares DRAM with the rest of the stack~\cite{cudategra}.",
    r"The cost matters most on automotive systems-on-chip, whose GPU shares DRAM with the rest of the stack~\cite{cudategra}.")

rep(r"A queued recipient that has not submitted its reads can then silently compute on the next frame: a detector reports objects seen in frame $k{+}1$ under the timestamp of frame $k$. At 20\Hz, a vehicle driving at 20\,m/s moves a full meter between the two.",
    r"A queued recipient that has not submitted its reads can then silently compute on the next frame. A detector would report objects seen in frame $k{+}1$ under the timestamp of frame $k$, and at 20\Hz{} a vehicle driving at 20\,m/s moves a full meter between the two.")

span(r"\textbf{Key insight.} A shared tensor",
     r"copying can be preferable when that read comes late.",
     r"""\textbf{Key insight.} A shared tensor, the \emph{source}, has two lifetimes (Fig.~\ref{fig:overview}b). Its \emph{storage lifetime} ends when the last operation that reads it completes. Its \emph{provenance lifetime} lasts until every result is delivered, because those results still name the frame they came from, much as an essay keeps citing a library book after the book has gone back to the shelf. The two can differ widely. In the TransFusion detection head that reads our BEV map, only the first of 287 operations reads it; the remaining operations work on intermediate results in private storage and can continue after the shared input is overwritten. Each recipient therefore needs its \emph{borrow}, permission to read the slot, only until its last source read completes.

Seen this way, full retention, copying, and early reuse are three choices of where a borrow ends: when the recipient's outputs are complete, when its private copy is complete, or when its last source read completes. All three must protect a recipient from before it starts reading.""")

rep(r"A reader that has not yet submitted GPU work leaves nothing to wait on.",
    r"A reader that has not yet submitted GPU work leaves no event to wait on.")

span(r"We present BEV-in-Memory (BIM), a cross-process borrowing contract",
     r"the application.",
     r"""We present BEV-in-Memory (BIM), a cross-process borrowing contract motivated by BEV sharing, and ReadSeal, the mechanism that answers these questions. BufferQueue and NvSciStream already let each consumer return a shared buffer on its own~\cite{bufferqueue,nvscistream}, but they leave the application to decide where it should do so and how to cover components that have not started reading. The producer knows only which processes receive a frame, so BIM registers every recipient's borrow when the frame is published, before any recipient starts (Section~\ref{sec:bim}). Each process knows which of its components will read the frame, so ReadSeal enrolls them before they submit GPU work, derives each one's read boundary by alias analysis of its model graph, and binds the plan to the code, model state, and input layout that execute (Section~\ref{sec:readseal}).""")

span(r"Automating the boundary matters because",
     r"using one fewer 64\MiB{} source buffer.",
     r"""Deriving the boundary matters because a hand-placed one can go stale or be misplaced from the start. One added late read moves our detection head's boundary from the first operation to the second-to-last (Fig.~\ref{fig:boundaries}). And while the first operation is the right boundary for the head, in a ResNet-18 tail~\cite{resnet} the residual connection reads the source again at operation~12. A version check catches the first failure but not the second. ReadSeal recomputes the boundary for each model version and refuses to run a plan that no longer matches execution. Our contributions are:
\begin{itemize}
\item \textbf{The two-lifetime view of a shared GPU tensor} (Sections~\ref{sec:intro}--\ref{sec:motivation}). Separating storage from provenance shows when a buffer can be reused while results keep their frame identity, and places full retention, copying, and early reuse on one axis.
\item \textbf{Checked release at a derived last read} (Sections~\ref{sec:bim}--\ref{sec:readseal}). BIM protects every recipient from publication onward, including readers that have not submitted work, and ReadSeal derives where each reader stops reading and rejects plans that no longer match execution.
\item \textbf{An evaluation of the release choices} (Section~\ref{sec:eval}), comparing early reuse with full retention, extra slots, and copying under load, and testing the derived boundaries under ordered overwrites and model updates.
\end{itemize}

With early source reads, one BIM slot delivers 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz{} and, at 30\Hz, matches two full-retention slots with a tuned request cap while using one fewer 64\MiB{} buffer (Section~\ref{sec:eval-slots}); mean latency rises by 8--11\ms. Derived boundaries deliver as much as hand-placed ones and follow model changes automatically.""")

# ------------------------------------------------------ background section
rep(r"Full's 51\ms{} hold just exceeds the 50\ms{} frame period, so every other frame is refused although the recipients sit idle: full retention is not work-conserving.",
    r"Full's 51\ms{} hold just exceeds the 50\ms{} frame period, so it refuses every other frame even though the recipients sit idle; full retention is not work-conserving.")

rep(r"Add alias chain inserts two storage-sharing views: the operation indices shift, but the runtime release point is unchanged.",
    r"Add alias chain inserts two storage-sharing views, which shift the operation indices but leave the runtime release point unchanged.")

rep(r"\textbf{Holding the source through computation.} With one slot, full retention's 51\ms{} hold exceeds the 50\ms{} period at 20\Hz, so every other frame is refused while the GPU idles (Fig.~\ref{fig:trace}). Adding a slot absorbs some of those arrivals, but can also admit more work than the GPU finishes before the deadline. Section~\ref{sec:eval-slots} measures this interaction with the request cap.",
    r"\textbf{Holding the source through computation.} Full retention's hold refuses frames while the GPU idles (Fig.~\ref{fig:trace}). A second slot absorbs some of those arrivals but can admit more work than the GPU finishes before the deadline (Section~\ref{sec:eval-slots}).")

rep(r"\textbf{GPU background.} A \emph{kernel}",
    r"""Each release rule below ends a recipient's borrow at a different point; Table~\ref{tab:options} compares them.

\textbf{GPU background.} A \emph{kernel}""")

rep(r"An \emph{event} marks a position in a stream and completes after the preceding work.",
    r"An \emph{event} marks a position in a stream and completes after the preceding work.")

rep(r"But an event can mark only work already enqueued: no process can wait on reads that another has not yet submitted.",
    r"But an event can only mark work that is already enqueued, so no process can wait on reads that another process has not yet submitted.")

rep(r"ROS~2's CUDA buffer backend exposes the same choice: a subscriber's read handle records a read event when destroyed, and the block is recycled once every handle is released~\cite{cudabackend}; destroying the handle after the engine's read is stream-only release, and holding it until the outputs complete is full retention.",
    r"ROS~2's CUDA buffer backend exposes the same choice. A subscriber's read handle records a read event when it is destroyed, and the block is recycled once every handle is released~\cite{cudabackend}. Destroying the handle after the engine's read gives stream-only release; holding it until the outputs complete gives full retention.")

rep(r"so a hand-placed boundary must be reviewed after model changes. A stale boundary can release too early unless execution is guarded against that change. Section~\ref{sec:eval-safety} distinguishes changes to the actual runtime boundary from shifts in operation numbering. Table~\ref{tab:options} summarizes the release choices.",
    r"so a hand-placed boundary must be reviewed whenever the model changes. A stale boundary releases too early unless execution is guarded against the change.")

rep(r" Both require plan refresh after a rejected change.", r"")

# ------------------------------------------------------------------- BIM
rep(r"An arriving frame takes a slot whose bits are all clear. If none is free, the frame is dropped so the producer can keep its fixed arrival schedule; blocking would change the offered workload through backpressure. Once the frame is written, the producer \emph{commits} it by setting every recipient's bit before sending any descriptor. This protects even a recipient waiting in its queue.",
    r"An arriving frame takes a slot whose bits are all clear; if none is free, the producer drops the frame instead of waiting. Once the frame is written, the producer \emph{commits} it by setting every recipient's bit before sending any descriptor. This ordering is what protects a recipient still waiting in its queue, because its bit is set before it could possibly read.")

# -------------------------------------------------------------- ReadSeal
rep(r"Storage sharing propagates through views: a slice of the source is a view,",
    r"Storage sharing propagates through views. A slice of the source is a view,")

rep(r"where $Q_r$ is the set of operations that may read the source.",
    r"where $Q_r$ is the set of operations that may read the source.")
rep(r" Sections~\ref{sec:derive}--\ref{sec:bind} describe these parts in order.", r"")

rep(r"Operator summaries cover 42 reviewed operator variants in ATen, PyTorch's operator library, plus selection of a tuple element at a fixed index.",
    r"Operator summaries cover 42 reviewed operator variants in ATen, PyTorch's operator library, plus fixed-index tuple selection.")

rep(r" These runs are separate from the slot campaign in Fig.~\ref{fig:slots}.}",
    r"}")

rep(r"At construction, ReadSeal captures the functions to run and clones model parameters and buffers once into plan-owned storage to isolate them from later caller edits, as does the manual implementation. These per-plan allocations are separate from the per-frame input copies in Table~\ref{tab:options}.",
    r"At construction, ReadSeal captures the functions to run and copies the model's parameters and buffers once into plan-owned storage, so later edits by the caller cannot change a plan in use. The manual implementation does the same.")

# ------------------------------------------------------------ evaluation
rep(r"The evaluation answers five questions in turn: when early reuse pays and what it costs in latency (Section~\ref{sec:eval-delivery}, Fig.~\ref{fig:delivery}); whether a second slot could do the same (Section~\ref{sec:eval-slots}, Fig.~\ref{fig:slots}); how jitter, mixed recipients, and copying change the picture (Section~\ref{sec:eval-mixed}, Fig.~\ref{fig:mixed}); whether BIM stays safe under reordering and model change (Section~\ref{sec:eval-safety}); and what ReadSeal's checks cost (Section~\ref{sec:eval-cost}).",
    r"")

rep(r"This setup measures reuse and admission independently of feature extraction; it does not run ROS~2, the BEV front end, or an embedded driving stack. The runtime uses PyTorch 2.1.2, CUDA 12.1, and TensorRT 10.3.",
    r"Saved features isolate reuse and admission from feature extraction; the setup does not run ROS~2, the BEV front end, or an embedded driving stack. The runtime uses PyTorch 2.1.2, CUDA 12.1, and TensorRT 10.3.")

rep(r"This controlled composition gives each recipient two readers of the same source, each with its own completion event.",
    r"This controlled composition gives each recipient two readers of the same source, each with its own completion event.")

rep(r"A pretrained ResNet-18 tail, comprising residual stages and classifier with saved stem activations as the shared source,",
    r"A pretrained ResNet-18 tail~\cite{resnet}, made of the residual stages and classifier with saved stem activations as the shared source,")

rep(r"Two hand-placed baselines isolate different costs. \emph{Manual}, used in the rate and slot sweeps, independently registers both readers and checks code and model digests. It tests early reuse with a separately implemented runtime. \emph{Manual-checked}, used in the jitter and mixed-recipient tests, shares BIM's runtime and binding checks, changing only the placement of the boundary. It isolates automatic placement from execution checks.",
    r"Two hand-placed baselines come from different campaigns. \emph{Manual}, used in the earlier rate and slot campaigns, is a separately implemented runtime that registers both readers and checks code and model digests, so it tests early reuse independently of our runtime. \emph{Manual-checked}, used in the later jitter and mixed-recipient campaign, shares BIM's runtime and binding checks and differs only in where the boundary comes from, which isolates automatic placement.")

span(r"Each frame offers one \emph{result}",
     r"including refused frames and partial admissions.",
     r"""Each frame should yield four \emph{results}, one output bundle per recipient, so the offered load is $4\lambda$ results/s. A result is \emph{timely} if it passes source-identity and reference-output checks and reaches the output sink, after device-to-host transfer and IPC, within 100\ms{} of the frame's planned arrival. The 100\ms{} budget is a common benchmark threshold rather than a vehicle requirement, so we also re-score the slot runs at 80--200\ms. \emph{Receipt latency} runs from planned arrival to sink receipt; \emph{slot hold time} runs from commit to the last borrow return. The complete-frame timely fraction (Section~\ref{sec:eval-mixed}) counts a frame only if all four intended results are correct and timely, and its denominator includes refused and partially admitted frames.""")

rep(r"\emph{No pipeline-wide cap} leaves the per-recipient queue limits in place.",
    r"\emph{No pipeline-wide cap} leaves the per-recipient queue limits in place. Because the producer drops frames rather than blocking, every policy sees the same offered load.")



span(r"Early reuse raises timely delivery once the frame period falls below",
     r"BIM stays within 0.2 results/s of Manual at every rate.",
     r"""Early reuse pays off once the frame period drops below full retention's hold time (Fig.~\ref{fig:delivery}a). Both policies keep up at 10 and 15\Hz. At 20\Hz, where Full accepts only every other frame, BIM delivers 1.95$\times$ as many timely results. At 25--40\Hz{} the ratio is 1.31--1.50$\times$. BIM stays within 0.2 results/s of Manual at every rate.""")

span(r"\textbf{Slot hold time.} Full holds the slot",
     r"the producer waits until its next scheduled arrival.",
     r"""\textbf{Slot hold time.} Full holds the slot for about 51\ms, nearly the entire computation of the four recipients. BIM returns it after their source reads and cuts the hold to 30--34\ms{} (Fig.~\ref{fig:delivery}c). The hold is not shorter still because, although each head reads the source in its first operation, the last recipient must wait for its turn on the shared GPU before that operation runs. The shorter hold lets the next frame enter while private computation continues, which fills the idle gaps of Fig.~\ref{fig:trace}. The dip at 25\Hz{} comes from periodic admission, since after a refused frame the producer waits for its next scheduled arrival.""")

rep(r"\textbf{Receipt latency.} The additional admitted work queues behind other recipients on the GPU. At 20--40\Hz, BIM's mean latency rises by 8--11\ms{} and its per-run 95th percentile by 15--19\ms{} relative to Full (Fig.~\ref{fig:delivery}b). The delivery lead at 30\Hz{} remains stable across 100--200\ms{} deadlines, but narrows at 80\ms{} because more of this queued work arrives late (Fig.~\ref{fig:slots}c).",
    r"\textbf{Receipt latency.} The additional admitted work queues behind other recipients on the GPU. At 20--40\Hz, BIM's mean latency is 8--11\ms{} higher than Full's and its per-run 95th percentile 15--19\ms{} higher (Fig.~\ref{fig:delivery}b). The delivery lead at 30\Hz{} holds across 100--200\ms{} deadlines and narrows at 80\ms, where more of this queued work arrives late (Fig.~\ref{fig:slots}c).")

rep(r"all three policies deliver 60.0 results/s at 30\Hz{} (Fig.~\ref{fig:delivery}d).",
    r"all three policies deliver 60.0 results/s at 30\Hz{} (Fig.~\ref{fig:delivery}d). The gain therefore comes from overlapping the private suffix with the next frame.")

span(r"Double buffering can recover the delivery lost to full retention",
     r"whereas no cap allows more work to miss the deadline.",
     r"""A second slot is the usual remedy for full retention's refusals (Fig.~\ref{fig:slots}a). At 30\Hz, two-slot Full with $K{=}8$ delivers 78.1 results/s, matching one-slot BIM's 78.5, so BIM reaches the same delivery with one fewer source buffer. In this pipeline that buffer is 64\MiB{} of a device peak of roughly 5\,GiB. The second slot also makes the request cap decisive: $K{=}4$ holds every policy to 53--54 results/s, and no cap lets work miss the deadline.""")

span(r"\textbf{Queueing with two slots.} One slot paces",
     r"a looser deadline recovers the delayed delivery (Fig.~\ref{fig:slots}c).",
     r"""\textbf{Queueing with two slots.} With one slot, the hold time in Eq.~\eqref{eq:hold} paces BIM's admissions. A second slot removes that pacing and lets requests queue before the GPU can start them. Without a pipeline-wide cap, two-slot BIM delivers only 24.9 timely results/s against Full's 72.3, and another 54.1 results/s arrive correct but late. Full's longer hold still throttles its arrivals. Manual shows the same drop, and a looser deadline recovers the delayed results (Fig.~\ref{fig:slots}c).""")

rep(r"BIM still returns borrows earlier: time-averaged source storage held by outstanding borrows falls from 86.4\MiB{} under Full to 52.3\MiB{} under BIM (Fig.~\ref{fig:slots}b). The allocated pool and device peak stay unchanged because returning a borrow makes a slot reusable without deallocating it.",
    r"BIM still returns borrows sooner, so the time-averaged source storage held by outstanding borrows falls from 86.4\MiB{} under Full to 52.3\MiB{} (Fig.~\ref{fig:slots}b). The metric counts locked storage rather than allocation; returning a borrow makes a slot reusable without freeing it, so the device peak is unchanged.")

rep(r" Manual-checked supplies the hand-placed comparison in this study.", r"")
rep(r"The next study tests whether every intended recipient completes on time, using the complete-frame metric in Fig.~\ref{fig:mixed}.",
    r"This study asks whether every intended recipient finishes on time, using the complete-frame metric (Fig.~\ref{fig:mixed}).")

span(r"A separate 168-run study measures individual recipient results",
     r"against BIM's 5,078\MiB.",
     r"""A separate 168-run study counts individual recipient results. With early readers, BIM delivers 0.4--0.9 results/s more than cloning at 20, 30, and 40\Hz; cloning leads by 2.75 [2.47, 3.03] at 25\Hz, where BIM shows its admission dip. When all readers read late at 30\Hz, cloning delivers 76.4 results/s against 60.0, a paired gain of 16.39 [16.06, 16.72], but raises the mean per-run 99th-percentile latency from 68.7 to 101.1\ms{} and worsens freshness. Its sampled device peak is 5,334\MiB, against BIM's 5,078\MiB.""")

rep(r"With the execution checks held fixed, automatic boundary derivation preserves the delivery of the hand-placed version.",
    r"With the runtime and checks held fixed, deriving the boundary automatically costs nothing in delivery.")

span(r"\textbf{Future readers.} In six controlled ordered tests",
     r"carried their admitted identity and matched reference outputs.",
     r"""\textbf{Future readers.} In six controlled ordered tests, engine~A's input-consumed event completes before graph~B submits its reads. Under stream-only release, the graph's outputs matched the replacement frame in every test, because recording stream use cannot cover reads that have not been submitted~\cite{recordstream}. Under BIM and Manual, they matched the admitted frame. Under load, all 109,592 results delivered by BIM, Manual, and Full in the 144 rate and late-read runs carried their admitted identity and matched reference outputs.""")

span(r"\textbf{Boundaries under model change.} Fig.~\ref{fig:boundaries} shows",
     r"before the affected stage.",
     r"""\textbf{Boundaries under model change.} Regenerated boundaries kept every output exact. Across eight snapshots per model, three inputs, and two methods, all 96 ordered-overwrite cases (540 output tensors) matched unsplit references, and binding validation rejected all 22 attempted substitutions of plan, code, globals, model state, or input before the affected stage ran.""")

span(r"\textbf{Boundary maintenance.} We replay 16 controlled transitions",
     r"All 24 update cases then gave exact outputs.",
     r"""\textbf{Boundary maintenance.} We replay 16 controlled transitions: 14 graph edits, one batch-normalization folding, and a public ResNet-18 to ResNet-50 substitution. The runtime release point moves in 13 of them; folding keeps the head's first source read, and the two alias-chain edits only renumber operations (Fig.~\ref{fig:boundaries}). Binding checks reject all 16 outdated hand-placed plans (the model substitution is checked on the CPU), so a manual deployment waits until someone refreshes its plan. ReadSeal rebuilds the updated plans in 0.08--0.21\,s on the CPU without source-reader or boundary annotations. The mixed-recipient tests show the same pattern. After a late read was added, Manual-checked's old boundary failed its check until the boundary was moved, and all 24 update cases then gave exact outputs.""")

rep(r"ReadSeal's checks add 0.8--0.9\ms{} per invocation, mostly at acceptance and stage submission: 8\% over Manual for the base head (11.8\ms{} against 10.9\ms) and 22--23\% for the lighter ResNet tail. In the pipelines above, this cost overlaps shared GPU work; even at 10 and 15\Hz, BIM's mean receipt latency is within 0.4\ms{} of Manual's. A static survey of 14 torchvision tails with untrained weights accepts nine,",
    r"ReadSeal's checks add 0.8--0.9\ms{} per invocation, mostly at acceptance and stage submission. That is 8\% over Manual for the base head (11.8\ms{} against 10.9\ms) and 22--23\% for the lighter ResNet tail. In the pipelines above the cost overlaps GPU work, and even at 10 and 15\Hz{} BIM's mean receipt latency is within 0.4\ms{} of Manual's. For coverage, a static survey of 14 torchvision tails accepts nine,")

# ------------------------------------------------------------ discussion
span(r"\textbf{Choosing a release policy.} Early reuse is useful",
     r"before its borrow can be removed.",
     r"""\textbf{Why derive the boundary?} Hand-placed boundaries delivered as much as derived ones in every campaign, so ReadSeal's value is correctness as models change. Binding checks reject a plan built for other code, weights, or inputs, but they cannot tell whether a current boundary was right to begin with, such as one placed after the ResNet tail's first operation or one that misses a late read through a view (Fig.~\ref{fig:boundaries}). ReadSeal finds these reads in the graph. It still relies on reviewed operator summaries, each native engine's input-consumed event, and declared component dependencies; in our survey, missing summaries caused all five rejections.

\textbf{Choosing a release policy.} Where each recipient's last source read falls, and how much memory is free, decide where its borrow should end. With early reads, one BIM slot matched two full-retention slots with a tuned cap and delivered about as much as per-recipient copies without their 256\MiB. With a late read, early reuse gains nothing (Fig.~\ref{fig:delivery}d), and in the mixed-recipient study copying completed 22--32 points more frames on time than BIM, at 20--25\ms{} more tail latency. With memory to spare and a tunable cap, extra slots or copies are simpler; early reuse fits the setting that motivated this work, where memory is too scarce for per-recipient copies. Early release also changes how a pool should be sized: with one slot and no cap, the hold time paced BIM's admissions so that the GPU finished every admitted result on time, whereas two slots needed a request cap.

\textbf{Portability.} BIM needs cross-process storage mapping and completion events that cover each reader's source access. ROS~2's CUDA buffer read handles~\cite{cudabackend} and NvSciStream's per-consumer packet release~\cite{nvscistream} are natural integration points. A port would create each consumer's hold before the frame is published, release it on ReadSeal's completion event, and validate the platform's ordering guarantees.

\textbf{Deployment.} The prototype runs declared topologies with single-stream stages, and a topology change requires a new plan. A crashed recipient leaves its borrow outstanding and blocks slot reuse, so recovery must confirm that the recipient's GPU work has stopped before its borrow is removed.""")

# ---------------------------------------------------------- related work
rep(r"Readers that have not yet submitted, and where to release, are left to the application.",
    r"These systems decide how a buffer is shared. When it may be reused while a subscriber has yet to read it is outside their scope.")

rep(r"and NvSciStream returns a multicast packet to its pool once every consumer has released it~\cite{nvscistream}. BIM's borrow bits implement this protocol; ReadSeal derives where the release fence goes, which these interfaces leave to the application.",
    r"and NvSciStream returns a multicast packet to its pool once every consumer has released it~\cite{nvscistream}. BIM's borrow bits follow this per-consumer protocol. ReadSeal adds the fence's position, deriving from each consumer's model where its reads end.")

rep(r"Simpson's four-slot mechanism separates concurrent reads and writes across buffers; Kopetz",
    r"Simpson's four-slot mechanism separates concurrent reads and writes across buffers, and Kopetz")
rep(r"Cyclical asynchronous buffers let readers acquire the latest complete value without blocking the writer~\cite{buttazzocab}. BIM preserves the particular frame already assigned to each recipient, including while its GPU reads are still unsubmitted. ReadSeal supplies the model-derived completion boundary for that borrow.",
    r"Cyclical asynchronous buffers let readers acquire the latest complete value without blocking the writer~\cite{buttazzocab}. BIM instead preserves the particular frame already assigned to each recipient, including while its GPU reads are unsubmitted, and ReadSeal supplies the model-derived point at which that borrow ends.")

rep(r"and Rust's non-lexical lifetimes end a borrow there~\cite{nll}; all see every use in one program, in program order. Safe memory reclamation, such as read-copy-update (RCU) grace periods~\cite{rcu}, reuses",
    r"and Rust's non-lexical lifetimes end a borrow there~\cite{nll}; both see every use in one program, in program order, whereas BIM's recipients are separate processes that announce nothing to the producer. Safe memory reclamation, such as read-copy-update (RCU) grace periods~\cite{rcu}, reuses")

# ------------------------------------------------------------ conclusion
span(r"BIM lets shared GPU storage serve the next frame while results",
     r"selective copying for late readers.",
     r"""When several processes read one GPU buffer, the producer can overwrite it as soon as the last read completes, often long before the last result is ready, provided it knows which readers are still to come and where each one stops reading. BIM registers every recipient when a frame is published, and ReadSeal derives each reader's last source read from its model graph and refuses to run a plan that no longer matches execution. In our A100 pipeline, where the detection head reads the shared map only in its first operation, one slot released this way delivered 1.31--1.50$\times$ the timely results of one-slot full retention at 25--40\Hz{} and, at 30\Hz, matched two full-retention slots with a tuned request cap, at 8--11\ms{} more mean latency. Derived boundaries delivered as much as hand-placed ones and followed every model edit we replayed. When the last read falls late, per-recipient copies are the better choice if memory allows. Early reads may be common: all nine torchvision tails that ReadSeal accepted stop reading their input within 12 operations. Next, we will integrate BIM with ROS~2's CUDA buffer backend and NvSciStream, measure the checks on embedded CPU cores, support recipients that run concurrently, and copy selectively for late readers.""")

# ------------------------------------------------ optional acknowledgment
rep(r"OpenAI Codex assisted with language editing, readability revisions, figure-label updates, evidence cross-checking, and build verification for this revision. Experimental data and figure values are unchanged.",
    r"OpenAI Codex and Anthropic's Claude were used to edit and restructure the text throughout the paper, update figure labels, and cross-check reported numbers against the experimental records. The experiments, data, and figure content are the authors' own.")


# ---- line-fitting trims (remove a duplicate example and a few words where a paragraph ends in a near-empty line)
rep(r"extend its reads, and one model edit can move this \emph{read boundary} from the first operation to the second-to-last (Fig.~\ref{fig:boundaries}).",
    r"extend its reads, so the \emph{read boundary} can lie far from where the source is named (Fig.~\ref{fig:boundaries}).")
rep(r"Our clone-on-accept policy uses the same recipient registration as BIM and ends each borrow at copy completion, with extra storage for the copies.",
    r"Our clone-on-accept policy uses BIM's recipient registration and ends each borrow at copy completion.")
rep(r"A CUDA event after the prefix then marks completion of all its source reads.",
    r"A CUDA event after the prefix then marks the end of its source reads.")
rep(r"The second slot also makes the request cap decisive:",
    r"The second slot also makes the cap decisive:")
rep(r"ReadSeal finds these reads in the graph.",
    r"ReadSeal finds both in the graph.")
rep(r"When it may be reused while a subscriber has yet to read it is outside their scope.",
    r"When it may be reused while a subscriber has yet to read it is left open.")
rep(r"For coverage, a static survey of 14 torchvision tails accepts nine,",
    r"A static survey of 14 torchvision tails accepts nine,")

# ---- fill the remaining space with content that sharpens the story
rep(r"Derived boundaries deliver as much as hand-placed ones and follow model changes automatically.",
    r"Derived boundaries deliver as much as hand-placed ones and follow model changes automatically. When the last read comes late, per-recipient copies are the better choice if memory allows.")
rep(r"both see every use in one program, in program order, whereas BIM's recipients are separate processes that announce nothing to the producer.",
    r"both see every use in one program, in program order. Task runtimes such as Legion and StarPU know future accesses because tasks declare the data they touch when they are submitted~\cite{legion,starpu}. BIM's recipients are separate processes that declare nothing to the producer.")

# ---- second line-fitting pass
rep(r"Deriving the boundary matters because a hand-placed one can go stale or be misplaced from the start.",
    r"Deriving the boundary matters because a hand-placed one can go stale or be wrong from the start.")
rep(r"And while the first operation is the right boundary for the head, in a ResNet-18 tail",
    r"While the first operation is right for the head, in a ResNet-18 tail")
rep(r"have finished accessing the source. This includes readers still waiting to submit work.",
    r"have finished reading the source, including readers still waiting to submit work.")
rep(r"here through PyTorch's CUDA IPC tensor-sharing support~\cite{torchmp}.",
    r"here through PyTorch's CUDA IPC support~\cite{torchmp}.")
rep(r"and proceeds only if $\hat T=T$ (Algorithm~\ref{alg:readseal}).",
    r"and proceeds only if $\hat T=T$.")
rep(r"At 20\Hz, where Full accepts only every other frame, BIM delivers 1.95$\times$ as many timely results. At 25--40\Hz{} the ratio is 1.31--1.50$\times$.",
    r"At 20\Hz, where Full accepts only every other frame, the ratio of timely results is 1.95$\times$; at 25--40\Hz{} it is 1.31--1.50$\times$.")
rep(r"The gain therefore comes from overlapping",
    r"The gain comes from overlapping")
rep(r"It still relies on reviewed operator summaries, each native engine's input-consumed event, and declared component dependencies; in our survey, missing summaries caused all five rejections.",
    r"It still relies on reviewed operator summaries, native input-consumed events, and declared component dependencies; missing summaries caused all five survey rejections.")
rep(r"because tasks declare the data they touch when they are submitted~\cite{legion,starpu}.",
    r"because tasks declare their data when submitted~\cite{legion,starpu}.")

# ---- final wording polish
rep(r"so the \emph{read boundary} can lie far from where the source is named (Fig.~\ref{fig:boundaries}).",
    r"so the \emph{read boundary} can come long after the source itself last appears (Fig.~\ref{fig:boundaries}).")
rep(r"These systems decide how a buffer is shared. When it may be reused while a subscriber has yet to read it is left open.",
    r"These systems decide how a buffer is shared but leave open when it may be reused while a subscriber has yet to read it.")
rep("\\IEEEtriggeratref{6}\n",
    "% Both columns of the last page fill without \\IEEEtriggeratref.\n")

# ---- keep eight pages when the optional acknowledgment is enabled: the Legion/StarPU sentence yields its space
rep(r"Task runtimes such as Legion and StarPU know future accesses because tasks declare their data when submitted~\cite{legion,starpu}. BIM's",
    "% Dropped automatically when the acknowledgment is enabled, so the paper stays within eight pages.\n\\ifaidisclosure\\else Task runtimes such as Legion and StarPU know future accesses because tasks declare their data when submitted~\\cite{legion,starpu}. \\fi\nBIM's")

path.write_text(tex, encoding="utf-8")
print("all edits applied")
