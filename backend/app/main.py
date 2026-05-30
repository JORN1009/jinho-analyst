from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import football, basketball, tennis, mma, predictions
from app.api import training
from app.db.database import initialize_database
from app.scheduler.jobs import setup_scheduler, shutdown_scheduler

app = FastAPI(title="JINHO Analyst", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(football.router, prefix="/api/football", tags=["Football"])
app.include_router(basketball.router, prefix="/api/basketball", tags=["Basketball"])
app.include_router(tennis.router, prefix="/api/tennis", tags=["Tennis"])
app.include_router(mma.router, prefix="/api/mma", tags=["MMA"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(training.router, prefix="/api/training", tags=["Training & Data"])


@app.on_event("startup")
async def startup_event():
    initialize_database()
    setup_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "JINHO Analyst"}


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
