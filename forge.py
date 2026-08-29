import argparse
import subprocess
import sys
import tempfile
import urllib.request
import tarfile
from fileinput import filename
from pathlib import Path
from urllib import request
import json

def user_input():
    parser = argparse.ArgumentParser(
        prog="forge",
        description="Source/Binary Package Manager"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser("install", aliases=["-S"], help="Install a package")

    install_parser.add_argument(
        "packages",
        nargs="+",
        help="Packages to install"
    )
    install_parser.add_argument(
        "--ask",
        action="store_true",
        help="To confirm your installation"
    )
    install_parser.add_argument(
        "--bin",
        action="store_true",
        help="Get binary packages instead of compiling from source"
    )
    return parser.parse_args()


def ask_argument(packages: list[str], use_binary: bool) -> bool:
    mode_str = "BINARY" if use_binary else "SOURCE (Compile)"
    print("\nPackages to merge::\n")
    print(f"Mode : {mode_str}")
    for pkg in packages:
        print(f" * {pkg}")
    print()
    try:
        response = input("Would you like to merge these packages? [y/N] ").strip().lower()
        return response in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print("\nCTRL+C detected, exiting..")
        sys.exit(130)


def build_packages(build_steps: list[str], working_dir: Path):
    print(f"\n[*] Compiling from source in: {working_dir}\n")

    for step in build_steps:
        cmd_args = step.split()
        print(f"[>] Running: {step}")
        try:
            subprocess.run(cmd_args, cwd=working_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n[0!!!] Building failed at step: '{step}' (Exit code: {e.returncode})")
            raise
        except FileNotFoundError:
            print(f"\n[0!!!] Command not found: '{cmd_args[0]}'. Is the tool installed?")
            raise

    print("\n[1] Build steps completed successfully!")


def build_from_source(archive_url: str, build_steps: list[str]):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / "package.tar.gz"
        extract_dir = temp_path / "src"
        extract_dir.mkdir(parents=True, exist_ok=True)

        print(f"[*] Downloading {archive_url}...")
        urllib.request.urlretrieve(archive_url, archive_path)

        print("[*] Extracting...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_dir, filter="data")

        subdirs = [p for p in extract_dir.iterdir() if p.is_dir()]
        source_root = subdirs[0] if subdirs else extract_dir

        build_packages(build_steps, source_root)

def fetch_manifest(repo_url:str) -> dict:
    response = urllib.request.urlopen(repo_url)
    json_string = response.read().decode("utf-8")
    data = json.loads(json_string)
    return data

def main():
    args = user_input()
    REPO_URL = "http://localhost:8000/index.json"
    if args.command in ("install", "-S"):
        try:
            print(f"[*] Fetching repository index from {REPO_URL}...")
            manifest = fetch_manifest(REPO_URL)
        except Exception as e:
            print(f"[!] Failed to fetch repository manifest: {e}")
            sys.exit(1)
        build_mode = "binary" if args.bin else "source"
        if args.ask:
            proceed = ask_argument(args.packages, use_binary=args.bin)
            if not proceed:
                print("Exiting without making changes...")
                sys.exit(0)
        for pkg_name in args.packages:
            if pkg_name not in manifest:
                print(f"[0!!!] Package '{pkg_name}' not found in repository!")
                continue
            pkg_info = manifest[pkg_name]
            print(f"\n[*] Processing {pkg_name} (v{pkg_info['version']})...")
            if build_mode == "source":
                source_url = pkg_info["source"]["url"]
                build_steps = pkg_info["source"]["build_steps"]

                build_from_source(source_url, build_steps)
            else:
                print("[0!!!] Binary mode not fully wired yet.")

if __name__ == "__main__":
    main()