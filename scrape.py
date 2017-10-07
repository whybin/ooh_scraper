import logging

from Sipper.scraper.include.config import config
from Sipper.scraper.src.database import databases
from Sipper.scraper.src.models.model import Model
from Sipper.scraper.src.utils import absolute_url
from Sipper.scraper.src.scraper import Scraper

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
    if type(scraper.data) is str:
        scraper.scrape()

    groups = scraper.data.select(".ooh-groups-col li a")
    occ_db = databases["occupation"]
    occ_index = len(occ_db)

    to = min(to, len(groups)) # Cap the upper bound

    # For now, assume `i` is group ID
    for i in range(fro, to):
        href = absolute_url(config["site.start_url"], groups[i]["href"])
        href = href.rsplit("/", 1)[0]
        group_scraper = Scraper(href).read().scrape()

        occ_rows = group_scraper.data.select("#landing-page-table tr")
        for row in occ_rows:
            if row.td is None:
                continue

            link = row.select("td")[1].a
            occ_name = link.string.strip()
            occ_url = absolute_url(config["site.start_url"], link["href"])

            occ_scraper = Scraper(occ_url).read().scrape()
