import subprocess
import os

OUTPUT_DIR = "data/output"
SCRAPED_DIR = os.path.join(OUTPUT_DIR, "scraped")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
BEARER_REPORT_FILE = os.path.join(REPORTS_DIR, "report-bearer.html")

os.makedirs(SCRAPED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def initialize_git_repo(scraped_dir):
    git_dir = os.path.join(scraped_dir, ".git")

    if os.path.exists(git_dir):
        subprocess.run(["rm", "-rf", git_dir], check=True)

    subprocess.run(["git", "init", scraped_dir], check=True)
    print(f"Initialized new Git repository in {scraped_dir}")

    subprocess.run(["git", "-C", scraped_dir, "add", "."], check=True)
    print("Added all files to the Git repository.")

    commit_message = "31337"
    subprocess.run(["git", "-C", scraped_dir, "commit", "-m", commit_message], check=True)
    print("Committed all changes to the Git repository.")

def run_bearer_scan():
    initialize_git_repo(SCRAPED_DIR)
    
    try:
        subprocess.run(
            ["bin/bearer", "scan", SCRAPED_DIR,  "-f", "html", "--output", BEARER_REPORT_FILE], 
            stderr=subprocess.STDOUT, 
            check=True, 
        )
        print(f"Bearer scan completed. Report saved to {BEARER_REPORT_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"{e}")
