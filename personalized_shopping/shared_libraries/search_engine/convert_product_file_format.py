# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import sys
import platform
import subprocess
from pathlib import Path
from tqdm import tqdm

# Auto-detect and set JAVA_HOME if not already set
if not os.environ.get('JAVA_HOME'):
    try:
        system = platform.system()
        if system == 'Windows':
            # Try to find java.exe using 'where' command
            result = subprocess.run(['where', 'java'], capture_output=True, text=True)
            if result.returncode == 0:
                java_path = result.stdout.strip().split('\n')[0]
                # Get the parent directory twice to get JAVA_HOME (remove /bin/java.exe)
                java_home = str(Path(java_path).parent.parent)
                os.environ['JAVA_HOME'] = java_home
                print(f"Auto-detected JAVA_HOME: {java_home}")
        else:
            # For Linux/Mac, try to find java using 'which' command
            result = subprocess.run(['which', 'java'], capture_output=True, text=True)
            if result.returncode == 0:
                java_path = result.stdout.strip()
                # Resolve symlinks if any
                java_path = str(Path(java_path).resolve())
                # Get the parent directory twice to get JAVA_HOME
                java_home = str(Path(java_path).parent.parent)
                os.environ['JAVA_HOME'] = java_home
                print(f"Auto-detected JAVA_HOME: {java_home}")
    except Exception as e:
        print(f"Warning: Could not auto-detect JAVA_HOME: {e}")
        print("Please set JAVA_HOME environment variable manually or in your .env file")

sys.path.insert(0, "../")

from web_agent_site.engine.engine import load_products

# Auto-detect the available items_shuffle file
data_dir = Path(__file__).parent.parent / "data"
possible_files = [
    data_dir / "items_shuffle_1000.json",  # Try 1k first (recommended)
    data_dir / "items_shuffle.json",        # Full dataset
    data_dir / "items_shuffle_10000.json",  # 10k dataset
]

items_file = None
for file_path in possible_files:
    if file_path.exists():
        items_file = file_path
        print(f"Using data file: {file_path.name}")
        break

if items_file is None:
    raise FileNotFoundError(
        f"Could not find any items_shuffle*.json file in {data_dir}\n"
        f"Please download the data file. See README.md for instructions."
    )

# Load products without human_goals to avoid requiring items_human_ins.json
all_products, *_ = load_products(filepath=str(items_file), human_goals=False)

docs = []
for p in tqdm(all_products, total=len(all_products)):
    option_texts = []
    options = p.get("options", {})
    for option_name, option_contents in options.items():
        option_contents_text = ", ".join(option_contents)
        option_texts.append(f"{option_name}: {option_contents_text}")
    option_text = ", and ".join(option_texts)

    doc = dict()
    doc["id"] = p["asin"]
    doc["contents"] = " ".join(
        [
            p["Title"],
            p["Description"],
            p["BulletPoints"][0],
            option_text,
        ]
    ).lower()
    doc["product"] = p
    docs.append(doc)

# Write documents to different sized resource files
# Only create directories and files for sizes we actually have data for
total_docs = len(docs)

# Always create 100 and 1k if we have enough data
if total_docs >= 100:
    os.makedirs("./resources_100", exist_ok=True)
    with open("./resources_100/documents.jsonl", "w+") as f:
        for doc in docs[:100]:
            f.write(json.dumps(doc) + "\n")
    print(f"Created resources_100/documents.jsonl with 100 products")

if total_docs >= 1000:
    os.makedirs("./resources_1k", exist_ok=True)
    with open("./resources_1k/documents.jsonl", "w+") as f:
        for doc in docs[:1000]:
            f.write(json.dumps(doc) + "\n")
    print(f"Created resources_1k/documents.jsonl with 1000 products")

# Only create 10k and 50k if we have that much data
if total_docs >= 10000:
    os.makedirs("./resources_10k", exist_ok=True)
    with open("./resources_10k/documents.jsonl", "w+") as f:
        for doc in docs[:10000]:
            f.write(json.dumps(doc) + "\n")
    print(f"Created resources_10k/documents.jsonl with 10000 products")

if total_docs >= 50000:
    os.makedirs("./resources_50k", exist_ok=True)
    with open("./resources_50k/documents.jsonl", "w+") as f:
        for doc in docs[:50000]:
            f.write(json.dumps(doc) + "\n")
    print(f"Created resources_50k/documents.jsonl with 50000 products")

print(f"\nTotal: Created resources for {total_docs} products")
