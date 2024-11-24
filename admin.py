# admin.py
import os
from users import add_user, remove_user, update_user
# admin.py

from users import add_user, remove_user, update_user
from issues import load_issues

def view_issues():
    print("\nList of Raised Issues:")
    issues = load_issues()
    if not issues:
        print("No issues have been reported.")
        return
    for idx, issue in enumerate(issues, start=1):
        print(f"\nIssue {idx}:")
        print(f"Raised by: {issue['raised_by']}")
        print(f"Timestamp: {issue['timestamp']}")
        print(f"Subject: {issue['subject']}")
        print(f"Description: {issue['description']}")

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Add User")
        print("2. Remove User")
        print("3. Update User")
        print("4. View Issues")
        print("5. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter new username: ")
            password = input("Enter password: ")
            role = input("Enter role (admin/trainer/employee): ").lower()
            if role not in ['admin', 'trainer', 'employee']:
                print("Invalid role.")
                continue
            add_user(username, password, role)
        elif choice == '2':
            username = input("Enter username to remove: ")
            remove_user(username)
        elif choice == '3':
            username = input("Enter username to update: ")
            password = input("Enter new password (leave blank to keep current): ")
            role = input("Enter new role (admin/trainer/employee, leave blank to keep current): ").lower()
            if role == '':
                role = None
            elif role not in ['admin', 'trainer', 'employee']:
                print("Invalid role.")
                continue
            if password == '':
                password = None
            update_user(username, password, role)
        elif choice == '4':
            view_issues()
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select from the menu options.")