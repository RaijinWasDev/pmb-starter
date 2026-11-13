from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProgramStudi(Base):
    __tablename__ = "program_studi"
    __table_args__ = (
        UniqueConstraint("kode", name="uq_program_studi_kode"),
        CheckConstraint("length(kode) = 3", name="ck_program_studi_kode_length"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode: Mapped[str] = mapped_column(String(3), nullable=False)
    nama: Mapped[str] = mapped_column(String(120), nullable=False)
    fakultas: Mapped[str] = mapped_column(String(120), nullable=False)
    pendaftar: Mapped[list["CalonMahasiswa"]] = relationship(back_populates="program_studi")


class CalonMahasiswa(Base):
    __tablename__ = "calon_mahasiswa"
    __table_args__ = (
        UniqueConstraint("email", name="uq_calon_email"),
        UniqueConstraint("phone", name="uq_calon_phone"),
        UniqueConstraint("nim", name="uq_calon_nim"),
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_calon_status"),
        CheckConstraint("jalur_masuk IN ('SNBP', 'SNBT', 'Mandiri')", name="ck_calon_jalur_masuk"),
        Index("ix_calon_mahasiswa_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nama_lengkap: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    tanggal_lahir: Mapped[datetime] = mapped_column(Date, nullable=False)
    alamat: Mapped[str] = mapped_column(Text, nullable=False)
    program_studi_id: Mapped[int] = mapped_column(ForeignKey("program_studi.id"), nullable=False)
    jalur_masuk: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    nim: Mapped[str | None] = mapped_column(String(11), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=lambda: datetime.now(timezone.utc))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    program_studi: Mapped[ProgramStudi] = relationship(back_populates="pendaftar")
