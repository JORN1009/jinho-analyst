from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def daily_collection():
    from app.services.data_collector import data_collector
    await data_collector.collect_incremental()


def setup_scheduler():
    scheduler.add_job(
        daily_collection,
        CronTrigger(hour=4, minute=0),
        id="daily_collection",
        name="Collecte quotidienne des resultats",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown(wait=False)
