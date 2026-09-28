"""Pinned remote dependency paths; importing this module does not import CUDA."""
import hashlib
import os
from pathlib import Path
import sys

ROOT = Path('/www/readseal_ipdps_revision_v6')
HERE = Path(__file__).resolve().parent
GPU = 'GPU-f3b314a8-3058-e0be-694c-76f4227afb7d'
BASE = ROOT / 'results/ispa_reviewer_execution_20260927_attempt2'
PYTHON = '/www/bim/venv/bin/python'
DEPS = [HERE] + [ROOT / p for p in (
    'prototype_ispa_copyin_20260923_attempt2',
    'prototype_borrowplan_v11_grouped_attempt1',
    'prototype_borrowplan_v10_maintenance_attempt1',
    'prototype_borrowplan_v10_admission_attempt1', 'prototype_borrowplan_v8_abc_attempt1',
    'prototype_borrowplan_v10_batch_attempt1', 'prototype_borrowplan_v7_followups_attempt1',
    'prototype_borrowplan_v7_formal_attempt1', 'prototype_borrowplan_v6_resnet_scope_attempt1',
    'prototype_borrowplan_v6_witness_attempt1', 'prototype_borrowplan_v5_prepared_attempt1',
    'prototype_borrowplan_v5_owned_attempt2', 'prototype_borrowplan_v4_segmented_attempt1',
    'prototype_borrowplan_v1_attempt2', 'prototype_borrowplan_v2_composition_attempt2',
    'prototype_borrowplan_v3_attempt1', 'sdk_trt_10_3_attempt2/packages', 'experiments')]


def activate():
    sys.path[:0] = [str(p) for p in DEPS if str(p) not in sys.path]


def environment(cuda=False):
    return dict(os.environ, PYTHONPATH=':'.join(map(str, DEPS)),
                CUDA_VISIBLE_DEVICES=GPU if cuda else '', PYTHONDONTWRITEBYTECODE='1',
                OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()
