# main.py

from users import authenticate
from admin import admin_menu
from trainer import trainer_menu
from employee import employee_menu


def main():
    print("Welcome to the Automated Question Builder CLI Application!")
    user = authenticate()
    if not user:
        return
    role = user['role']
    username = user['username']
    if role == 'admin':
        admin_menu()
    elif role == 'trainer':
        trainer_menu(username)
    elif role == 'employee':
        employee_menu(username)
    else:
        print("Invalid user role.")

if __name__ == "__main__":
    main()