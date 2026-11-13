from fastapi import FastAPI

from app.routers.pmb import router

app = FastAPI(title="API Penerimaan Mahasiswa Baru", version="1.0.0",
              description="API registrasi, pengecekan status, persetujuan, dan statistik PMB.")
app.include_router(router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
