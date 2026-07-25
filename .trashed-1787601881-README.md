# CRISPR-X — Genome Engineering Lab

## What's in this package
- `crispr-x.html` — the full interactive app. Open it directly in any modern browser
  (double-click, or drag into a browser window). No server or install needed.
- `compute_descriptors.py` — companion script that computes real RDKit molecular
  descriptors (MW, LogP, HBD, HBA, TPSA, rotatable bonds) for the fictional
  compound set used in the app's drug-screening panel. Run with:
  `pip install rdkit --break-system-packages && python3 compute_descriptors.py`

## What's real vs. simplified
The app runs entirely client-side in your browser — no external AI model, genome
database, EHR system, or live blockchain network is called. See the
"What's real vs. simplified here" panel inside the app for the full, honest
accounting of every feature (3D viewer, CRISPR editing, disease matching, drug
descriptors, docking, chemical space, variant calling, survival simulation,
audit ledger, vision triage). In short: the computations are genuine
(SHA-256 hashing, TF-IDF search, RDKit chemistry, Kaplan-Meier statistics, a
real YOLOv8 vision model), but they run on synthetic/illustrative data — this
is an educational demo, not a clinical, wet-lab, or production system.

## Extending it for real
- **Hedera integration**: the audit ledger simulates a hash chain locally.
  To connect it to a real Hedera testnet/mainnet, use the Hedera SDK
  (`pip install hedera-sdk-py` or the JS SDK) server-side with your own
  account ID and private key — this needs real credentials this package
  doesn't include.
- **Real docking/drug discovery**: swap the stylized pocket scoring for
  AutoDock Vina or DiffDock against real PDB structures.
- **Real genomics**: replace the mock disease table with a live ClinVar/
  gnomAD/Ensembl lookup.
