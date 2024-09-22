import argparse
from collection.collect import collect
from scan import scan

def main():
    parser = argparse.ArgumentParser(description="Web spidering and SAST analysis tool.")
    parser.add_argument(
        "-u", "--url", 
        type=str, 
        help="The target URL to spider from", 
        required=False
    )
    parser.add_argument(
        "--collect-only", 
        action="store_true", 
        help="Collect page only and exit the program."
    )
    parser.add_argument(
        "--scan-only", 
        action="store_true", 
        help="Scan only and quit the program"
    )
    parser.add_argument(
        "--auth-header", 
        type=str, 
        help="Authentication header in the format 'Key=Value'", 
        required=False
    )

    args = parser.parse_args()
    
    if args.scan_only:
        scan.scan()
        return

    target = args.url
    
    if not target:
        print("Provide target to collect from --url <target>")
        return
    
    auth_header = args.auth_header

    collect(target, auth_header)
    
    print("Collection completed.")

    if args.collect_only:
        return

    scan.scan()

if __name__ == "__main__":
    main()
