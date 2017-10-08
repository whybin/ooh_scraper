import logging, re

from tinydb import Query

from Sipper.scraper.include.config import config
from Sipper.scraper.src.database import databases
from Sipper.scraper.src.models.model import Model
from Sipper.scraper.src.utils import absolute_url
from Sipper.scraper.src.scraper import Scraper

logger = logging.getLogger(name="scraper")
number_rgx = "([\d,.]+)"
NA_TEXT = "-"

def extract_number(text):
    """
    :param text:
    :type text: string
    :returns: None|float
    """
    num = re.search(number_rgx, text)
    return (num if num is None
            else float(num.group(0).replace(",", "")))

def handle_expected_string(text):
    """
    Handle text where a string is expected but could be a nested HTML element
    instead.
    :param text:
    :type text: None|string
    :returns: string
    """
    return text.strip() if text is not None else NA_TEXT

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

    # Prepare ahead of time
    per_year_rgx = number_rgx + " +per year"
    per_hour_rgx = number_rgx + " +per hour"
    Occupation = Query()

    to = min(to, len(groups)) # Cap the upper bound

    # For now, assume `i` is group ID
    for i in range(fro, to):
        href = absolute_url(config["site.start_url"], groups[i]["href"])
        href = href.rsplit("/", 1)[0]

        logger.info("Scraping group: " + groups[i].string.strip())
        group_scraper = Scraper(href).read().scrape()

        occ_rows = group_scraper.data.select("#landing-page-table tr")
        for row in occ_rows:
            if row.td is None:
                continue

            link = row.select("td")[1].a
            occ_name = link.string.strip()

            # Check if occupation already scraped
            res = databases["occupation"].get(Occupation.name == occ_name)
            if res is not None:
                logger.info("!! Already scraped: " + occ_name)
                continue

            occ_url = absolute_url(config["site.start_url"], link["href"])

            brief = row.select("td")[2].p
            if brief is None:
                continue

            data = {
                    "id": occ_index,
                    "category_id": i,
                    "name": occ_name,
                    "brief": brief.string
                    }

            logger.info("Scraping occupation: " + occ_name)
            occ_scraper = Scraper(occ_url).read().scrape()

            quick_facts = occ_scraper.data.select("#quickfacts tbody td")

            median_pay_strings = quick_facts[0].strings
            median_pay = ""
            for string in median_pay_strings:
                median_pay = median_pay + string

            per_year = re.search(per_year_rgx, median_pay)
            per_hour = re.search(per_hour_rgx, median_pay)
            if per_year is not None:
                per_year = extract_number(per_year.group(1))
            if per_hour is not None:
                per_hour = extract_number(per_hour.group(1))

            similar_occ_links = (occ_scraper.data
                    .select("#similar-occupations h4 a"))
            similar_occ_names = [link.string.strip()
                    for link in similar_occ_links]

            data.update({
                "pay_per_year": per_year,
                "pay_per_hour": per_hour,
                "entry_level": handle_expected_string(quick_facts[1].string),
                "work_experience": handle_expected_string(quick_facts[2].string),
                "job_training": handle_expected_string(quick_facts[3].string),
                "total_jobs": extract_number(quick_facts[4].string),
                "job_growth": extract_number(quick_facts[5].string),
                "total_new_jobs": extract_number(quick_facts[6].string),
                "similar_occupations": similar_occ_names
                })
            occ_model = Model(databases["occupation"]).update(data)
            occ_model.upload()

            occ_index = occ_index + 1
