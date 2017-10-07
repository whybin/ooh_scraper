from Sipper.scraper.src import utils
from Sipper.scraper.src import setup
from Sipper.scraper.src import arg_parser

def main():
    parser  = arg_parser.get_arg_parser()
    args    = parser.parse_args()
    fro, to = utils.fixRange(args.fro, args.to)

    setup.setup()

if __name__ == "__main__":
    main()
