"""Canonical candidate/measurement linkage with rollback and schema-head checks."""

import hashlib
import os
import uuid

import pytest

if not os.environ.get("EIJEX_TEST_DATABASE_URL"):
    pytest.skip("Explicit isolated test DB not configured", allow_module_level=True)
pytest.importorskip("eijex_db_core")
from eijex_db_core.models import (
    Artifact,
    ArtifactType,
    AssayRun,
    Campaign,
    Candidate,
    EncryptionStatus,
    ExperimentalArm,
    Measurement,
    MoleculeClass,
    Organization,
    OrganizationType,
    Sequence,
    User,
    UserRole,
)
from eijex_db_core.testing import isolated_test_sessions
from sqlalchemy import func, select

from validationhub.intake.db_ingest import ingest_wetlab_csv


@pytest.fixture
def setup():
    with isolated_test_sessions() as factory:
        with factory() as session, session.begin():
            org = Organization(
                display_name="Synthetic", organization_type=OrganizationType.internal
            )
            session.add(org)
            session.flush()
            user = User(
                organization_id=org.organization_id,
                display_name="Synthetic operator",
                role=UserRole.researcher,
            )
            session.add(user)
            session.flush()
            digest = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
            artifact = Artifact(
                artifact_uri="synthetic://test",
                sha256_hash=digest,
                mime_type="text/plain",
                size_bytes=9,
                artifact_type=ArtifactType.other,
                encryption_status=EncryptionStatus.none,
            )
            session.add(artifact)
            session.flush()
            seq = Sequence(
                molecule_class=MoleculeClass.CDS,
                canonical_sequence_sha256=digest,
                artifact_id=artifact.artifact_id,
                length=9,
            )
            campaign = Campaign(name="TEST-" + uuid.uuid4().hex)
            session.add_all([seq, campaign])
            session.flush()
            candidate = Candidate(
                campaign_id=campaign.campaign_id,
                sequence_id=seq.sequence_id,
                designer_user_id=user.user_id,
            )
            session.add(candidate)
            session.flush()
            yield factory, user.user_id, candidate.candidate_id


def rows(candidate):
    return [
        dict(
            candidate_id=str(candidate),
            arm_role="candidate",
            measurement_type="yield",
            readout_value=14.7,
            measurement_unit="mg/L",
        ),
        dict(
            candidate_id="",
            arm_role="negative_control",
            measurement_type="yield",
            readout_value=0,
            measurement_unit="mg/L",
        ),
    ]


def test_dbtl_integration_query(setup):
    factory, user, candidate = setup
    assay = ingest_wetlab_csv(
        "TEST-synthetic",
        "expression_yield",
        rows(candidate),
        operator_id=user,
        session_factory=factory,
    )
    with factory() as session:
        result = session.execute(
            select(ExperimentalArm.control_type, ExperimentalArm.candidate_id, Measurement.value)
            .join(Measurement, Measurement.arm_id == ExperimentalArm.arm_id)
            .where(ExperimentalArm.assay_id == uuid.UUID(assay))
            .order_by(Measurement.value.desc())
        ).all()
        assert result == [("candidate", candidate, 14.7), ("negative_control", None, 0.0)]


def test_invalid_candidate_rolls_back_entire_ingestion(setup):
    factory, user, candidate = setup
    from sqlalchemy.exc import IntegrityError

    with factory() as session:
        before = session.scalar(select(func.count()).select_from(AssayRun))
    with pytest.raises(IntegrityError):
        ingest_wetlab_csv(
            "TEST-invalid",
            "expression_yield",
            rows(uuid.uuid4()),
            operator_id=user,
            session_factory=factory,
        )
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(AssayRun)) == before


def test_incompatible_schema_is_rejected(setup):
    factory, user, candidate = setup
    from sqlalchemy import text

    with factory() as session, session.begin():
        session.execute(text("UPDATE alembic_version SET version_num='unsupported'"))
    with pytest.raises(RuntimeError, match="schema"):
        ingest_wetlab_csv(
            "TEST-schema",
            "expression_yield",
            rows(candidate),
            operator_id=user,
            session_factory=factory,
        )
