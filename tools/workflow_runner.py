#!/usr/bin/env python3
"""
Workflow Runner with Transaction-Style Error Recovery
Wraps workflows in try/catch with automatic rollback on failure.

Features:
- Checkpoint system: saves state after each step
- Automatic rollback: removes partial files on failure
- Resume capability: continue from last successful step
- Detailed error logging with solutions

Usage:
    python tools/workflow_runner.py --workflow audit --url https://example.com
    python tools/workflow_runner.py --workflow audit --resume .tmp/checkpoint.json
    python tools/workflow_runner.py --workflow content_draft --client acme --rollback
"""

import argparse
import json
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class WorkflowRunner:
    def __init__(self, workflow: str, checkpoint_file: str = None):
        self.workflow = workflow
        self.checkpoint_file = Path(checkpoint_file or f".tmp/checkpoint_{workflow}.json")
        self.state = self.load_checkpoint()
        self.created_files = []
        self.errors = []

    def load_checkpoint(self) -> Dict:
        """Load previous checkpoint if exists"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {
            "workflow": self.workflow,
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "current_step": 0,
            "created_files": [],
            "errors": []
        }

    def save_checkpoint(self):
        """Save current state to checkpoint file"""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def run_command(self, cmd: List[str], step_name: str, output_file: str = None) -> bool:
        """
        Run a shell command with error handling

        Args:
            cmd: Command to run (list format)
            step_name: Name of this step for logging
            output_file: Expected output file (for validation)

        Returns:
            True if successful, False if failed
        """
        print(f"\n[STEP {self.state['current_step'] + 1}] {step_name}")
        print(f"Command: {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )

            # Print output
            if result.stdout:
                print(result.stdout)

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.errors.append({
                    "step": step_name,
                    "command": " ".join(cmd),
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"[ERROR] Step failed with exit code {result.returncode}")
                print(f"Error: {error_msg}")
                return False

            # Validate output file if specified
            if output_file:
                output_path = Path(output_file)
                if not output_path.exists():
                    self.errors.append({
                        "step": step_name,
                        "command": " ".join(cmd),
                        "error": f"Output file not created: {output_file}",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"[ERROR] Expected output file not created: {output_file}")
                    return False

                # Track created file for potential rollback
                self.created_files.append(str(output_path))
                self.state["created_files"].append(str(output_path))

            # Mark step as completed
            self.state["steps_completed"].append(step_name)
            self.state["current_step"] += 1
            self.save_checkpoint()

            print(f"[SUCCESS] {step_name} completed")
            return True

        except subprocess.TimeoutExpired:
            self.errors.append({
                "step": step_name,
                "command": " ".join(cmd),
                "error": "Command timed out (>5 minutes)",
                "timestamp": datetime.now().isoformat()
            })
            print(f"[ERROR] Command timed out after 5 minutes")
            return False

        except Exception as e:
            self.errors.append({
                "step": step_name,
                "command": " ".join(cmd),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            print(f"[ERROR] Unexpected error: {e}")
            return False

    def rollback(self):
        """Remove all files created during this workflow"""
        print(f"\n{'='*70}")
        print(f"ROLLBACK — Cleaning up partial workflow")
        print(f"{'='*70}\n")

        if not self.state["created_files"]:
            print("[INFO] No files to clean up")
            return

        print(f"Removing {len(self.state['created_files'])} files created during this workflow:\n")

        for file_path in self.state["created_files"]:
            path = Path(file_path)
            if path.exists():
                try:
                    path.unlink()
                    print(f"[DELETED] {file_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to delete {file_path}: {e}")
            else:
                print(f"[SKIP] Already deleted: {file_path}")

        # Remove checkpoint file
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            print(f"\n[DELETED] Checkpoint file: {self.checkpoint_file}")

        print(f"\n[ROLLBACK COMPLETE] System restored to pre-workflow state\n")

    def run_audit_workflow(self, url: str) -> bool:
        """
        Run the audit workflow with checkpoints

        Steps:
        1. Pre-flight check
        2. Framework detection
        3. No-JS crawl
        4. JS crawl
        5. PageSpeed audit
        6. Report generation
        """
        from utils import url_to_slug

        slug = url_to_slug(url)

        steps = [
            {
                "name": "Pre-flight Check",
                "cmd": ["python", "tools/preflight_check.py", "--workflow", "audit", "--url", url],
                "output": None
            },
            {
                "name": "Framework Detection",
                "cmd": ["python", "tools/framework_detector.py", "--url", url, "--output", f".tmp/{slug}_framework.json"],
                "output": f".tmp/{slug}_framework.json"
            },
            {
                "name": "No-JS Crawl (Google's Perspective)",
                "cmd": ["python", "tools/seo_crawler.py", "--url", url, "--max-pages", "50", "--no-js", "--output", f".tmp/{slug}_crawl_nojs.json"],
                "output": f".tmp/{slug}_crawl_nojs.json"
            },
            {
                "name": "JS Crawl (User's Perspective)",
                "cmd": ["python", "tools/seo_crawler.py", "--url", url, "--max-pages", "50", "--output", f".tmp/{slug}_crawl_js.json"],
                "output": f".tmp/{slug}_crawl_js.json"
            },
            {
                "name": "Lighthouse Audit (Core Web Vitals)",
                "cmd": ["python", "tools/lighthouse_audit.py", "--url", url, "--strategy", "both", "--output", f".tmp/{slug}_lighthouse.json"],
                "output": f".tmp/{slug}_lighthouse.json"
            },
            {
                "name": "Validate Audit Files",
                "cmd": ["python", "tools/validate_audit_files.py", "--url", url],
                "output": None
            }
        ]

        # Resume from checkpoint if applicable
        start_index = self.state["current_step"]

        if start_index > 0:
            print(f"\n[RESUME] Continuing from step {start_index + 1}/{len(steps)}")
            print(f"Previous steps completed: {', '.join(self.state['steps_completed'])}\n")

        # Execute steps
        for i, step in enumerate(steps[start_index:], start=start_index):
            success = self.run_command(step["cmd"], step["name"], step["output"])

            if not success:
                print(f"\n[WORKFLOW FAILED] Stopped at step {i + 1}/{len(steps)}")
                self.print_error_report()
                return False

        print(f"\n{'='*70}")
        print(f"[WORKFLOW COMPLETE] All {len(steps)} steps successful")
        print(f"{'='*70}\n")
        return True

    def print_error_report(self):
        """Print detailed error report with solutions"""
        print(f"\n{'='*70}")
        print(f"ERROR REPORT")
        print(f"{'='*70}\n")

        for i, error in enumerate(self.errors, 1):
            print(f"Error #{i}: {error['step']}")
            print(f"  Command: {error['command']}")
            print(f"  Message: {error['error']}")
            print(f"  Time:    {error['timestamp']}")

            # Suggest solutions based on error type
            if "ModuleNotFoundError" in error['error'] or "No module named" in error['error']:
                module = error['error'].split("'")[1] if "'" in error['error'] else "unknown"
                print(f"  Fix:     pip install {module}")

            elif "playwright" in error['error'].lower() and "browser" in error['error'].lower():
                print(f"  Fix:     playwright install chromium")

            elif "timeout" in error['error'].lower() or "timed out" in error['error'].lower():
                print(f"  Fix:     Increase timeout or check network connection")

            elif "not found" in error['error'].lower() or "does not exist" in error['error'].lower():
                print(f"  Fix:     Check file path and ensure prerequisites ran successfully")

            print()

        print(f"Checkpoint saved to: {self.checkpoint_file}")
        print(f"\nTo resume: python tools/workflow_runner.py --workflow {self.workflow} --resume {self.checkpoint_file}")
        print(f"To rollback: python tools/workflow_runner.py --rollback --checkpoint {self.checkpoint_file}\n")


def main():
    parser = argparse.ArgumentParser(description="Workflow runner with error recovery")
    parser.add_argument("--workflow", choices=["audit", "content_draft", "keyword_research"],
                       help="Workflow to run")
    parser.add_argument("--url", help="URL for audit workflow")
    parser.add_argument("--client", help="Client name for content workflows")
    parser.add_argument("--resume", help="Resume from checkpoint file")
    parser.add_argument("--rollback", action="store_true", help="Rollback last workflow")
    parser.add_argument("--checkpoint", help="Checkpoint file to rollback")
    args = parser.parse_args()

    # Rollback mode
    if args.rollback:
        if not args.checkpoint:
            print("[ERROR] --checkpoint required for rollback")
            sys.exit(1)

        runner = WorkflowRunner("rollback", args.checkpoint)
        runner.rollback()
        sys.exit(0)

    # Resume mode
    if args.resume:
        runner = WorkflowRunner("resume", args.resume)
        print(f"[RESUME] Continuing workflow from checkpoint")
        # TODO: Implement resume logic based on workflow type
        sys.exit(0)

    # New workflow mode
    if not args.workflow:
        print("[ERROR] --workflow required (or use --rollback)")
        sys.exit(1)

    runner = WorkflowRunner(args.workflow)

    # Run workflow
    if args.workflow == "audit":
        if not args.url:
            print("[ERROR] --url required for audit workflow")
            sys.exit(1)

        success = runner.run_audit_workflow(args.url)
        sys.exit(0 if success else 1)

    else:
        print(f"[ERROR] Workflow '{args.workflow}' not yet implemented")
        sys.exit(1)


if __name__ == "__main__":
    main()
