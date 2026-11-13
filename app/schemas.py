import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def normalize_indonesian_phone(value: str) -> str:
    digits = re.sub(r"[\s()-]", "", value)
    if digits.startswith("+62"):
        digits = "0" + digits[3:]
    elif digits.startswith("62"):
        digits = "0" + digits[2:]
    if not re.fullmatch(r"08\d{8,11}", digits):
        raise ValueError("Nomor telepon harus nomor seluler Indonesia (08..., 10–13 digit).")
    return digits


class RegistrationCreate(BaseModel):
    nama_lengkap: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    tanggal_lahir: date
    alamat: str = Field(min_length=5, max_length=2000)
    program_studi_id: int = Field(gt=0)
    jalur_masuk: Literal["SNBP", "SNBT", "Mandiri"]

    @field_validator("nama_lengkap", "alamat")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nilai tidak boleh kosong.")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_indonesian_phone(value)

    @field_validator("tanggal_lahir")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Tanggal lahir harus sebelum hari ini.")
        return value


class ApplicantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nama_lengkap: str
    email: EmailStr
    phone: str
    tanggal_lahir: date
    alamat: str
    program_studi_id: int
    jalur_masuk: str
    status: str
    nim: str | None
    created_at: datetime
    approved_at: datetime | None


class ApprovalRead(BaseModel):
    id: int
    status: str
    nim: str
    approved_at: datetime


class StatsRead(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
