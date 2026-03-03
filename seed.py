"""
Run this once before the event to populate auction items:
    python seed.py
"""

from app.database import Base, SessionLocal, engine
from app import models

ITEMS = [
    {
        "name": "Front Row Seats Music Program: 3rd Grade",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Fall - 3rd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 3rd Grade",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Fall - 3rd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 4th",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Fall - 4th Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 4th",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Fall - 4th Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 1st Grade",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Spring - 1st Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 1st Grade",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Spring - 1st Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 2nd",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Spring - 2nd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 2nd",
        "description": "Up to six (6) reserved seats in the front row at MPAAC for the Music Program next Spring - 2nd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 1",
        "description": "August 18th to October 14th",
        "starting_bid": 50.00,
    },

    {
        "name": "Parent Pick Up Reserved Spot: Quarter 2",
        "description": "October 19th to December 22nd",
        "starting_bid": 50.00,
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 3",
        "description": "January 6th to March 12th",
        "starting_bid": 50.00,
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 4",
        "description": "March 22nd to May 21st",
        "starting_bid": 50.00,
    },
    {
        "name": "Principal For A Day",
        "description": "Your student will accompany Ms. Dow throughout the day and enjoy \"Principal Duties\"",
        "starting_bid": 50.00,
    },
    {
        "name": "Class Pizza Party Bus Ride",
        "description": "The student's entire class will earn a special ride on a party bus including pizza to enjoy during the ride",
        "starting_bid": 50.00,
    },
    {
        "name": "Cupcake Party",
        "description": "Entire class will receive a cupcake party",
        "starting_bid": 20.00,
    },
    {
        "name": "Donut Party",
        "description": "Entire class will receive a donut party",
        "starting_bid": 20.00,
    },
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(models.Item).count()
    if existing > 0:
        print(f"Database already has {existing} items. Skipping seed.")
        db.close()
        return

    for item_data in ITEMS:
        item = models.Item(
            name=item_data["name"],
            description=item_data["description"],
            starting_bid=item_data["starting_bid"],
            current_bid=item_data["starting_bid"],
        )
        db.add(item)

    db.commit()
    db.close()
    print(f"Seeded {len(ITEMS)} auction items successfully.")


if __name__ == "__main__":
    seed()