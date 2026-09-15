"""Reconcile recorded ResNet graph counts without executing or unpickling models."""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_operations(path):
    function = next(n for n in ast.parse(path.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'forward')
    result = []
    for statement in function.body:
        if not isinstance(statement, ast.Assign):
            continue
        value = statement.value
        if isinstance(value, ast.Call):
            target = ast.unparse(value.func).removeprefix('torch.ops.')
        elif isinstance(value, ast.Subscript):
            target = '<built-in function getitem>'
        else:
            continue
        result.append((statement.targets[0].id, target))
    return result


def references(value):
    if isinstance(value, dict):
        if set(value) == {'node'}:
            yield value['node']
        else:
            for item in value.values():
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parents[1] / 'evidence/export_audit')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    root = args.data
    paths = {name: root / name for name in (
        'earlier_graph_code.py', 'substitution_graph_code.py',
        'earlier_report.json', 'reloaded_manual_artifact.json')}
    for name in ('earlier_graph_code.py', 'substitution_graph_code.py'):
        assert sha(paths[name]) == '0b79f0d150affbc2e23672d08cf6152b7794d91074b7f6373ff389383293a133'
    assert sha(paths['reloaded_manual_artifact.json']) == '72f4d22f2a24153942fbba8092b9d7c6d302deb4d477fe919d17135851c32b4c'
    report = json.loads(paths['earlier_report.json'].read_text())
    artifact = json.loads(paths['reloaded_manual_artifact.json'].read_text())
    assert report['files']['graph_code.py'] == sha(paths['earlier_graph_code.py'])
    assert report['files']['resnet_tail.pt2'] == artifact['review']['export_sha256']
    assert artifact['edit'] == 'base' and artifact['boundary'] == 'add'
    original = code_operations(paths['earlier_graph_code.py'])
    calls = [node for node in artifact['graph'] if node[0] == 'call_function']
    added = [n for n in calls if '_unused_' in n[1]]
    assert len(original) == 85 and len(calls) == 123 and len(added) == 38
    nodes = {n[1]: n for n in artifact['graph']}
    uses = Counter(r for n in artifact['graph'] for r in references(n[3:]))
    for node in added:
        assert node[2] == '<built-in function getitem>'
        assert node[3][1] in (1, 2) and uses[node[1]] == 0
        parent = nodes[node[3][0]['node']]
        assert parent[2] == 'aten._native_batch_norm_legit_no_training.default'
    assert Counter(n[3][1] for n in added) == {1: 19, 2: 19}
    filtered = [n for n in calls if n not in added]
    assert [n[2] for n in filtered] == [target for _, target in original]
    in_memory_prefix = next(i + 1 for i, n in enumerate(original) if n[0] == 'add')
    reloaded_prefix = next(i + 1 for i, n in enumerate(calls) if n[1] == 'add')
    assert (in_memory_prefix, reloaded_prefix) == (8, 12)
    assert len([n for n in artifact['stages'][0] if n[0] == 'call_function']) == 12
    result = {
        'status': 'COMPLETE', 'model_execution': False, 'gpu_used': False,
        'inputs': {name: sha(path) for name, path in paths.items()},
        'validator_sha256': sha(Path(__file__)),
        'same_in_memory_graph_text': True,
        'same_export_hash_in_original_report_and_reloaded_review': True,
        'in_memory': {'prefix': 8, 'total': 85, 'boundary': 'add'},
        'reloaded': {'prefix': 12, 'total': 123, 'boundary': 'add'},
        'additional_unused_tuple_indices': 38, 'batchnorm_sites': 19,
        'remaining_operator_order_matches': True,
        'scope': 'Recorded graph structure and provenance only; not a new numerical or CUDA test.',
    }
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
