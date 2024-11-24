# issues.py

import json
import os
from datetime import datetime

ISSUES_FILE = 'data/issues.json'

def load_issues():
    if not os.path.exists(ISSUES_FILE):
        return []
    with open(ISSUES_FILE, 'r') as f:
        issues = json.load(f)
    return issues

def save_issues(issues):
    with open(ISSUES_FILE, 'w') as f:
        json.dump(issues, f, indent=4)

def add_issue(username):
    print("\nRaise an Issue")
    subject = input("Subject: ")
    description = input("Description: ")
    issue = {
        'raised_by': username,
        'subject': subject,
        'description': description,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    issues = load_issues()
    issues.append(issue)
    save_issues(issues)
    print("Your issue has been recorded. Thank you!")