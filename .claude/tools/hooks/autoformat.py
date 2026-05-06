#!/usr/bin/env python3
import json, sys, subprocess, os, shutil

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "")

if file_path.endswith(".py") and shutil.which("uv"):
    result = subprocess.run(["uv", "run", "ruff", "format", file_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ ruff format: {os.path.basename(file_path)}")

elif file_path.endswith((".js", ".ts", ".tsx", ".jsx")) and shutil.which("pnpm"):
    result = subprocess.run(["pnpm", "exec", "prettier", "--write", file_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ prettier: {os.path.basename(file_path)}")
