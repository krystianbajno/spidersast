import argparse
from collection.collect import collect

def main():
    parser = argparse.ArgumentParser(description="Web spidering and SAST analysis tool.")
    parser.add_argument(
        "-u", "--url", 
        type=str, 
        help="The target URL to spider from", 
        required=True
    )
    parser.add_argument(
        "--collect-only", 
        action="store_true", 
        help="Collect page only and exit the program."
    )

    args = parser.parse_args()

    target = args.url
    collect(target)

    if args.collect_only:
        print("Collection completed. Exiting due to --collect-only flag.")
        return

if __name__ == "__main__":
    main()
