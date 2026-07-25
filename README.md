# CRISPR-X — Genome Engineering Lab

## What's in this package
- `crispr-x.html` — the full interactive app, **already built by the pipeline below**.
  Open it directly in any modern browser (double-click, or drag into a browser
  window). No server or install needed.
- `generate_synthetic_data.py` — generates the synthetic dataset (compound
  descriptors via real RDKit chemistry, plus a synthetic patient cohort) and
  prints it as JSON to stdout.
- `inject_data.py` — reads that JSON from stdin and splices it directly into
  `crispr-x.html`'s JS data blocks (`COMPOUND_DB`, initial `cohort`), replacing
  the hand-typed values.
- `compute_descriptors.py` — standalone RDKit descriptor script, useful if you
  just want the numbers without rebuilding the HTML.

## Rebuild the app from fresh synthetic data
This is a real Unix pipe — no manual copy/pasting of numbers into the JS:

```bash
pip install rdkit --break-system-packages
python3 generate_synthetic_data.py --seed 42 --cohort-size 6 \
  | python3 inject_data.py crispr-x.html > crispr-x-generated.html
```

Change `--seed` for a different random cohort, or `--cohort-size` for more
starting patients. The resulting HTML has a comment near the top of its
`<script>` block recording exactly which generator and seed produced it.

## What's real vs. simplified
The app runs entirely client-side in the browser — no external AI model,
genome database, EHR system, or live blockchain network is called. See the
"What's real vs. simplified here" panel inside the app for the full,
honest accounting of every feature. In short: the computations are genuine
(SHA-256 hashing, TF-IDF search, RDKit chemistry, Kaplan-Meier statistics,
a real YOLOv8 vision model), but they run on synthetic/illustrative data —
this is an educational demo, not a clinical, wet-lab, or production system.
The compound SMILES are hand-built valid molecules, not existing approved
drugs; the cohort is randomly generated with no real patients or PII.

## Extending it for real
- **Hedera integration**: the audit ledger simulates a hash chain locally.
  To connect it to a real Hedera testnet/mainnet, use the Hedera SDK
  server-side with your own account ID and private key.
- **Real docking/drug discovery**: swap the stylized pocket scoring for
  AutoDock Vina or DiffDock against real PDB structures.
- **Real genomics**: replace the mock disease table with a live ClinVar/
  gnomAD/Ensembl lookup.
