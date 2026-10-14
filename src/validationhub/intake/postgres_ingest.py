"""Opt-in permissioned PostgreSQL adapter; default registry remains local-only."""

import math
import os
import uuid

ALLOWED_FIELDS = {
    "candidate_id",
    "arm_role",
    "readout_value",
    "measurement_type",
    "measurement_unit",
}
ARM_ROLES = {"candidate", "positive_control", "negative_control", "reference"}


def _validated_rows(records):
    if not records:
        raise ValueError("At least one measurement record is required")
    rows = []
    for row in records:
        if not isinstance(row, dict) or set(row) - ALLOWED_FIELDS:
            raise ValueError("Unrecognized measurement fields; inputs must be minimal")
        if row.get("arm_role") not in ARM_ROLES:
            raise ValueError("Unsupported arm_role")
        candidate = uuid.UUID(str(row["candidate_id"])) if row.get("candidate_id") else None
        if row["arm_role"] == "candidate" and candidate is None:
            raise ValueError("Candidate arms require a registered candidate_id")
        if row.get("readout_value") is None or isinstance(row["readout_value"], bool):
            raise ValueError("readout_value must be a finite measurement")
        value = float(row["readout_value"])
        if not math.isfinite(value) or value < 0:
            raise ValueError("readout_value must be finite and nonnegative")
        metric, unit = row.get("measurement_type"), row.get("measurement_unit")
        if (
            not isinstance(metric, str)
            or not metric.strip()
            or not isinstance(unit, str)
            or not unit.strip()
        ):
            raise ValueError("measurement_type and measurement_unit are required")
        rows.append((candidate, row["arm_role"], metric.strip(), value, unit.strip()))
    return rows


def ingest_wetlab_csv(
    assay_name,
    assay_type,
    records,
    performer_user_id=None,
    *,
    operator_id=None,
    database_url=None,
    session_factory=None,
):
    """Atomically store reviewed minimal measurements in the pinned shared schema.

    performer_user_id is a compatibility alias for canonical operator_id. This
    adapter neither approves nor publishes evidence. No implicit database exists.
    """
    operator = operator_id or performer_user_id
    if operator is None:
        raise ValueError("A registered operator_id is required")
    operator = uuid.UUID(str(operator))
    if operator_id and performer_user_id and str(operator_id) != str(performer_user_id):
        raise ValueError("Conflicting operator identity")
    if not isinstance(assay_name, str) or not assay_name.strip():
        raise ValueError("assay_name is required")
    rows = _validated_rows(records)
    from eijex_db_core.contracts import postgres_url, require_schema
    from eijex_db_core.models import AssayRun, AssayType, ExperimentalArm, Measurement
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    assay = AssayType(assay_type)
    engine = None
    if session_factory is None:
        url = database_url or os.environ.get("VALIDATIONHUB_DATABASE_URL")
        if not url or not url.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise RuntimeError("Set VALIDATIONHUB_DATABASE_URL explicitly to PostgreSQL")
        engine = create_engine(postgres_url(url), pool_pre_ping=True)
        session_factory = sessionmaker(bind=engine)
    try:
        with session_factory() as session, session.begin():
            require_schema(session)
            run = AssayRun(name=assay_name.strip(), assay_type=assay, operator_id=operator)
            session.add(run)
            session.flush()
            for candidate, role, metric, value, unit in rows:
                arm = ExperimentalArm(
                    assay_id=run.assay_id, candidate_id=candidate, control_type=role
                )
                session.add(arm)
                session.flush()
                session.add(
                    Measurement(arm_id=arm.arm_id, metric_type=metric, value=value, unit=unit)
                )
            session.flush()
            return str(run.assay_id)
    finally:
        if engine is not None:
            engine.dispose()
