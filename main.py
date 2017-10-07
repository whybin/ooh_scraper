from Sipper.scraper.src import utils
from Sipper.scraper.src import setup
from Sipper.scraper.src import arg_parser

import scrape

def main():
    parser  = arg_parser.get_arg_parser()
    args    = parser.parse_args()
    fro, to = utils.fixRange(args.fro, args.to)

    scraper = setup.setup_scraper()
    scrape.scrape_groups_once(scraper)
    scrape.scrape_range(scraper, fro, to)

if __name__ == "__main__":
    main()
