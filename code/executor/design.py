"""Fixed reviewer follow-up matrix. No CUDA import or outcome-driven selection."""
import hashlib
import json
import random


METHODS = ("auto-batched", "manual-checked", "manual-full", "copy-in")
PROFILES = {
    "homogeneous": ("composed",) * 4,
    "heterogeneous": ("native", "head", "composed", "composed-late"),
    "late": ("composed-late",) * 4,
}
CONDITIONS = tuple(
    dict(id=f"{mix}-{arrival}-hz30", mix=mix, arrival=arrival, rate_hz=30)
    for mix in ("homogeneous", "heterogeneous")
    for arrival in ("periodic", "jitter")
) + (dict(id="late-periodic-hz30", mix="late", arrival="periodic", rate_hz=30),)
PLAN = dict(
    schema="readseal-reviewer-followup-v1", repetitions=6,
    methods=METHODS, conditions=CONDITIONS, profiles=PROFILES,
    common=dict(consumers=4, ring=1, queue=8, outstanding_cap=0,
                deadline_ms=100, warmup_seconds=10, measure_seconds=30),
    expected_runs=dict(smoke=18, formal=108),
    jitter="independent nonnegative U[0,0.8*period] arrival displacement; no sorting or clipping",
    seeds=dict(order=26092701, arrivals=26092702),
    initial_free_gib_floor=40, between_run_free_gib=20,
    disk_rule="initial max(40 GiB, 20 GiB + 2*estimated whole-campaign raw bytes)",
    gpu_uuid="GPU-f3b314a8-3058-e0be-694c-76f4227afb7d",
    primary="all four intended recipients exact and received within 100ms / all scheduled publications",
    secondary=("complete-publication timely goodput/s", "recipient timely bundles/s",
               "complete-publication scheduled-to-last-receipt P50/P99",
               "all-correct complete count", "partial count", "producer and queue drops",
               "per-recipient latency and timely fractions", "sampled device and allocator peaks"),
    confidence="n=6 whole-run paired, pointwise t95 df=5; no equivalence or multiplicity guarantee",
    scope="native A100 component heterogeneity, not heterogeneous AV nodes or embedded execution",
    no_retry=True, no_condition_selection=True,
)


def schedule(phase):
    if phase not in ("smoke", "formal"):
        raise ValueError("invalid phase")
    rng = random.Random(PLAN["seeds"]["order"] + (phase == "formal"))
    rows = []
    for repeat in range(1 if phase == "smoke" else 6):
        conditions = list(CONDITIONS)
        rng.shuffle(conditions)
        for condition in conditions:
            methods = list(METHODS if condition["mix"] != "late"
                           else ("auto-batched", "manual-checked"))
            rng.shuffle(methods)
            for method in methods:
                cell = dict(PLAN["common"], **condition,
                            arrival_seed=PLAN["seeds"]["arrivals"] + repeat,
                            profiles=PROFILES[condition["mix"]])
                if phase == "smoke":
                    cell.update(warmup_seconds=1, measure_seconds=3)
                rows.append(dict(name=f"{phase}-r{repeat:02d}-{condition['id']}-{method}",
                                 repeat=repeat, condition=condition["id"], method=method, cell=cell))
    assert len(rows) == PLAN["expected_runs"][phase]
    return rows


def arrivals(cell):
    """Integer offsets shared by every method, generated before any inference."""
    rng = random.Random(cell["arrival_seed"])
    period = 1e9 / cell["rate_hz"]
    finish = round((cell["warmup_seconds"] + cell["measure_seconds"]) * 1e9)
    finish += round(cell["deadline_ms"] * 1e6)
    if cell["arrival"] not in ("periodic", "jitter"):
        raise ValueError("unknown arrival policy")
    offsets = []
    tick = 0
    while True:
        extra = rng.uniform(0, 0.8 * period) if cell["arrival"] == "jitter" else 0
        offset = round(tick * period + extra)
        if offset >= finish:
            break
        offsets.append(offset)
        tick += 1
    assert all(a < b for a, b in zip(offsets, offsets[1:]))
    return offsets


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()
