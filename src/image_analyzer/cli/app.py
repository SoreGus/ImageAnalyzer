import argparse
from image_analyzer.cli.bootstrap import run_bootstrap
from image_analyzer.cli.doctor import run_doctor

def main():
    parser = argparse.ArgumentParser(prog="image-analyzer")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("bootstrap")
    commands.add_parser("doctor")
    args = parser.parse_args()
    raise SystemExit(run_bootstrap() if args.command == "bootstrap" else run_doctor())
