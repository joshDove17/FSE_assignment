from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime # SQLAlchemy object-relational mapping imports
from sqlalchemy.orm import relationship # relationship management between tables
from datetime import datetime # datetime for timestamps
from database import Base, SessionLocal # import database connection and session management
from tabulate import tabulate # table formatting

import os # for environment variable management
from twilio.rest import Client # for Twilio SMS 
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file

def send_sms(to_number, message): # function to send SMS using Twilio
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_number
        )
        print(" SMS sent successfully!")
    except Exception as e:
        print(f" Failed to send SMS: {e}")

# MODELS

class Group(Base): # group model for database
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Member(Base): # member model for database
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"))

class Contribution(Base): # contribution model for database
    __tablename__ = "contributions"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    amount = Column(Float)
    date = Column(DateTime, default=datetime.now)

class Payout(Base): # payout model for database
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    recipient = Column(String)
    amount = Column(Float)
    reason = Column(String)
    date = Column(DateTime, default=datetime.now)

class Goal(Base): # goal model for database
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    amount = Column(Float)
    deadline = Column(String)

# FUNCTIONS 

def create_group(name): # function to create a new group
    db = SessionLocal()
    if db.query(Group).filter_by(name=name).first():
        print(f"Group '{name}' already exists.")
        return
    db.add(Group(name=name))
    db.commit()
    print(f"Group '{name}' created.")

def add_member(group_name, name, role): # function to add a member to a group
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return
    existing = db.query(Member).filter_by(name=name, group_id=group.id).first()
    if existing:
        print(f"Member '{name}' already exists in group '{group_name}'.")
        return
    db.add(Member(name=name, role=role, group_id=group.id))
    db.commit()
    print(f"Member '{name}' added to group '{group_name}' as {role}.")

def record_contribution(group_name, member_name, amount): # function to record a contribution made by a member
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return
    member = db.query(Member).filter_by(name=member_name, group_id=group.id).first()
    if not member:
        print(f"Member '{member_name}' not found in group '{group_name}'.")
        return
    db.add(Contribution(member_id=member.id, amount=amount))
    db.commit()
    print(f"R{amount:.2f} contributed by '{member_name}' in '{group_name}'.")

def record_payout(group_name, recipient, amount, reason): # function to record a payout made to a member
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return
    db.add(Payout(group_id=group.id, recipient=recipient, amount=amount, reason=reason))
    db.commit()
    print(f"R{amount:.2f} payout to '{recipient}' for '{reason}' in '{group_name}'.")

def set_goal(group_name, amount, deadline): # function to set a savings goal for a group
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return
    db.add(Goal(group_id=group.id, amount=amount, deadline=deadline))
    db.commit()
    print(f"Goal of R{amount:.2f} set for group '{group_name}' by {deadline}.")

def show_summary(group_name): # function to show summary of contributions and payouts for a group
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return

    members = db.query(Member).filter_by(group_id=group.id).all()
    member_ids = [m.id for m in members]

    contributions = db.query(Contribution).filter(Contribution.member_id.in_(member_ids)).all()
    payouts = db.query(Payout).filter_by(group_id=group.id).all()

    table_c, total_contrib = [], 0 # contributions table and total
    for c in contributions:
        member = next((m for m in members if m.id == c.member_id), None)
        total_contrib += c.amount
        table_c.append((group.name, member.name if member else "Unknown", c.amount, c.date.strftime("%Y-%m-%d")))

    table_p, total_payout = [], 0 # payouts table and total
    for p in payouts:
        total_payout += p.amount
        table_p.append((group.name, p.recipient, p.amount, p.reason, p.date.strftime("%Y-%m-%d")))

    print(f"\nContributions for '{group.name}'")
    if table_c:
        print(tabulate(table_c, headers=["Group", "Member", "Amount", "Date"], tablefmt="grid"))
        print(f"Total Contributions: R{total_contrib:.2f}")
    else:
        print("   No contributions yet.")

    print(f"\nPayouts for '{group.name}'")
    if table_p:
        print(tabulate(table_p, headers=["Group", "Recipient", "Amount", "Reason", "Date"], tablefmt="grid"))
        print(f"Total Payouts: R{total_payout:.2f}")
    else:
        print("   No payouts yet.")

    balance = total_contrib - total_payout
    print(f"\nTOTAL BALANCE: R{balance:.2f}")

    formatted_text = ( # format summary text for SMS
        f"Group: {group.name}\n"
        f"Total Contributions: R{total_contrib:.2f}\n"
        f"Total Payouts: R{total_payout:.2f}\n"
        f"Balance: R{balance:.2f}"
    )
    sms = input("Would you like to send this summary via SMS? (y/n): ").lower()
    if sms == "y":
        number = input("Enter the recipient's phone number (e.g., +2783xxxxxxx): ")
        send_sms(number, formatted_text)

def list_group_members(group_name): # function to list all members of a group
    db = SessionLocal()
    group = db.query(Group).filter_by(name=group_name).first()
    if not group:
        print(f"Group '{group_name}' not found.")
        return

    members = db.query(Member).filter_by(group_id=group.id).all()
    print(f"\nMembers in '{group.name}':")
    if not members:
        print("   No members yet.")
        return

    lines = [f"   • {m.name} ({m.role})" for m in members]
    for line in lines:
        print(line)

    sms = input("Would you like to send this list via SMS? (y/n): ").lower()
    if sms == "y":
        number = input("Enter the recipient's phone number (e.g., +2783xxxxxxx): ")
        message = f"Group: {group.name}\nMembers:\n" + "\n".join(lines)
        send_sms(number, message)

# CSV export
import csv 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine # database connection 

def export_database_to_csv(): # function to export database tables to CSV files
    engine = create_engine("sqlite:///./stokvel.db")
    Session = sessionmaker(bind=engine)
    db = Session()

    tables = {
        "groups": db.query(Group).all(),
        "members": db.query(Member).all(),
        "contributions": db.query(Contribution).all(),
        "payouts": db.query(Payout).all(),
        "goals": db.query(Goal).all()
    }

    for table_name, records in tables.items():
        if not records:
            continue

        with open(f"{table_name}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            headers = records[0].__table__.columns.keys()
            writer.writerow(headers)

            for record in records:
                row = [getattr(record, column) for column in headers]
                writer.writerow(row)

    print(" Database exported to CSV files.")