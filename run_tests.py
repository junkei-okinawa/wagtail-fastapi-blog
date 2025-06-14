#!/usr/bin/env python3
"""
Simple test runner script for the Django + FastAPI blog project.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    # テスト用の環境変数を設定
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'django_project.totonoe_template.settings.test'
    
    result = subprocess.run(command, shell=True, capture_output=False, env=env)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    else:
        print(f"✅ Success: {description}")
        return True

def main():
    """Main test runner function."""
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 Django + FastAPI Blog Test Runner")
    print(f"📁 Project Directory: {project_dir}")
    
    # Install dependencies
    if not run_command("uv sync --group test", "Installing test dependencies"):
        sys.exit(1)
    
    # Check if user wants to run specific test type
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "unit":
            success = run_command("uv run pytest tests/unit/ -m unit -v", "Running unit tests")
        elif test_type == "integration":
            success = run_command("uv run pytest tests/integration/ -m integration -v", "Running integration tests")
        elif test_type == "coverage":
            success = run_command("uv run pytest --cov=fastapi_app --cov=blog --cov-report=term-missing --cov-report=html", "Running tests with coverage")
        elif test_type == "quick":
            success = run_command("uv run pytest -m 'not slow' -v", "Running quick tests")
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available options: unit, integration, coverage, quick")
            sys.exit(1)
    else:
        # Run all tests
        success = run_command("uv run pytest -v", "Running all tests")
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
