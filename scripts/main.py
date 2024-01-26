import sys
from run import Runner

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <window_type> [-v]")
        sys.exit(1)

    window_type = sys.argv[1]
    
    if(window_type not in ["vertical", "horizontal"]):
        print("Invalid window type. Please enter 'vertical' or 'horizontal'.")
        sys.exit(1)

    if len(sys.argv) > 2 and sys.argv[2] == "-v":
        verbose = True
        if(window_type == "vertical"):
            print("Window type 'vertical' doesn't have verbose option")
            sys.exit(1)
    else:
        verbose = False

    runner = Runner(window_type, verbose)
    runner.run()