"""Create PMB tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "program_studi",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kode", sa.String(length=3), nullable=False),
        sa.Column("nama", sa.String(length=120), nullable=False),
        sa.Column("fakultas", sa.String(length=120), nullable=False),
        sa.CheckConstraint("length(kode) = 3", name="ck_program_studi_kode_length"),
        sa.UniqueConstraint("kode", name="uq_program_studi_kode"),
    )
    op.create_table(
        "calon_mahasiswa",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nama_lengkap", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=False),
        sa.Column("tanggal_lahir", sa.Date(), nullable=False),
        sa.Column("alamat", sa.Text(), nullable=False),
        sa.Column("program_studi_id", sa.Integer(), nullable=False),
        sa.Column("jalur_masuk", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("nim", sa.String(length=11), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("jalur_masuk IN ('SNBP', 'SNBT', 'Mandiri')", name="ck_calon_jalur_masuk"),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_calon_status"),
        sa.ForeignKeyConstraint(["program_studi_id"], ["program_studi.id"]),
        sa.UniqueConstraint("email", name="uq_calon_email"),
        sa.UniqueConstraint("phone", name="uq_calon_phone"),
        sa.UniqueConstraint("nim", name="uq_calon_nim"),
    )
    op.create_index("ix_calon_mahasiswa_status", "calon_mahasiswa", ["status"])
    op.create_index("ix_calon_nim", "calon_mahasiswa", ["nim"])


def downgrade() -> None:
    op.drop_index("ix_calon_nim", table_name="calon_mahasiswa")
    op.drop_index("ix_calon_mahasiswa_status", table_name="calon_mahasiswa")
    op.drop_table("calon_mahasiswa")
    op.drop_table("program_studi")
