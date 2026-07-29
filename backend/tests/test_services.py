"""Minimal but real tests — run with: pytest tests/ -v"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app
from app.data.disease_db import REFERENCE_SEQUENCE
from app.services import molecule_lab_service

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_disease_scan_detects_sca_mutation():
    seq = list(REFERENCE_SEQUENCE)
    seq[6] = "T"  # sickle cell mutant base
    r = client.post("/api/disease/scan", json={"sequence": seq})
    matches = [d["id"] for d in r.json() if d["match"]]
    assert "sca" in matches


def test_hdr_repair_restores_normal_base():
    seq = list(REFERENCE_SEQUENCE)
    seq[6] = "T"
    r = client.post("/api/genome/repair", json={
        "sequence": seq, "pos": 6, "normal": "A", "mutant": "T", "strategy": "hdr"
    })
    assert r.json()["sequence"][6] == "A"


def test_drug_ranking_returns_all_compounds():
    r = client.post("/api/drug/rank", json={"target_gene": "HBB"})
    data = r.json()
    assert len(data) == 8
    assert all("affinity_score" in c for c in data)


def test_molecule_lab_builds_valid_molecule():
    r = client.post("/api/molecule/build", json={
        "atoms": ["C", "C", "O"], "bonds": [[0, 1, 1], [1, 2, 1]], "name": "ethanol-test"
    })
    assert r.status_code == 200
    assert r.json()["formula"] == "C2H6O"


def test_molecule_lab_rejects_invalid_valence():
    r = client.post("/api/molecule/build", json={
        "atoms": ["C", "N", "N", "N", "N", "N"],
        "bonds": [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [0, 5, 1]],
    })
    assert r.status_code == 400


def test_ledger_chain_integrity():
    client.post("/api/ledger/append", json={"action": "a", "data": {}})
    client.post("/api/ledger/append", json={"action": "b", "data": {}})
    r = client.get("/api/ledger/verify")
    assert r.json()["ok"] is True


def test_survival_simulation_shape():
    r = client.post("/api/survival/simulate", json={"efficacy": 0.3, "n_per_arm": 10, "seed": 1})
    data = r.json()
    assert "log_rank_p" in data
    assert 0 <= data["log_rank_p"] <= 1


def test_hedera_not_configured_by_default():
    r = client.get("/api/hedera/status")
    assert r.json()["configured"] is False


def test_vision_summary_template_fallback():
    r = client.post("/api/vision/summarize", json={
        "detections": [{"label": "person", "confidence": 0.9}, {"label": "laptop", "confidence": 0.7}]
    })
    data = r.json()
    assert data["source"] == "template"
    assert "person" in data["summary"]
