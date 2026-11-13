import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import ProgramStudi


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        db.add_all([
            ProgramStudi(kode="001", nama="Teknik Informatika", fakultas="Teknik"),
            ProgramStudi(kode="002", nama="Sistem Informasi", fakultas="Ilmu Komputer"),
        ])
        db.commit()

    def override_get_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def registration():
    return {
        "nama_lengkap": "Ayu Pratama", "email": "ayu@example.com", "phone": "081234567890",
        "tanggal_lahir": "2005-04-20", "alamat": "Jalan Melati Nomor 12",
        "program_studi_id": 1, "jalur_masuk": "SNBT",
    }
