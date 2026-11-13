import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import ProgramStudi


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with TestingSession() as session:
        session.add_all([
            ProgramStudi(kode="001", nama="Teknik Informatika", fakultas="Teknik"),
            ProgramStudi(kode="002", nama="Sistem Informasi", fakultas="Ilmu Komputer"),
        ])
        session.commit()
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def registration():
    return {
        "nama_lengkap": "Ayu Pratama", "email": "ayu@example.com", "phone": "081234567890",
        "tanggal_lahir": "2005-04-20", "alamat": "Jalan Melati Nomor 12",
        "program_studi_id": 1, "jalur_masuk": "SNBT",
    }
