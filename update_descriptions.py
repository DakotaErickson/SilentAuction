"""
Run once to update item descriptions:
    python update_descriptions.py
"""

from app.database import SessionLocal
from app import models

# Map item ID -> new description. Only listed items will be changed.
DESCRIPTION_UPDATES = {
    2: "Birthday party at Bricks & Minifigs (M-TH), small horizontal banner from Brush and Banner Co, birthday cake from Carrie Bakes Cakes",
    14: "August 18th to October 14th. Designated spot to drop off/pick up your student(s) by the office",
    15: "October 19th to December 22nd. Designated spot to drop off/pick up your student(s) by the office",
    16: "January 6th to March 12th. Designated spot to drop off/pick up your student(s) by the office",
    17: "March 22nd to May 21st. Designated spot to drop off/pick up your student(s) by the office"
}

# Map item ID -> new name. Only listed items will be changed.
NAME_UPDATES = {
    14: "Parent Pick Up/Drop off Reserved Spot: Quarter 1 2026",
    15: "Parent Pick Up/Drop off Reserved Spot: Quarter 2 2026",
    16: "Parent Pick Up/Drop off Reserved Spot: Quarter 3 2027",
    17: "Parent Pick Up/Drop off Reserved Spot: Quarter 4 2027"
}


def update() -> None:
    db = SessionLocal()

    for item_id, new_description in DESCRIPTION_UPDATES.items():
        item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item:
            print(f"WARNING: Item {item_id} not found, skipping.")
            continue
        print(f"Updating item {item_id} '{item.name}'")
        item.description = new_description

    db.commit()
    print(f"Updated {len(DESCRIPTION_UPDATES)} item descriptions.")

    for item_id, new_name in NAME_UPDATES.items():
        item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item:
            print(f"WARNING: Item {item_id} not found, skipping.")
            continue
        print(f"Updating item {item_id} '{item.name}'")
        item.name = new_name

    db.commit()
    db.close()
    print(f"Updated {len(NAME_UPDATES)} item names.")


if __name__ == "__main__":
    update()