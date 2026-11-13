# Sistem Penerimaan Mahasiswa Baru (PMB)

Contoh aplikasi REST API untuk pendaftaran calon mahasiswa. Proyek ini mengikuti spesifikasi tugas: FastAPI, SQLite/SQLAlchemy, migrasi Alembic dengan rollback, validasi, persetujuan admin, NIM unik, statistik, dan tes otomatis.

## Menjalankan aplikasi

```powershell
cd pmb-starter
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Buka `http://127.0.0.1:8000/docs` untuk mencoba API melalui Swagger. Database SQLite dibuat di `pmb.db`.

## Alur utama

1. `POST /api/pmb/register` memeriksa masukan dan menyimpan pendaftar dengan status `pending`.
2. `GET /api/pmb/status/{id}` melihat status dan data pendaftar.
3. `PUT /api/pmb/approve/{id}` menyetujui pendaftar dan memberikan NIM. Bila diulang, endpoint mengembalikan NIM yang sama (idempotent).
4. `GET /api/pmb/stats` menghitung pendaftar menurut status.

Kesalahan masukan menghasilkan 400, data tak ditemukan 404, email/telepon duplikat 409, dan persetujuan ulang aman dilakukan tanpa membuat NIM baru.

## Struktur kode

- `app/models.py`: tabel `calon_mahasiswa` dan `program_studi`, beserta constraint unik.
- `app/schemas.py`: bentuk JSON dan validasi email, tanggal, serta nomor telepon Indonesia.
- `app/services.py`: aturan bisnis dan generator NIM.
- `app/routers/pmb.py`: endpoint HTTP.
- `alembic/versions/0001_initial.py`: migrasi awal; `alembic downgrade -1` membatalkannya.
- `tests/`: contoh penggunaan TestClient dan fixture database sementara.
- `AI_USAGE.md`: catatan penggunaan AI dan pemeriksaan manual yang perlu dilakukan.

## NIM dan konkurensi

Format NIM adalah `YYYYPPPXXXX`: tahun masuk 4 digit, kode prodi 3 karakter, dan nomor urut 4 digit. Contoh: `20250010001` untuk kode prodi `001`. Generator mencari urutan terbesar dalam satu prodi dan tahun, lalu membuat nomor berikutnya. Constraint unik database mencegah NIM ganda; endpoint menangani benturan transaksi dengan percobaan ulang terbatas. Pada SQLite, transaksi tulis mengambil kunci database; database produksi dengan banyak penulis dapat memakai penguncian baris yang disediakan PostgreSQL.

## Menjalankan tes

```powershell
python -m pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

Tes mencakup pendaftaran valid, duplikasi, validasi telepon/email, pembuatan NIM berurutan, persetujuan idempotent, pendaftar hilang, dan statistik. Tidak ada kredensial admin pada contoh ini: endpoint persetujuan perlu dipasangi autentikasi sebelum dipakai di lingkungan nyata.

## GitHub Desktop

Folder ini adalah repository Git lokal. Tambahkan ke GitHub Desktop dengan **File → Add Local Repository...**, lalu pilih folder `pmb-starter`. Untuk membuat repo online, gunakan **Publish repository** di GitHub Desktop setelah masuk ke akun GitHub yang akan dipakai.
