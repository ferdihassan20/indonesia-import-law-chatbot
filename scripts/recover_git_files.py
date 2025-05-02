import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def show_reflog():
    code, out, err = run_command("git reflog -n 10")
    if code != 0:
        print(f"Error getting git reflog: {err}")
        sys.exit(1)
    print("Recent git reflog entries:")
    print(out)

def reset_to_commit(commit_hash):
    print(f"Resetting to commit {commit_hash} (this will discard current changes!)")
    code, _, err = run_command(f"git reset --hard {commit_hash}")
    if code != 0:
        print(f"Error resetting to commit: {err}")
        sys.exit(1)
    print("Reset successful.")

def main():
    show_reflog()
    commit_hash = input("Enter the commit hash to reset to for recovery: ").strip()
    if not commit_hash:
        print("No commit hash entered. Exiting.")
        sys.exit(0)
    confirm = input(f"Are you sure you want to reset to {commit_hash}? This will discard current changes. (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Reset cancelled.")
        sys.exit(0)
    reset_to_commit(commit_hash)

if __name__ == "__main__":
    main()
