from datetime import date

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models import CalonMahasiswa
from app.routers.pmb import approve, get_stats, get_status, register
from app.schemas import RegistrationCreate


def test_register_success(db, registration):
    result = register(RegistrationCreate(**registration), db)
    assert result.status == "pending"
    assert result.nim is None


def test_duplicate_email_is_conflict(db, registration):
    register(RegistrationCreate(**registration), db)
    duplicate = {**registration, "phone": "081298765432"}
    with pytest.raises(HTTPException) as error:
        register(RegistrationCreate(**duplicate), db)
    assert error.value.status_code == 409


@pytest.mark.parametrize("field,value", [
    ("phone", "12345"), ("email", "bukan-email"),
    ("tanggal_lahir", date.today().isoformat()),
])
def test_invalid_registration_fields_are_rejected(registration, field, value):
    with pytest.raises(ValidationError):
        RegistrationCreate(**{**registration, field: value})


def test_missing_program_is_bad_request(db, registration):
    with pytest.raises(HTTPException) as error:
        register(RegistrationCreate(**{**registration, "program_studi_id": 999}), db)
    assert error.value.status_code == 400


def test_approve_generates_sequential_nim_and_is_idempotent(db, registration):
    first = register(RegistrationCreate(**registration), db)
    second = register(RegistrationCreate(**{
        **registration, "email": "budi@example.com", "phone": "081211112222",
    }), db)
    assert approve(first.id, db).nim == "20260010001"
    assert approve(second.id, db).nim == "20260010002"
    assert approve(first.id, db).nim == "20260010001"


def test_status_not_found(db):
    with pytest.raises(HTTPException) as error:
        get_status(999, db)
    assert error.value.status_code == 404


def test_approve_not_found(db):
    with pytest.raises(HTTPException) as error:
        approve(999, db)
    assert error.value.status_code == 404


def test_stats(db, registration):
    register(RegistrationCreate(**registration), db)
    result = get_stats(db)
    assert result.model_dump() == {"total": 1, "pending": 1, "approved": 0, "rejected": 0}


def test_status_response_contains_registration(db, registration):
    applicant = register(RegistrationCreate(**registration), db)
    assert get_status(applicant.id, db).email == registration["email"]
