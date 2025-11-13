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

import os
import sys
import json
import glob
import platform
from datetime import datetime
from pathlib import Path

import dotenv
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


def find_java_home():
    """
    Automatically detect JAVA_HOME from common installation paths.
    Returns the path to the best Java installation (21+) or None if not found.
    """
    # First check if JAVA_HOME is already set
    if os.environ.get("JAVA_HOME"):
        java_home = os.environ["JAVA_HOME"]
        if os.path.exists(os.path.join(java_home, "bin", "java.exe" if platform.system() == "Windows" else "java")):
            print(f"[OK] Using existing JAVA_HOME: {java_home}")
            return java_home

    system = platform.system()
    java_installations = []

    if system == "Windows":
        # Common Java installation directories on Windows
        search_paths = [
            r"C:\Program Files\Eclipse Adoptium",
            r"C:\Program Files\Java",
            r"C:\Program Files\OpenJDK",
            r"C:\Program Files (x86)\Eclipse Adoptium",
            r"C:\Program Files (x86)\Java",
            r"C:\Program Files (x86)\OpenJDK",
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                # Find all jdk* directories
                for jdk_dir in glob.glob(os.path.join(search_path, "jdk*")):
                    java_exe = os.path.join(jdk_dir, "bin", "java.exe")
                    if os.path.exists(java_exe):
                        # Extract version number from directory name
                        import re
                        match = re.search(r"jdk-?(\d+)", os.path.basename(jdk_dir))
                        if match:
                            version = int(match.group(1))
                            java_installations.append({
                                "path": jdk_dir,
                                "version": version
                            })

    elif system == "Darwin":  # macOS
        # Common Java installation directories on macOS
        search_paths = [
            "/Library/Java/JavaVirtualMachines",
            os.path.expanduser("~/Library/Java/JavaVirtualMachines"),
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                for jdk_dir in glob.glob(os.path.join(search_path, "*.jdk")):
                    java_home = os.path.join(jdk_dir, "Contents", "Home")
                    java_exe = os.path.join(java_home, "bin", "java")
                    if os.path.exists(java_exe):
                        import re
                        match = re.search(r"jdk-?(\d+)", os.path.basename(jdk_dir))
                        if match:
                            version = int(match.group(1))
                            java_installations.append({
                                "path": java_home,
                                "version": version
                            })

    else:  # Linux
        # Common Java installation directories on Linux
        search_paths = [
            "/usr/lib/jvm",
            "/usr/java",
            "/opt/java",
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                for jdk_dir in glob.glob(os.path.join(search_path, "*jdk*")):
                    java_exe = os.path.join(jdk_dir, "bin", "java")
                    if os.path.exists(java_exe):
                        import re
                        match = re.search(r"jdk-?(\d+)", os.path.basename(jdk_dir))
                        if match:
                            version = int(match.group(1))
                            java_installations.append({
                                "path": jdk_dir,
                                "version": version
                            })

    if not java_installations:
        print("[FAIL] No Java installation found!")
        print("  Please install Java 21+ from https://adoptium.net/")
        return None

    # Sort by version (highest first) and pick the best one (21+)
    java_installations.sort(key=lambda x: x["version"], reverse=True)
    best_java = next((j for j in java_installations if j["version"] >= 21), None)

    if not best_java:
        print("[FAIL] Found Java installations, but none are version 21 or higher!")
        print("  Found versions:")
        for java in java_installations:
            print(f"    - Java {java['version']}: {java['path']}")
        print("\n  Please install Java 21+ from https://adoptium.net/")
        return None

    print(f"[OK] Found Java {best_java['version']}: {best_java['path']}")
    return best_java["path"]


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables and set up JAVA_HOME."""
    dotenv.load_dotenv()

    # Auto-detect and set JAVA_HOME if not already set
    if not os.environ.get("JAVA_HOME"):
        java_home = find_java_home()
        if java_home:
            os.environ["JAVA_HOME"] = java_home
            print(f"[OK] Set JAVA_HOME to: {java_home}")
        else:
            pytest.fail("JAVA_HOME could not be detected. Please install Java 21+ or set JAVA_HOME manually.")


@pytest.mark.asyncio
async def test_simple(capsys):
    """Test the agent's basic ability on a few examples."""
    eval_data_dir = os.path.join(os.path.dirname(__file__), "eval_data")
    results_dir = os.path.join(os.path.dirname(__file__), "test_results")
    os.makedirs(results_dir, exist_ok=True)

    # Run evaluation and capture results
    print("\n" + "="*80)
    print("Running Simple Evaluation Test")
    print("="*80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # Run evaluation (output will be captured by capsys)
        result = await AgentEvaluator.evaluate(
            "personalized_shopping",
            eval_data_dir,
            num_runs=1,
            print_detailed_results=True,
        )

        # Get captured output from pytest
        captured = capsys.readouterr()
        evaluation_output = captured.out + captured.err

        # Parse evaluation results from output
        eval_results = {
            "test_cases": [],
            "metrics": {},
            "status": "PASSED"
        }

        # Extract metrics from output
        lines = evaluation_output.split('\n')
        for i, line in enumerate(lines):
            if 'tool_trajectory_avg_score' in line.lower():
                # Try to extract score
                for j in range(max(0, i-5), min(len(lines), i+5)):
                    if 'score' in lines[j].lower() or 'value' in lines[j].lower():
                        eval_results["metrics"]["tool_trajectory_score"] = lines[j].strip()
            if 'response_match_score' in line.lower():
                for j in range(max(0, i-5), min(len(lines), i+5)):
                    if 'score' in lines[j].lower() or 'value' in lines[j].lower():
                        eval_results["metrics"]["response_match_score"] = lines[j].strip()
            if 'query:' in line.lower() or 'prompt:' in line.lower():
                eval_results["test_cases"].append(line.strip())
            if 'actual_response' in line.lower() or 'agent response' in line.lower():
                # Capture agent responses
                response_text = []
                for j in range(i+1, min(len(lines), i+10)):
                    if lines[j].strip() and not lines[j].startswith('-'):
                        response_text.append(lines[j].strip())
                    else:
                        break
                if response_text:
                    eval_results["test_cases"].append("Response: " + " ".join(response_text))

        # Check if test failed
        if 'FAILED' in evaluation_output or 'failed' in evaluation_output.lower():
            eval_results["status"] = "FAILED"

        # Save detailed results to file
        result_file = os.path.join(results_dir, f"simple_test_{timestamp}.json")

        # Convert result to serializable format
        result_data = {
            "timestamp": timestamp,
            "test_name": "simple",
            "status": eval_results["status"],
            "metrics": eval_results["metrics"],
            "test_cases_output": eval_results["test_cases"][:20],  # Limit to first 20 entries
            "full_output_length": len(evaluation_output),
            "full_output": evaluation_output,  # No limit - save everything
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        # Create a human-readable summary
        summary_file = os.path.join(results_dir, f"simple_test_{timestamp}_summary.txt")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("Simple Evaluation Test Results\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Test: simple (greeting and basic interaction)\n")
            f.write(f"Status: {eval_results['status']}\n\n")

            f.write("Test Files:\n")
            f.write("-" * 80 + "\n")
            f.write("Running all .test.json files in eval_data/:\n")
            test_files = glob.glob(os.path.join(eval_data_dir, "*.test.json"))
            for test_file in test_files:
                f.write(f"  - {os.path.basename(test_file)}\n")
            f.write("\n\n")

            f.write("Evaluation Results:\n")
            f.write("-" * 80 + "\n")
            f.write("NOTE: The detailed evaluation summary table with agent responses and scores\n")
            f.write("is displayed during test execution but uses terminal-specific formatting\n")
            f.write("that cannot be captured in this file.\n\n")
            f.write("To see the full evaluation summary:\n")
            f.write("  1. Run: pytest eval/test_eval.py -v -s\n")
            f.write("  2. Look for the table showing:\n")
            f.write("     - eval_status (PASSED/FAILED)\n")
            f.write("     - score values\n")
            f.write("     - prompt (test query)\n")
            f.write("     - expected_response\n")
            f.write("     - actual_response (agent's actual response)\n")
            f.write("     - expected_tool_calls\n")
            f.write("     - actual_tool_calls\n\n")
            if eval_results["metrics"]:
                f.write("Extracted Metrics:\n")
                for metric, value in eval_results["metrics"].items():
                    f.write(f"  {metric}: {value}\n")
            f.write("\n")
            f.write("Test Execution Log (Environment Setup and Tool Execution):\n")
            f.write("-" * 80 + "\n")
            f.write(evaluation_output)
            f.write("\n\n")
            f.write("="*80 + "\n")
            if eval_results["status"] == "PASSED":
                f.write("[OK] Test PASSED - Agent responds correctly to basic queries\n")
            else:
                f.write("[FAIL] Test FAILED - See details above\n")
            f.write("="*80 + "\n")

        print(f"\n[OK] Test results saved to:")
        print(f"  - JSON: {result_file}")
        print(f"  - Summary: {summary_file}")
        print("="*80 + "\n")

    except Exception as e:
        # Save error details
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = os.path.join(results_dir, f"simple_test_{timestamp}_ERROR.txt")

        with open(error_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("Simple Evaluation Test - ERROR\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write("Traceback:\n")
            f.write("-" * 80 + "\n")
            import traceback
            f.write(traceback.format_exc())

        print(f"\n[FAIL] Test failed. Error details saved to: {error_file}")
        raise
