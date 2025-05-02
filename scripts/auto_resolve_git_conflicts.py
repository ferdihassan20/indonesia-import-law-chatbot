import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_unmerged_files():
    code, out, err = run_command("git diff --name-only --diff-filter=U")
    if code != 0:
        print(f"Error getting unmerged files: {err}")
        sys.exit(1)
    files = out.splitlines()

    # Check for rename/delete conflicts using git status --porcelain
    code_status, status_out, status_err = run_command("git status --porcelain")
    if code_status != 0:
        print(f"Error getting git status: {status_err}")
        sys.exit(1)
    for line in status_out.splitlines():
        # Lines starting with 'R' or 'D' indicate rename or delete conflicts
        if line.startswith('R') or line.startswith('D'):
            print("Rename/Delete conflict detected:")
            print(line)
            print("Please resolve these conflicts manually before running this script.")
            sys.exit(1)

    return files

def auto_resolve_conflicts(files):
    for f in files:
        print(f"Auto-resolving conflict in file: {f} by taking 'theirs' version")
        code, _, err = run_command(f"git checkout --theirs -- \"{f}\"")
        if code != 0:
            print(f"Failed to checkout theirs for {f}: {err}")
            print(f"Trying to checkout ours for {f}")
            code_ours, _, err_ours = run_command(f"git checkout --ours -- \"{f}\"")
            if code_ours != 0:
                print(f"Failed to checkout ours for {f}: {err_ours}")
                print(f"Skipping file {f} due to unresolved conflict.")
                continue
        code, _, err = run_command(f"git add -- \"{f}\"")
        if code != 0:
            print(f"Error adding file {f}: {err}")
            sys.exit(1)

def commit_resolution():
    # Check if there are staged changes to commit
    code, out, err = run_command("git diff --cached --name-only")
    if code != 0:
        print(f"Error checking staged changes: {err}")
        sys.exit(1)
    if not out:
        print("No changes staged for commit. Skipping commit.")
        return
    code, _, err = run_command('git commit -m "Auto-resolved merge conflicts by taking theirs"')
    if code != 0:
        print(f"Error committing merge resolution: {err}")
        sys.exit(1)
    print("Merge conflicts resolved and committed.")

def git_pull():
    print("Pulling latest changes...")
    code, out, err = run_command("git pull")
    if code != 0:
        print(f"Error pulling changes: {err}")
        sys.exit(1)
    print(out)

def main():
    files = get_unmerged_files()
    if not files:
        print("No unmerged files found. Nothing to resolve.")
        sys.exit(0)
    auto_resolve_conflicts(files)
    commit_resolution()
    git_pull()

if __name__ == "__main__":
    main()
