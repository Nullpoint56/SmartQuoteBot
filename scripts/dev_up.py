#!/usr/bin/env python3
import os
import subprocess
import sys
from scripts.utils import sanitize_branch_name

def get_default_branch_tag():
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True
        ).strip()
        return sanitize_branch_name(branch)
    except Exception:
        return "latest"

def main():
    print("🔧 SmartQuoteBot Dev Runner")
    tag = input(f"Enter image tag to use [default: current branch]: ").strip()
    if not tag:
        tag = get_default_branch_tag()

    os.environ["IMAGE_TAG"] = tag

    try:
        subprocess.run([
            "docker", "compose",
            "-f", "docker-compose.yml",
            "-f", "docker-compose.override.yml",
            "up", "-d", "--build", "--remove-orphans"
        ], check=True)
    except subprocess.CalledProcessError:
        sys.exit("❌ Docker Compose failed.")

if __name__ == "__main__":
    main()
