import argparse
from ynab_convert_rd.core import run_all, DEFAULT_SOURCE_DIR, DEFAULT_RESULT_DIR

def main():
    parser = argparse.ArgumentParser(
        description="YNAB RD Convert Tool - Convert Dominican bank files to YNAB CSV format."
    )
    parser.add_argument(
        '-s', '--source', default=DEFAULT_SOURCE_DIR,
        help="Source directory containing bank files (default: data/)"
    )
    parser.add_argument(
        '-r', '--result', default=DEFAULT_RESULT_DIR,
        help="Result directory for output CSVs (default: result/)"
    )
    args = parser.parse_args()
    run_all(args.source, args.result)

if __name__ == '__main__':
    main()
