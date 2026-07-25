#!/usr/bin/env python3
"""
generate_synthetic_data.py
---------------------------
Generates the synthetic dataset used by CRISPR-X (compound descriptors via
real RDKit chemistry, plus a synthetic patient cohort) and writes it as a
single JSON object to stdout.

Meant to be piped straight into inject_data.py:

    python3 generate_synthetic_data.py | python3 inject_data.py crispr-x.html > crispr-x-generated.html

Nothing here is real patient or compound data — SMILES are hand-built valid
molecules (not existing approved drugs), and the cohort is randomly
generated with a fixed seed for reproducibility.
"""
import json
import random
import sys
import argparse

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski


# Fictional candidate molecules (not real approved drugs), same set used
# throughout the app, tagged to the genes in the app's disease table.
COMPOUND_SMILES = {
    "Voxelamine":   {"smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)NCCN",                      "tags": ["HBB", "CFTR"]},
    "Fentrostat":   {"smiles": "COc1ccc(cc1)CCNC(=O)c1ccc(Cl)cc1OC",                 "tags": ["CFTR"]},
    "Kerabinol":    {"smiles": "OCC1OC(O)C(O)C(O)C1O",                              "tags": ["HBB"]},
    "Ondaprexil":   {"smiles": "CC1=NN(C(=O)C1)c1ccc(cc1)S(=O)(=O)N1CCCCC1",         "tags": ["BRCA1"]},
    "Nucleoflavin": {"smiles": "Cc1cc2nc3c(nc(=O)[nH]c3=O)n(CC(O)C(O)C(O)CO)c2cc1C", "tags": ["HTT", "BRCA1"]},
    "Thiazolamex":  {"smiles": "Cc1nc(cs1)C(=O)Nc1ccc(cc1)S(N)(=O)=O",               "tags": ["G6PD"]},
    "Corvexanide":  {"smiles": "CCN(CC)CCNC(=O)c1ccc(cc1)Nc1ncccn1",                 "tags": ["CFTR", "HBB"]},
    "Plicatannin":  {"smiles": "Oc1ccc(cc1)C1Oc2cc(O)cc(O)c2C(=O)C1O",               "tags": ["BRCA1", "HTT"]},
}

FIRST_NAMES_UNUSED = None  # cohort is anonymous by design — no names, only synthetic IDs


def compute_compounds():
    compounds = []
    for name, info in COMPOUND_SMILES.items():
        mol = Chem.MolFromSmiles(info["smiles"])
        if mol is None:
            raise ValueError(f"Invalid SMILES for {name}")
        compounds.append({
            "name": name,
            "smiles": info["smiles"],
            "mw": round(Descriptors.MolWt(mol), 1),
            "logp": round(Descriptors.MolLogP(mol), 2),
            "hbd": Lipinski.NumHDonors(mol),
            "hba": Lipinski.NumHAcceptors(mol),
            "tpsa": round(Descriptors.TPSA(mol), 1),
            "rotb": Descriptors.NumRotatableBonds(mol),
            "tags": info["tags"],
        })
    return compounds


def generate_cohort(rng, n, phase_dose_label):
    cohort = []
    for i in range(1, n + 1):
        cohort.append({
            "id": f"PT-{i:03d}",
            "age": rng.randint(22, 66),
            "sex": rng.choice(["F", "M"]),
            "consented": rng.random() > 0.15,
            "dose": phase_dose_label,
            "ae": [],
        })
    return cohort


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducible synthetic data")
    parser.add_argument("--cohort-size", type=int, default=6, help="number of synthetic patients to pre-generate")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    payload = {
        "meta": {
            "generator": "generate_synthetic_data.py",
            "seed": args.seed,
            "note": "Synthetic data only — no real patients, no real approved compounds.",
        },
        "compounds": compute_compounds(),
        "cohort": generate_cohort(rng, args.cohort_size, "Single ascending dose"),
    }

    json.dump(payload, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
