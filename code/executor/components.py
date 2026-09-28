"""Different real component workloads; identical profile within each policy pair."""
import torch
from batch_backend import BatchProgram
from common import Join, now
from copyin_composition import CopyInInvocation
from core import Rejected
from manual_checked import from_pinned_export
from manual_static import ManualProgram
from native_loader import FrozenNative
from study_common import MODELS, ROOT


class ComponentProgram:
    def __init__(self, example, profile, method):
        if profile not in ("native", "head", "composed", "composed-late"):
            raise Rejected("unknown consumer profile")
        if method not in ("auto-batched", "manual-checked", "manual-full", "copy-in"):
            raise Rejected("unknown policy")
        self.profile, self.method = profile, method
        self.full = method == "manual-full"
        self.late = profile == "composed-late"
        if method == "copy-in":
            self.private_program = ComponentProgram(example, profile, "manual-full")
            self.artifact = dict(schema="reviewer-copyin-v1", profile=profile,
                                 private_compute=self.private_program.artifact,
                                 copy_bytes=example.numel()*example.element_size())
            return
        self.native = None if profile == "head" else FrozenNative(
            ROOT / "results/borrowplan_v2_native_composition_attempt1")
        self.child = None
        if profile != "native":
            path = MODELS["transfusion"][0]
            if method == "manual-checked":
                self.child = from_pinned_export(path, example, self.late)
            elif method == "auto-batched":
                self.child = BatchProgram(torch.export.load(path), example, self.late)
            else:
                self.child = ManualProgram(path, example, "transfusion", self.late, full=True)
        self.artifact = dict(schema="reviewer-component-v1", profile=profile, method=method,
                             native=None if self.native is None else self.native.receipt,
                             child=None if self.child is None else self.child.artifact,
                             outer_join="same explicit complete enrollment for all policies",
                             scope="component heterogeneity, not independently trained AV nodes")

    def start(self, x, publication, ready):
        if self.method == "copy-in":
            return CopyInInvocation(self, x, dict(publication), ready)
        return ComponentInvocation(self, x, publication, ready)


class ComponentInvocation:
    def __init__(self, program, x, publication, ready):
        self.program, self.x, self.publication, self.ready = program, x, dict(publication), ready
        self.stage, self.published = 0, False
        self.events, self.child, self.native = [], None, None
        self.trace = dict(enrolled_ns=now(), profile=program.profile)

    def submit(self, stage, stream):
        p = self.program
        if stage != self.stage or self.published or stage > (0 if p.full else 1):
            raise Rejected("invalid component stage")
        if stage == 0:
            self.stream = stream
            if p.native is not None:
                self.native = p.native.launch(self.x, self.ready)
            if p.child is not None:
                self.child = p.child.start(self.x, self.publication, self.ready)
                self.child.submit(0, stream)
            reads = []
            if self.native is not None:
                reads.append(self.native.output_done if p.full else self.native.read_done)
            if self.child is not None:
                reads.append(self.child.events[0])
            self.events.append(Join(reads))
            self.x = None
        else:
            if stream.cuda_stream != self.stream.cuda_stream:
                raise Rejected("stream changed")
            if self.child is not None:
                self.child.submit(1, stream)
            outputs = []
            if self.native is not None:
                outputs.append(self.native.output_done)
            if self.child is not None:
                outputs.append(self.child.events[-1])
            self.events.append(Join(outputs))
        self.stage += 1
        return self.events[-1]

    def can_release(self):
        if not self.events or not self.events[0].query():
            return False
        if self.child is None:
            return True
        if self.program.full:
            return self.child.can_release()
        return self.child.lease.can_release(self.child.lease.bindings[self.program.child.root].allocation)

    def publish(self):
        if self.published or self.stage != (1 if self.program.full else 2) or not self.events[-1].query():
            raise Rejected("incomplete or duplicate component output")
        result = () if self.native is None else (self.native.output,)
        if self.child is not None:
            if self.program.full:
                values, identity = self.child.publish()
                if identity != self.publication:
                    raise Rejected("manual output identity mismatch")
            else:
                values = self.child.outputs()
                identities = self.child.lease.publish_identity()
                versions = {b.version for group in identities.values() for b in group.values()}
                expected = tuple(self.publication[k] for k in ("epoch", "sequence", "generation"))
                if versions != {expected}:
                    raise Rejected("checked output identity mismatch")
            result += tuple(values)
        self.published = True
        return result, dict(self.publication)
