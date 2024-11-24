# employee.py
import json
import os
from issues import add_issue
from Learning_plan import generate_learning_plan

QUESTION_BANK_DIR = 'data/question_banks/'
QB_DETAILS_FILE = 'data/question_banks_details.json'
all_question_bank_details_path=r"C:\Users\2000108450\OneDrive - Hexaware Technologies\Desktop\AutomatedQuestionBuilder\data\question_banks_details.json"
all_learning_plan_details_path=r"C:\Users\2000108450\OneDrive - Hexaware Technologies\Desktop\AutomatedQuestionBuilder\data\learning_question_bank.json"



def view_question_banks():
    print("\nAvailable Question Banks:")
    if not os.path.exists(QB_DETAILS_FILE):
        print("No question banks available.")
        return
    try:
        with open(QB_DETAILS_FILE, 'r') as f:
            qb_details = json.load(f)
        if not qb_details:
            print("No question banks available.")
            return
        print("\nAvailable Topics:")
        for idx, qb in enumerate(qb_details, start=1):
            print(f"{idx}. {qb['topic']}")
        choice = input("Enter the number of the topic to download or '0' to cancel: ")
        try:
            choice = int(choice)
            if choice == 0:
                return
            selected_qb = qb_details[choice - 1]
            print(f"You have selected: {selected_qb['topic']}")
            file_path = selected_qb['file_path']
            if not os.path.exists(file_path):
                print("The selected question bank file does not exist.")
                return
            print("Downloading...")
            # For simulation, we'll just print the content
            with open(file_path, 'r') as f:
                content = f.read()
                print(f"\nContent of {selected_qb['topic']} Question Bank:\n")
                print(content)
                print("\nDownload complete.")
        except (ValueError, IndexError):
            print("Invalid selection.")
    except Exception as e:
        print(f"An error occurred while accessing question banks: {e}")


def display_learning_plan(plan):
    print("\n--- User Profile ---")
    user_profile = plan.get('User_Profile', {})
    print(f"Primary Focus: {user_profile.get('Primary_Focus', 'N/A')}")
    print(f"Skill Level: {user_profile.get('Skill_Level', 'N/A')}")
    print(f"Learning Style: {user_profile.get('Learning_Style', 'N/A')}")
    print(f"Areas of Improvement: {', '.join(user_profile.get('Areas_of_improvement', []))}")
    print(f"Learning Goals: {', '.join(user_profile.get('Learning_goals', []))}")

    print("\n--- Learning Plan ---")
    learning_plan = plan.get('Learning_Plan', [])
    for idx, item in enumerate(learning_plan, start=1):
        print(f"\nModule {idx}: {item.get('File_Name', 'N/A')}")
        print(f"  Topics Covered: {', '.join(item.get('Topics_Covered', []))}")
        print(f"  Estimated Time: {item.get('Estimated_Time', 'N/A')}")
        print(f"  Difficulty: {item.get('Difficulty', 'N/A')}")

    print("\n--- Question Banks ---")
    question_banks = plan.get('Question_Banks', [])
    for idx, qb in enumerate(question_banks, start=1):
        print(f"\nQuestion Bank {idx}: {qb.get('File_Name', 'N/A')}")
        print(f"  Topics Covered: {', '.join(qb.get('Topics_Covered', []))}")
        print(f"  Difficulty: {qb.get('Difficulty', 'N/A')}")

    print("\n--- Timeline ---")
    timeline = plan.get('Timeline', [])
    for entry in timeline:
        print(f"\nWeek {entry.get('Week', 'N/A')}")
        print(f"  Focus: {entry.get('Focus', 'N/A')}")
        print(f"  Milestone: {entry.get('Milestone', 'N/A')}")

    print("\n--- Recommendations ---")
    recommendations = plan.get('Recommendations', [])
    for idx, rec in enumerate(recommendations, start=1):
        print(f"\nRecommendation {idx}:")
        print(f"  Type: {rec.get('Type', 'N/A')}")
        print(f"  Description: {rec.get('Description', 'N/A')}")
        benefits = rec.get('Benefits', [])
        print(f"  Benefits: {', '.join(benefits)}")



def learning_plan_generator():
    print("\nLearning Plan Generator")
    primary_focus = input("Enter your primary focus area: ")
    skill_level = input("Enter your skill level (beginner/intermediate/advanced): ").lower()
    learning_style = input("Enter your preferred learning style (e.g., project-based, theoretical): ")
    areas_of_improvement = input("Enter areas of improvement: ")
    learning_goals = input("Enter your learning goals: ")

    user_request = {
        "Primary_Focus": primary_focus,
        "Skill_Level": skill_level,
        "Learning_Style": learning_style,
        "Areas of improvement": areas_of_improvement,
        "learning goals": learning_goals
    }

    if os.path.exists(all_question_bank_details_path) and os.path.getsize(all_question_bank_details_path) > 0:
        with open(all_question_bank_details_path, 'r') as file:
            data = json.load(file)
    else:
        data=[]

    # Call the generate_learning_plan function (assumed to be implemented by you)
    response = generate_learning_plan(user_request,data)
    print("\nYour personalized learning plan has been generated successfully.")
    print("\nLearning Plan Details:")
    display_learning_plan(response)

    if os.path.exists(all_learning_plan_details_path) and os.path.getsize(all_learning_plan_details_path) > 0:
        with open(all_learning_plan_details_path, 'r') as file:
            lr_details = json.load(file)
    else:
        lr_details=[]
    lr_details.append(response)

        # Write the updated data back to the file
    with open(all_learning_plan_details_path, 'w') as file:
        json.dump(lr_details, file, indent=4)
    




def employee_menu(username):
    while True:
        print("\nEmployee Menu:")
        print("1. View and Download Question Banks")
        print("2. Learning Plan Generator")
        print("3. Raise Issue")
        print("4. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_question_banks()
        elif choice == '2':
            learning_plan_generator()
        elif choice == '3':
            add_issue(username)
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select from the menu options.")