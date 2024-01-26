import argparse
import sys
from run import Runner

def parse_arguments():
    parser = argparse.ArgumentParser(description="Description of your script.")

    parser.add_argument("window_type", choices=["vertical", "horizontal"], help="Specify the window type.")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode.")

    return parser.parse_args()

def main():
    args = parse_arguments()

    window_type = args.window_type
    verbose = args.verbose

    if verbose and window_type == "vertical":
        print("Window type 'vertical' doesn't have verbose option.")
        sys.exit(1)

    runner = Runner(window_type, verbose)
    runner.run()

if __name__ == "__main__":
    main()
