import argparse
from autotender import annotator

def main():
    parser = argparse.ArgumentParser(description="AutoTender Document Tool")
    parser.add_argument("input", help="Input PDF or image")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output file")
    parser.add_argument("-c", "--config", help="Config file with annotation rules")

    args = parser.parse_args()
    annotator.annotate(args.input, args.output, args.config)

if __name__ == "__main__":
    main()
