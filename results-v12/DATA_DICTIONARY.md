# V12 Data Dictionary

## E1/E2 Counts and Units
- One source publication can be offered to four recipients. Each delivered recipient bundle contains the required composition outputs. Counts are not numbers of individual tensors.
- `rate_hz` is the planned source-publication rate. Offered recipient-bundle rate is four times this value.
- `arrivals` counts measured planned recipient offers, including rejected offers.
- `publications` in the inherited schema counts delivered recipient bundles, NOT accepted source publications.
- `timely` counts delivered, source-verified, reference-matching bundles received by the 100 ms deadline.
- `correct_late` counts valid delivered bundles received after the deadline. It is distinct from wrong output and unknown source.
- `producer_late`, `pool_exhausted`, `credit_exhausted` are rejected recipient offers. A producer-level rejection contributes four offers. `queue_loss` counts individual failed recipient enqueues.
- Counts reconcile as arrivals = publications + rejected offers + queue_loss, and publications = timely + correct_late.
- `goodput_hz` = timely / 12 seconds in formal runs; smoke uses its separately frozen shorter duration.
- `cap=0` disables the additional outstanding-credit bound; the finite ring and recipient queues still exist. It does not mean an infinite system queue.

## Time and Storage
- `publish_ns` records sink receipt immediately after Queue.get returns. It includes output copying and IPC before receipt. Source/output correctness is checked after that timestamp. Oracle hashing time is not added to the receipt deadline.
- Timeline CSVs use milliseconds relative to measured-cohort start. Negative timestamps are warm-up. `cohort` is defined by the planned arrival, not completion time. All admitted work is drained.
- `source_hold_mean_ms` is commit_end to the last recipient release_end for measured accepted source publications with receipts. Producer reservation/write time before commit is excluded. This conditional mean is not load-independent service time.
- `read_done_ns` is a host timestamp after the method's first completion event is synchronized. Full retention's first event covers full computation; it is not an independently measured physical last-shared-load timestamp for that method.
- `private_after_read_mean_ms` is output_done minus this policy-specific read_done timestamp. It is a host-observed interval, not isolated GPU kernel time. Across-method subtraction must respect that distinction.
- `planned_to_admit_mean_ms` includes upstream waiting before admitted execution. `execution_mean_ms` is admission to observed output completion, not pure GPU kernel time.
- `receipt_p95_ms_mean` is the mean of six within-run 95th percentiles, not the 95th percentile of pooled requests.
- `protected_byte_seconds` integrates the union of logical protected intervals per slot (commit_begin to final return), clipped to the measured window.
- `mean_protected_mib` divides that integral by window seconds and 2^20. `protected_interval_fraction_mean` additionally divides by ring capacity in source bytes. The local audit's shorter field name `occupied_fraction` denotes this same protected-interval fraction, not total slot-busy time, GPU utilization or allocated-memory utilization.
- `device_peak_mib` is the inherited measured device-memory peak. Reduced logical borrowing does not imply allocator deallocation or a reduced peak.

## Statistics
- Each condition/method has six whole-run repetitions. Paired differences align repeat IDs. There are 20,000 bootstrap draws of six paired runs.
- Intervals are pointwise 95% percentile intervals, not simultaneous bands, capacity bounds, or equivalence tests. A zero-width interval means the six observed values coincided, not that all deployment uncertainty is zero.
- E1 and E2 are separate measurement windows. Their overlapping base/30 Hz conditions are not pooled. Earlier V11 windows remain separate.

## E3/E4/E6
- E3 `manual_edit_count` counts changed review fields, not human edits, lines of code or elapsed labor. Runtime-used fields exclude the documentary readers list. Binding hashes may be regenerated mechanically.
- E3 `readseal_edits=0` refers only to manual source-reader/boundary annotations supplied to these constructors, not all integration work.
- E3 times are CPU constructor medians after one warm-up and 12 measured calls. Tracing/export, disk reads, deserialization, execution and GPU copies are excluded.
- E4 normal phases and inclusive cProfile counters are separate tables. Nested/inclusive counters are not additive. Missing enrollment instrumentation is blank with an explanatory note, not a zero-cost estimate.
- E6 `supported=True` means CPU export, unchanged-registry checks, analysis and lowering passed for the declared tail/interface with weights=None. No numerical-equivalence, GPU, accuracy or production-support inference follows. Unsupported operators are recorded explicitly.
- CSV blanks mean unavailable or inapplicable, never an implied zero. JSON carries explicit booleans, nulls, frozen parameters and lineage.
