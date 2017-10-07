import logging

from Sipper.scraper.src.database import databases
from Sipper.scraper.src.models.model import Model

logger = logging.getLogger(name="scraper")

def scrape_groups_once(scraper):
    group_db = databases["group"]
    if len(group_db) > 0:
        return

    scraper.scrape()
    groups = scraper.data.select(".ooh-groups-col li")

    for index, li in enumerate(groups):
        model = Model(group_db)
        model.update({
            "id": index,
            "fullname": li.string.strip()
            })
        model.upload()

    logger.info("Finished scraping group names")

def scrape_range(scraper, fro, to):
    if scraper.data is None:
        scraper.scrape()
