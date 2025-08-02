from database import init_db # import database initialization function
from models_logic import (
    create_group, add_member, record_contribution, record_payout,
    set_goal, show_summary, list_group_members, export_database_to_csv
) # import group management and expoert functions

def main_menu():
    while True:
        print("\n===== HI, WELCOME TO STOKVEL MANAGER =====")
        print("1) Create Group")
        print("2) Add Member")
        print("3) Record Contribution")
        print("4) Record Payout")
        print("5) View Summary")
        print("6) Set Savings Goal")
        print("7) List Group Members")
        print("8) EXIT") 

        choice = input("Select an option (1–8): ").strip() 

        if choice == "1": # create a new group
            group_name = input("Enter group name: ").strip()
            create_group(group_name)

        elif choice == "2": # add a member to an existing group
            group_name = input("Enter group name: ").strip()
            member_name = input("Enter member name: ").strip()
            role = input("Enter member role (Chairperson, member etc.): ").strip()
            add_member(group_name, member_name, role)

        elif choice == "3": # record a contribution made by a member
            group_name = input("Enter group name: ").strip()
            member_name = input("Who is contributing? ").strip()
            try:
                amount = float(input("How much is the contribution? R").strip())
                record_contribution(group_name, member_name, amount)
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == "4": # record a payout made to a member
            group_name = input("Enter group name: ").strip()
            recipient = input("Who is being paid? ").strip()
            try:
                amount = float(input("How much is the payout? R").strip())
                reason = input("Reason for Payout? ").strip()
                record_payout(group_name, recipient, amount, reason)
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == "5": # view summary of contributions and payouts for a group
            group_name = input("Enter the group name to view summary: ").strip()
            show_summary(group_name)

        elif choice == "6": # set a savings goal for a group
            group_name = input("Enter group name: ").strip()
            try:
                amount = float(input("Enter savings goal amount: R").strip())
                deadline = input("Enter deadline (YYYY-MM-DD): ").strip()
                set_goal(group_name, amount, deadline)
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == "7": # list all members of a group
            group_name = input("Enter the group name to view members: ").strip()
            list_group_members(group_name)

        elif choice == "8": # exit the application
            print("\n Exporting database to CSV before exiting...")
            export_database_to_csv()
            print("Goodbye, Thanks for coming!")
            break
        else:
            print("Please enter a valid option (1–8).")

if __name__ == "__main__": # main entry of the application
    print("Initializing database...")
    init_db()
    main_menu()