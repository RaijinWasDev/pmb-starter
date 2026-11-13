import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models import CalonMahasiswa


class DuplicateRegistration(Exception):
    pass


class InvalidTransition(Exception):
    pass


class NIMGenerationError(Exception):
    pass


def register_applicant(db: Session, values: dict) -> CalonMahasiswa:
    applicant = CalonMahasiswa(**values, status="pending")
    db.add(applicant)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise DuplicateRegistration from error
    db.refresh(applicant)
    return applicant


def generate_nim(db: Session, applicant: CalonMahasiswa, year: int | None = None) -> str:
    """Allocate YYYYPPPXXXX inside a write transaction; unique DB constraint is final guard."""
    year = year or datetime.now(timezone.utc).year
    if not 1000 <= year <= 9999:
        raise ValueError("Tahun NIM harus terdiri dari empat digit.")
    code = applicant.program_studi.kode
    prefix = f"{year}{code}"
    for attempt in range(3):
        try:
            db.add(applicant)
            db.flush()  # SQLite serializes writers here; PostgreSQL can lock matching rows below.
            if db.bind and db.bind.dialect.name == "postgresql":
                db.execute(select(CalonMahasiswa.id).where(
                    CalonMahasiswa.nim.like(f"{prefix}%")
                ).with_for_update())
            last_nim = db.scalar(select(func.max(CalonMahasiswa.nim)).where(
                CalonMahasiswa.nim.like(f"{prefix}%")
            ))
            sequence = int(last_nim[-4:]) + 1 if last_nim else 1
            if sequence > 9999:
                raise NIMGenerationError("Nomor urut NIM untuk program studi ini sudah penuh.")
            nim = f"{prefix}{sequence:04d}"
            if not re.fullmatch(r"\d{4}[A-Z0-9]{3}\d{4}", nim):
                raise NIMGenerationError("Format kode program studi tidak dapat digunakan untuk NIM.")
            applicant.nim = nim
            applicant.status = "approved"
            applicant.approved_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(applicant)
            return nim
        except NIMGenerationError:
            db.rollback()
            raise
        except (IntegrityError, OperationalError) as error:
            db.rollback()
            if attempt == 2:
                raise NIMGenerationError("Terjadi benturan saat membuat NIM; silakan coba lagi.") from error
    raise NIMGenerationError("NIM tidak dapat dibuat.")


def approve_applicant(db: Session, applicant: CalonMahasiswa) -> str:
    if applicant.status == "approved" and applicant.nim:
        return applicant.nim
    if applicant.status != "pending":
        raise InvalidTransition("Pendaftar yang ditolak tidak dapat disetujui.")
    return generate_nim(db, applicant)
