import asyncio
import logging
from datetime import datetime
from scraper import scrape_article
from database import get_due_sources, update_source_status, save_article

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 300

async def scheduler_loop():
    while True:
        try:
            sources = get_due_sources()
            for source in sources:
                try:
                    logger.info(f"Scheduled scrape: {source['url']}")
                    result = await scrape_article(source["url"])
                    if "error" in result and result["error"]:
                        update_source_status(source["id"], "error", error=result["error"])
                    else:
                        save_article(source["user_id"], source["url"], result, source_id=source["id"])
                        update_source_status(source["id"], "ok", scraped_at=datetime.now().isoformat())
                except Exception as e:
                    logger.error(f"Scheduled scrape failed for {source['url']}: {e}")
                    update_source_status(source["id"], "error", error=str(e))
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
