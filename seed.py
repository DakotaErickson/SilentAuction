"""
Run this once before the event to populate auction items:
    python seed.py
"""

from app.database import Base, SessionLocal, engine
from app import models

ITEMS = [
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 50.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 60.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 70.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 80.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 90.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 100.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 110.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 120.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 130.00,
    },
    {
        "name": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas sagittis lobortis ipsum at posuere. Sed ornare eros sed quam fermentum ultrices. Cras ut eleifend enim, in ullamcorper nibh.",
        "starting_bid": 140.00,
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