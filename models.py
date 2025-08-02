from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime # database model definitions
from sqlalchemy.orm import relationship # ORM relationships
from datetime import datetime # datetime for timestamps
from database import Base, SessionLocal # import base class and session
from tabulate import tabulate # for tables

# MODELS

class Group(Base): # group model for database
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Member(Base): # member model for database
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
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
    group = Group(name=name)
    db.add(group)
    db.commit()
    print(f"Group '{name}' created.")

def add_member(group_id, name, role):
    db = SessionLocal()
    member = Member(group_id=group_id, name=name, role=role)
    db.add(member)
    db.commit()
    print(f"Member '{name}' added to group {group_id} as {role}.")

def record_contribution(member_id, amount):
    db = SessionLocal()
    contribution = Contribution(member_id=member_id, amount=amount)
    db.add(contribution)
    db.commit()
    print(f"R{amount} contribution recorded for member {member_id}.")

def record_payout(group_id, recipient, amount, reason):
    db = SessionLocal()
    payout = Payout(group_id=group_id, recipient=recipient, amount=amount, reason=reason)
    db.add(payout)
    db.commit()
    print(f"Payout of R{amount} recorded to {recipient} for '{reason}'.")

def set_goal(group_id, amount, deadline):
    db = SessionLocal()
    goal = Goal(group_id=group_id, amount=amount, deadline=deadline)
    db.add(goal)
    db.commit()
    print(f"Goal of R{amount} set for group {group_id} by {deadline}.")

def show_summary():
    db = SessionLocal()
    contributions = db.query(Contribution).all()
    payouts = db.query(Payout).all()

    print("\n--- Contributions ---")
    print(tabulate([(c.id, c.member_id, c.amount, c.date.strftime("%Y-%m-%d")) for c in contributions],
                   headers=["ID", "Member ID", "Amount", "Date"]))

    print("\n--- Payouts ---")
    print(tabulate([(p.id, p.group_id, p.recipient, p.amount, p.reason, p.date.strftime("%Y-%m-%d")) for p in payouts],
                   headers=["ID", "Group ID", "Recipient", "Amount", "Reason", "Date"]))