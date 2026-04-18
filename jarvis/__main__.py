import argparse
from jarvis.loop import start_cli, start_voice

def main():
    parser = argparse.ArgumentParser(description="Jarvis — Offline AI Operator")
    parser.add_argument("--mode", choices=["cli", "voice"], default="cli", help="Interface mode")
    args = parser.parse_args()
    if args.mode == "voice":
        start_voice()
    else:
        start_cli()

if __name__ == "__main__":
    main()
