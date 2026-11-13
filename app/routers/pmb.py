from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CalonMahasiswa, ProgramStudi
from app.schemas import ApprovalRead, ApplicantRead, RegistrationCreate, StatsRead
from app.services import (DuplicateRegistration, InvalidTransition, NIMGenerationError,
                          approve_applicant, register_applicant)

router = APIRouter(prefix="/api/pmb", tags=["PMB"])


@router.post("/register", response_model=ApplicantRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegistrationCreate, db: Session = Depends(get_db)):
    if not db.get(ProgramStudi, payload.program_studi_id):
        raise HTTPException(status_code=400, detail="Program studi tidak ditemukan.")
    try:
        return register_applicant(db, payload.model_dump())
    except DuplicateRegistration:
        raise HTTPException(status_code=409, detail="Email atau nomor telepon sudah terdaftar.") from None


@router.get("/status/{applicant_id}", response_model=ApplicantRead)
def get_status(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(CalonMahasiswa, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Pendaftar tidak ditemukan.")
    return applicant


@router.put("/approve/{applicant_id}", response_model=ApprovalRead)
def approve(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(CalonMahasiswa, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Pendaftar tidak ditemukan.")
    try:
        nim = approve_applicant(db, applicant)
    except InvalidTransition as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except NIMGenerationError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return ApprovalRead(id=applicant.id, status=applicant.status, nim=nim,
                        approved_at=applicant.approved_at)


@router.get("/stats", response_model=StatsRead)
def get_stats(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(CalonMahasiswa.status, func.count(CalonMahasiswa.id))
                             .group_by(CalonMahasiswa.status)).all())
    pending, approved, rejected = (counts.get(key, 0) for key in ("pending", "approved", "rejected"))
    return StatsRead(total=pending + approved + rejected, pending=pending,
                     approved=approved, rejected=rejected)
