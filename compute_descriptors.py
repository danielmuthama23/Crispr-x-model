from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

# Fictional candidate molecules (not real approved drugs) with valid, computable structures.
compounds = {
    "Voxelamine":   "CC(C)Cc1ccc(cc1)C(C)C(=O)NCCN",
    "Fentrostat":   "COc1ccc(cc1)CCNC(=O)c1ccc(Cl)cc1OC",
    "Kerabinol":    "OCC1OC(O)C(O)C(O)C1O",
    "Ondaprexil":   "CC1=NN(C(=O)C1)c1ccc(cc1)S(=O)(=O)N1CCCCC1",
    "Nucleoflavin": "Cc1cc2nc3c(nc(=O)[nH]c3=O)n(CC(O)C(O)C(O)CO)c2cc1C",
    "Thiazolamex":  "Cc1nc(cs1)C(=O)Nc1ccc(cc1)S(N)(=O)=O",
    "Corvexanide":  "CCN(CC)CCNC(=O)c1ccc(cc1)Nc1ncccn1",
    "Plicatannin":  "Oc1ccc(cc1)C1Oc2cc(O)cc(O)c2C(=O)C1O",
}

print(f"{'Name':<14}{'MW':>8}{'LogP':>8}{'HBD':>6}{'HBA':>6}{'TPSA':>8}{'RotB':>6}  Ro5")
for name, smi in compounds.items():
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        print(f"{name}: INVALID SMILES")
        continue
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotb = Descriptors.NumRotatableBonds(mol)
    ro5 = mw<=500 and logp<=5 and hbd<=5 and hba<=10
    print(f"{name:<14}{mw:>8.1f}{logp:>8.2f}{hbd:>6}{hba:>6}{tpsa:>8.1f}{rotb:>6}  {'PASS' if ro5 else 'FAIL'}")
