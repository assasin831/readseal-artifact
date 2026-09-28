"""CPU-only full-publication accounting, including rejected offered load."""
import math
import statistics


def percentile(values, probability):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def evaluate(producer, receipts, consumers, begin_ns, end_ns, deadline_ms):
    if type(consumers) is not int or consumers < 1 or not begin_ns < end_ns:
        raise ValueError("invalid population/window")
    offered = {}
    for row in producer:
        tick = row["tick"]
        if tick in offered or type(tick) is not int:
            raise ValueError("duplicate/invalid producer tick")
        if len(row["enqueued"]) != consumers:
            raise ValueError("recipient enrollment length")
        if any(type(flag) is not bool for flag in row["enqueued"]):
            raise ValueError("nonboolean enrollment")
        offered[tick] = row
    indexed = {}
    for row in receipts:
        tick, cid = row["tick"], row["consumer"]
        if tick not in offered or type(cid) is not int or not 0 <= cid < consumers:
            raise ValueError("unregistered receipt")
        source = offered[tick]
        if not source["enqueued"][cid] or (tick, cid) in indexed:
            raise ValueError("receipt for rejected/duplicate recipient")
        for key in ("sequence", "source_id", "scheduled_ns"):
            if row[key] != source[key]:
                raise ValueError("receipt lineage mismatch: " + key)
        identity = row["identity"]
        if identity != dict(epoch=987654, sequence=row["sequence"], generation=2*row["sequence"]):
            raise ValueError("publication identity mismatch")
        if type(row["publish_ns"]) is not int or row["publish_ns"] < row["scheduled_ns"]:
            raise ValueError("invalid receipt clock")
        if any(type(row[k]) is not bool for k in ("output_equal", "provenance_verified", "finite")):
            raise ValueError("invalid verification flags")
        indexed[tick, cid] = row
    detail = []
    recipient_latencies = [[] for _ in range(consumers)]
    recipient_timely = [0] * consumers
    complete_latencies = []
    for tick, source in offered.items():
        if not begin_ns <= source["scheduled_ns"] < end_ns:
            continue
        rows = [indexed.get((tick, cid)) for cid in range(consumers)]
        correct = [r is not None and r["output_equal"] and r["provenance_verified"] and r["finite"]
                   for r in rows]
        timely = []
        for cid, row in enumerate(rows):
            latency = None if row is None else (row["publish_ns"]-source["scheduled_ns"])/1e6
            valid = bool(correct[cid] and latency <= deadline_ms)
            timely.append(valid)
            recipient_timely[cid] += int(valid)
            if correct[cid]:
                recipient_latencies[cid].append(latency)
        complete = all(correct)
        last_ms = max((r["publish_ns"]-source["scheduled_ns"])/1e6 for r in rows) if complete else None
        if complete:
            complete_latencies.append(last_ms)
        detail.append(dict(tick=tick, scheduled_ns=source["scheduled_ns"],
                           intended=consumers, enqueued=sum(source["enqueued"]),
                           received=sum(r is not None for r in rows), correct=sum(correct),
                           timely_recipients=sum(timely), complete_correct=complete,
                           complete_timely=all(timely), complete_latency_ms=last_ms,
                           drop_reason=source.get("drop_reason")))
    count = len(detail)
    duration = (end_ns-begin_ns)/1e9
    timely_count = sum(r["complete_timely"] for r in detail)
    complete_count = sum(r["complete_correct"] for r in detail)
    return dict(
        offered_publications=count, complete_correct=complete_count, complete_timely=timely_count,
        full_publication_timely_fraction=timely_count/count if count else None,
        full_publication_timely_goodput_hz=timely_count/duration,
        recipient_timely_goodput_hz=sum(recipient_timely)/duration,
        partial_publications=sum(0 < r["correct"] < consumers for r in detail),
        zero_correct_publications=sum(r["correct"] == 0 for r in detail),
        incomplete_publications=count-complete_count,
        full_publication_p50_ms=percentile(complete_latencies, .5),
        full_publication_p99_ms=percentile(complete_latencies, .99),
        latency_population="all-correct complete publications only; incomplete counted separately",
        recipients=[dict(consumer=i, timely=recipient_timely[i],
                         timely_fraction=recipient_timely[i]/count if count else None,
                         p50_ms=percentile(values, .5), p99_ms=percentile(values, .99))
                    for i, values in enumerate(recipient_latencies)],
        publications=detail,
    )


def t95(values):
    if len(values) != 6 or not all(math.isfinite(x) for x in values):
        raise ValueError("exactly six finite whole-run observations required")
    mean = statistics.mean(values)
    half = 2.570581835636305 * statistics.stdev(values) / math.sqrt(6)
    return dict(n=6, mean=mean, low=mean-half, high=mean+half,
                interval="pointwise t95 df5; whole-run unit; not simultaneous or equivalence")
