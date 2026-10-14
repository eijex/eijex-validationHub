"""Tests for ComputationalEvidenceStore contracts and conflict handling."""

import tempfile
from pathlib import Path
import uuid
import pytest

from validationhub.computational_evidence import (
    ComputationalEvidenceStore,
    EvidenceConflict,
)


def test_existing_sequence_assessment_contract():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.sqlite"
        store = ComputationalEvidenceStore(db_path)
        task_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        digest = "a" * 64
        evidence = {
            "analysis_mode": "existing_sequence_assessment",
            "generation_performed": False,
            "canonical_metrics_available": False,
            "multi_constraint_pass": None,
            "gc_in_target_range": True,
            "metric_provenance": "computed_from_existing_cds_without_generation",
        }
        assessment_id = store.put(task_id, run_id, digest, evidence)
        assert assessment_id is not None

        retrieved = store.get(task_id)
        assert retrieved is not None
        assert retrieved["assessment_id"] == assessment_id
        assert retrieved["evidence"]["analysis_mode"] == "existing_sequence_assessment"


def test_structure_conditioned_design_contract():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.sqlite"
        store = ComputationalEvidenceStore(db_path)
        task_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        digest = "b" * 64
        evidence = {
            "analysis_mode": "structure_conditioned_design",
            "generation_performed": True,
            "package_id": "pkg_123456",
            "candidate_count": 2,
            "validation_passed": True,
            "metric_provenance": "factorforge_dual_track_dp_v3.5.5",
            "target_ref": "tgt_synth",
            "mapping_ref": "map_synth",
            "policy_ref": "structural_pause_v0",
            "cai_baseline": 0.8902,
            "cai_3dp": 0.8730,
            "pause_concordance_3dp": 0.50,
            "cds_differences": 11,
        }
        assessment_id = store.put(task_id, run_id, digest, evidence)
        assert assessment_id is not None

        retrieved = store.get(task_id)
        assert retrieved is not None
        assert retrieved["assessment_id"] == assessment_id
        assert retrieved["evidence"]["package_id"] == "pkg_123456"
        assert retrieved["evidence"]["candidate_count"] == 2
        assert retrieved["evidence"]["cds_differences"] == 11

        # Idempotent put returns same assessment_id
        same_id = store.put(task_id, run_id, digest, evidence)
        assert same_id == assessment_id

        # Conflicting evidence raises EvidenceConflict
        diff_evidence = dict(evidence, cds_differences=12)
        with pytest.raises(EvidenceConflict):
            store.put(task_id, run_id, digest, diff_evidence)


def test_invalid_evidence_contracts_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.sqlite"
        store = ComputationalEvidenceStore(db_path)
        task_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        digest = "c" * 64

        # Unknown mode
        with pytest.raises(ValueError, match="Unsupported computational evidence analysis_mode"):
            store.put(task_id, run_id, digest, {"analysis_mode": "unknown"})

        # Structure design with generation_performed=False
        bad_evidence = {
            "analysis_mode": "structure_conditioned_design",
            "generation_performed": False,  # Must be True
            "package_id": "pkg_123",
            "candidate_count": 2,
            "validation_passed": True,
            "metric_provenance": "test",
            "target_ref": "t",
            "mapping_ref": "m",
            "policy_ref": "p",
            "cai_baseline": 0.8,
            "cai_3dp": 0.8,
            "pause_concordance_3dp": 0.5,
            "cds_differences": 2,
        }
        with pytest.raises(ValueError, match="Invalid structure-conditioned design evidence contract"):
            store.put(task_id, run_id, digest, bad_evidence)
