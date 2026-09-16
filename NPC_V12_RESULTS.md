# NPC V12 experimental results

This evidence-only update preserves the exact author-provided results archive.
It does not publish a new paper PDF, LaTeX source package, or later figure draft.
Older archives and version tags remain unchanged.

## Download and identity

- [Results ZIP](./readseal_npc_v12_results_20260915.zip)
- Frozen version: `npc-results-v12`
- Bytes: 13,722,193
- Files inside: 104
- ZIP SHA-256: `d775f1b5be0eace0b4a338dd3b5c4fa116085f22fefacd600b31fccd39f8d47c`

The following browsable documents are byte-identical copies from the archive:

- [Verified results for writing](./results-v12/RESULTS_FOR_WRITING.md)
- [Data dictionary](./results-v12/DATA_DICTIONARY.md)
- [Recorded package validation](./results-v12/PACKAGE_VALIDATION.json)
- [Internal checksum inventory](./results-v12/SHA256SUMS.txt)

## Contents and boundaries

| Part | Included evidence | Scope |
| --- | --- | --- |
| E1 | 108 formal one-slot rate-sweep runs | Six paired repetitions, three methods, six source rates |
| E2 | 36 formal base/late-read runs | A separate window; not pooled with E1 |
| Smoke | Six smoke runs | Excluded from formal estimates |
| E3 | 16 transitions and 20 constructor timing snapshots | Review-field changes and CPU constructor cost, not observed developer labor |
| E4 | Four diagnostic profile processes | Normal host phases and inclusive profiles remain separate |
| E5 | Explicit not-run record | The frozen full-pipeline factory does not support the requested ResNet experiment |
| E6 | 14 predeclared model-tail static checks | Nine supported static cases and five unsupported-operator cases; not GPU correctness or performance tests |
| E7 | Dated host/environment record | Applies to this window, not retroactive provenance for older experiments |
| Prior evidence | Compact V11 evidence and notes | Separate measurement windows, with original limitations retained |

New formal data account for 172,800 recipient offers, 109,592 delivered bundles,
109,569 timely bundles, 23 correct-late bundles, and 63,208 pool-exhausted offers.
Source publication rate is distinct from recipient-bundle rate. Statistical
intervals use 20,000 whole-run paired bootstrap draws and are pointwise.

The archive also retains failed analysis attempts with their explanations.
It identifies a separately distributed full raw archive; it does not contain
those complete raw blobs, model weights, or a turnkey GPU environment. Absolute
deployment paths in provenance records may need adaptation on another machine.
No inference was launched for this repository upload.

## Verify the download

After extracting into a fresh directory, run this standard-library Python check
from the directory containing `SHA256SUMS.txt`:

```python
from pathlib import Path
import hashlib

root = Path.cwd()
checked = 0
for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8-sig").splitlines():
    if not line.strip():
        continue
    expected, name = line.split(maxsplit=1)
    path = (root / name.strip().lstrip("*")).resolve()
    assert path.is_relative_to(root.resolve()), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    checked += 1
assert checked == 103
print(f"Verified {checked} files")
```

Before upload, archive CRCs and all 103 inventoried files passed verification.
A content scan found no common credential-token, credential-URL, or private-key
patterns. These packaging checks are not an independent-team replication or a
guarantee that every experimental claim has been re-evaluated.
