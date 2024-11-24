# employee.py

import os
from issues import add_issue

QUESTION_BANK_DIR = 'data/question_banks/'

def view_question_banks():
    print("\nAvailable Question Banks:")
    if not os.path.exists(QUESTION_BANK_DIR):
        print("No question banks available.")
        return
    files = os.listdir(QUESTION_BANK_DIR)
    if not files:
        print("No question banks available.")
        return
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")
    choice = input("Enter the number of the question bank to download or '0' to cancel: ")
    try:
        choice = int(choice)
        if choice == 0:
            return
        selected_file = files[choice - 1]
        print(f"You have selected: {selected_file}")
        print("Downloading...")
        # For simulation, we'll just print the content
        with open(os.path.join(QUESTION_BANK_DIR, selected_file), 'r') as f:
            content = f.read()
            print(f"Content of {selected_file}:\n")
            print(content)
            print("\nDownload complete.")
    except (ValueError, IndexError):
        print("Invalid selection.")

def employee_menu(username):
    while True:
        print("\nEmployee Menu:")
        print("1. View and Download Question Banks")
        print("2. Raise Issue")
        print("3. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_question_banks()
        elif choice == '2':
            add_issue(username)
        elif choice == '3':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select from the menu options.")