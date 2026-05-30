from fastapi import APIRouter, BackgroundTasks
from app.services.data_collector import data_collector
from app.ml.trainer import football_trainer

router = APIRouter()


@router.post("/collect-football")
async def collect_football(background_tasks: BackgroundTasks, seasons: str = "2022,2023,2024"):
    season_list = [int(s.strip()) for s in seasons.split(",")]
    background_tasks.add_task(data_collector.collect_all_football, season_list)
    return {"status": "started", "seasons": season_list, "leagues": ["PL", "PD", "BL1", "SA", "FL1"]}


@router.post("/collect-basketball")
async def collect_basketball(background_tasks: BackgroundTasks, seasons: str = "2022,2023,2024"):
    season_list = [int(s.strip()) for s in seasons.split(",")]
    background_tasks.add_task(data_collector.collect_all_basketball, season_list)
    return {"status": "started", "seasons": season_list}


@router.post("/collect-incremental")
async def collect_incremental(background_tasks: BackgroundTasks):
    background_tasks.add_task(data_collector.collect_incremental)
    return {"status": "started", "message": "Collecte incrementale lancee"}


@router.post("/train-football")
def train_football():
    metrics = football_trainer.train()
    return metrics


@router.get("/stats")
def get_data_stats():
    stats = data_collector.get_stats()
    stats["model_trained"] = football_trainer.is_trained
    return stats
