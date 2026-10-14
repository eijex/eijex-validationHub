"""Private local computational evidence, separate from wet-lab measurements."""

import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path


class EvidenceConflict(ValueError):
    """A task already has different evidence; never overwrite it."""


class ComputationalEvidenceStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS computational_assessments (
                task_id TEXT PRIMARY KEY, assessment_id TEXT UNIQUE NOT NULL,
                run_id TEXT NOT NULL, subject_digest TEXT NOT NULL,
                schema_version TEXT NOT NULL, evidence_json TEXT NOT NULL)""")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def put(self, task_id, run_id, subject_digest, evidence):
        task_id, run_id = str(uuid.UUID(str(task_id))), str(uuid.UUID(str(run_id)))
        if not isinstance(subject_digest, str) or not re.fullmatch("[0-9a-f]{64}", subject_digest):
            raise ValueError("Invalid subject digest")
        if not isinstance(evidence, dict):
            raise ValueError("Only dictionary evidence is accepted")

        mode = evidence.get("analysis_mode")
        if mode is None:
            raise ValueError("Only minimal computational evidence with analysis_mode is accepted")
        if mode == "existing_sequence_assessment":
            fields = {
                "analysis_mode",
                "generation_performed",
                "canonical_metrics_available",
                "multi_constraint_pass",
                "gc_in_target_range",
                "metric_provenance",
            }
            if set(evidence) != fields:
                raise ValueError("Only minimal computational evidence is accepted")
            if (
                evidence["generation_performed"] is not False
                or evidence["canonical_metrics_available"] is not False
                or evidence["multi_constraint_pass"] is not None
                or type(evidence["gc_in_target_range"]) is not bool
                or evidence["metric_provenance"] != "computed_from_existing_cds_without_generation"
            ):
                raise ValueError("Invalid existing-CDS evidence contract")
        elif mode in {"structure_conditioned_design", "baseline_design"}:
            fields = {
                "analysis_mode",
                "generation_performed",
                "package_id",
                "candidate_count",
                "validation_passed",
                "metric_provenance",
                "target_ref",
                "mapping_ref",
                "policy_ref",
                "cai_baseline",
                "cai_3dp",
                "pause_concordance_3dp",
                "cds_differences",
            }
            if mode == "baseline_design":
                fields -= {"cai_3dp", "pause_concordance_3dp", "cds_differences"}
            if set(evidence) != fields:
                raise ValueError("Invalid structure-conditioned design evidence fields")
            if (
                evidence["generation_performed"] is not True
                or evidence["validation_passed"] is not True
                or not isinstance(evidence["package_id"], str)
                or type(evidence["candidate_count"]) is not int
                or evidence["candidate_count"] < 1
                or not isinstance(evidence["metric_provenance"], str)
                or not isinstance(evidence["target_ref"], str)
                or not isinstance(evidence["policy_ref"], str)
                or type(evidence["cai_baseline"]) not in (int, float)
                or (
                    mode == "structure_conditioned_design"
                    and type(evidence["cai_3dp"]) not in (int, float)
                )
                or (
                    mode == "structure_conditioned_design"
                    and type(evidence["pause_concordance_3dp"]) not in (int, float)
                )
                or (
                    mode == "structure_conditioned_design"
                    and type(evidence["cds_differences"]) is not int
                )
            ):
                raise ValueError("Invalid structure-conditioned design evidence contract")
            refs = ("package_id", "target_ref", "mapping_ref", "policy_ref", "metric_provenance")
            if any(
                not isinstance(evidence[k], str)
                or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", evidence[k])
                for k in refs
            ):
                raise ValueError("Invalid opaque evidence reference")
            if (
                any(
                    not 0 <= evidence.get(k, 0) <= 1
                    for k in ("cai_baseline", "cai_3dp", "pause_concordance_3dp")
                )
                or evidence.get("cds_differences", 0) < 0
            ):
                raise ValueError("Invalid computational evidence metric range")
        else:
            raise ValueError("Unsupported computational evidence analysis_mode")
        encoded = json.dumps(evidence, sort_keys=True, allow_nan=False)
        assessment_id = str(uuid.uuid4())
        with self.connection() as db:
            existing = db.execute(
                "SELECT * FROM computational_assessments WHERE task_id=?", (task_id,)
            ).fetchone()
            if existing:
                if (existing["run_id"], existing["subject_digest"], existing["evidence_json"]) != (
                    run_id,
                    subject_digest,
                    encoded,
                ):
                    raise EvidenceConflict("Existing task evidence differs")
                return existing["assessment_id"]
            db.execute(
                "INSERT INTO computational_assessments VALUES (?,?,?,?,?,?)",
                (task_id, assessment_id, run_id, subject_digest, "0.1.0", encoded),
            )
        return assessment_id

    def get(self, task_id):
        task_id = str(uuid.UUID(str(task_id)))
        with self.connection() as db:
            row = db.execute(
                "SELECT * FROM computational_assessments WHERE task_id=?", (task_id,)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["evidence"] = json.loads(result.pop("evidence_json"))
        return result
