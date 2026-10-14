import subprocess
import sys
import uuid

import pytest

from validationhub.intake.postgres_ingest import _validated_rows, ingest_wetlab_csv


def test_import_does_not_connect_or_load_optional_packages():
    code = (
        "import sys; import validationhub.intake.db_ingest; assert 'sqlalchemy' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


@pytest.mark.parametrize("bad", [None, True, float("nan"), float("inf"), -1])
def test_invalid_values_are_rejected_before_database_access(bad):
    with pytest.raises(ValueError):
        _validated_rows(
            [
                dict(
                    candidate_id=str(uuid.uuid4()),
                    arm_role="candidate",
                    readout_value=bad,
                    measurement_type="yield",
                    measurement_unit="mg/L",
                )
            ]
        )


def test_operator_and_candidate_identity_required():
    with pytest.raises(ValueError, match="operator_id"):
        ingest_wetlab_csv("synthetic", "expression_yield", [])
    with pytest.raises(ValueError, match="candidate_id"):
        _validated_rows(
            [
                dict(
                    arm_role="candidate",
                    readout_value=1,
                    measurement_type="yield",
                    measurement_unit="mg/L",
                )
            ]
        )


def test_zero_is_preserved_and_sequence_fields_rejected():
    row = dict(
        arm_role="negative_control",
        readout_value=0,
        measurement_type="yield",
        measurement_unit="mg/L",
    )
    assert _validated_rows([row])[0][3] == 0
    with pytest.raises(ValueError, match="minimal"):
        _validated_rows([{**row, "raw_sequence": "synthetic-blocked"}])
