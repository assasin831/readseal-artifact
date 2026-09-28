"""Manual boundary with the EXACT BatchProgram admission and stage guards.

Construction consumes a reviewed boundary, never an automatic alias plan.
The generic two-node certificate binds these explicitly asserted stages.
This is a shared-check ablation, not an independently implemented runtime.
"""
import hashlib
import json
import marshal

import torch
from batch_backend import BatchProgram
from batch_lease import prepare_groups
from core import Node, Rejected, Summary, compile_plan, digest
from manual_static import BASE_BOUNDARY, EXPORTS, fixed_graph, manual_partition, sha
from owned_backend import Capsule, capture, records, state_token
from prepared_lease import prepare
from torch_backend import spec


class ManualCheckedProgram(BatchProgram):
    __slots__ = ()

    def __init__(self, exported, example, late_read=False, boundary=None):
        if torch.__version__ != "2.1.2+cu121":
            raise Rejected("unreviewed PyTorch implementation")
        graph, root, state, changed_boundary = fixed_graph(exported, example.device, late_read)
        ref = next(n for n in graph.nodes if n.name == root).meta["val"]
        if (tuple(ref.shape), tuple(ref.stride()), ref.dtype, ref.storage_offset()) != (
                tuple(example.shape), tuple(example.stride()), example.dtype, example.storage_offset()):
            raise Rejected("input outside fixed graph metadata")
        stop = boundary or (changed_boundary if late_read else BASE_BOUNDARY["transfusion"])
        graphs, carry = manual_partition(graph, stop)
        # An explicit boundary must not carry the shared input itself into the suffix.
        # Indirect aliases remain covered by the unchanged dynamic stage guard.
        if root in carry:
            raise Rejected("manual boundary carries source; a new safety review is required")
        modules = tuple(torch.fx.GraphModule(torch.nn.Module(), g) for g in graphs)
        functions = tuple(capture(module) for module in modules)
        owned = tuple(state.items())
        identity = digest(dict(graph=records(graph), boundary=stop,
                               modules=[f.module_sha256 for f in functions],
                               state=[state_token(t) for _, t in owned]))
        nodes = (
            Node("prefix", (root,), Summary((0,), implementation=functions[0].module_sha256)),
            Node("suffix", ("prefix",), Summary((0,), implementation=functions[1].module_sha256)),
        )
        plan = compile_plan((root,), nodes, ("suffix",), {root: spec(example)}, identity)
        groups = (("prefix",), ("suffix",))
        artifact = dict(schema="manual-boundary-equal-checks-v1", boundary=stop,
                        manual_source_sha256=sha(__file__), graph=records(graph), carry=carry,
                        boundary_source="explicit reviewed node, no auto alias analysis",
                        guard_implementation="BatchProgram.start/guard and BatchExecution.submit unchanged",
                        shared_runtime=True, independent_runtime=False,
                        modules=[dict(code=m.code, sha256=f.module_sha256,
                                      code_sha256=hashlib.sha256(marshal.dumps(f.code)).hexdigest())
                                 for m, f in zip(modules, functions)])
        capsule = Capsule(root, spec(example), plan, identity, digest(artifact), owned,
                          tuple(state_token(t) for _, t in owned),
                          tuple(n.name for n in graph.nodes if n.op == "placeholder"),
                          groups, carry, functions, json.dumps(artifact, sort_keys=True))
        object.__setattr__(self, "_capsule", capsule)
        object.__setattr__(self, "_certificate", prepare(plan))
        object.__setattr__(self, "_grouping", prepare_groups(plan, groups))
        object.__setattr__(self, "_batch_artifact", json.dumps(artifact, sort_keys=True))
        object.__setattr__(self, "_batch_identity", digest(artifact))


def from_pinned_export(path, example, late=False):
    if sha(path) != EXPORTS["transfusion"]:
        raise Rejected("changed export requires fresh explicit manual review")
    return ManualCheckedProgram(torch.export.load(path), example, late)
