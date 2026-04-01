"""
Run this once before the event to populate auction items:
    python seed.py
"""

from app.database import Base, SessionLocal, engine
from app import models

ITEMS = [
    {
        "name": "Front Row Seats Music Program: 3rd Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Fall 2026 - 3rd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 3rd Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Fall 2026 - 3rd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 4th Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Fall 2026 - 4th Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 4th Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Fall 2026 - 4th Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 1st Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Spring 2027 - 1st Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 1st Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Spring 2027 - 1st Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 2nd Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Spring 2027 - 2nd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Front Row Seats Music Program: 2nd Grade",
        "description": "Up to five (5) reserved seats in the front row at MPAAC for the Music Program Spring 2027 - 2nd Grade",
        "starting_bid": 50.00,
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 1 2026",
        "description": "August 18th to October 14th",
        "starting_bid": 50.00,
    },

    {
        "name": "Parent Pick Up Reserved Spot: Quarter 2 2026",
        "description": "October 19th to December 22nd",
        "starting_bid": 50.00,
    },
    {
        "name": "Foxy Treat at Maize City Park",
        "description": "The student's entire class will earn a trip to the new Foxi Ice Cream to enjoy an ice cream at the Maize City Park",
        "starting_bid": 50.00, # VERIFY THIS STARTING PRICE
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 3 2027",
        "description": "January 6th to March 12th",
        "starting_bid": 50.00,
    },
    {
        "name": "Parent Pick Up Reserved Spot: Quarter 4 2027",
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
        "name": "Cupcake Party #1",
        "description": "Entire class will receive a cupcake party",
        "starting_bid": 20.00,
    },
    {
        "name": "Donut Party #1",
        "description": "Entire class will receive a donut party",
        "starting_bid": 20.00,
    },
    {
        "name": "Cupcake Party #2",
        "description": "Entire class will receive a cupcake party",
        "starting_bid": 20.00,
    },
    {
        "name": "Donut Party #2",
        "description": "Entire class will receive a donut party",
        "starting_bid": 20.00,
    },
    {
        "name": "Cupcake Party #3",
        "description": "Entire class will receive a cupcake party",
        "starting_bid": 20.00,
    },
    {
        "name": "Donut Party #3",
        "description": "Entire class will receive a donut party",
        "starting_bid": 20.00,
    },
    {
        "name": "Pizza Party",
        "description": "Entire class will enjoy pizza and games at Maize City Park",
        "starting_bid": 20.00,
    },
    {
        "name": "Sonic Drink Party",
        "description": "Entire class will earn Sonic drinks delivered to them at school",
        "starting_bid": 20.00, # VERIFY THIS STARTING PRICE
    },
    {
        "name": "Lunch with Ms. Dow",
        "description": "Student will go out to lunch with Ms. Dow!",
        "starting_bid": 20.00, # VERIFY THIS STARTING PRICE
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