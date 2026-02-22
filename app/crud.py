from sqlalchemy.orm import Session

from app import models
from app.config import auction_is_open
from app.schemas import BidCreate
from dotenv import load_dotenv
import os


load_dotenv()

MIN_BID_INCREMENT = os.getenv("MIN_BID_INCREMENT", 5.00)


def get_all_items(db: Session) -> list[models.Item]:
    return db.query(models.Item).all()


def get_item(db: Session, item_id: int) -> models.Item | None:
    return db.query(models.Item).filter(models.Item.id == item_id).first()  # type: ignore[return-value]


def place_bid(db: Session, item_id: int, bid_in: BidCreate) -> tuple[models.Bid | None, str | None]:
    """
    Attempt to place a bid. Returns (bid, error_message).
    Uses with_for_update() to prevent race conditions.
    """
    if not auction_is_open():
        return None, "The auction has closed. No further bids are accepted."

    item = (
        db.query(models.Item)
        .filter(models.Item.id == item_id)
        .with_for_update()
        .first()
    )

    if not item:
        return None, "Item not found."

    min_required = round(item.current_bid + MIN_BID_INCREMENT, 2)
    if bid_in.amount < min_required:
        return None, (
            f"Bid must be at least ${min_required:.2f} "
            f"(current bid ${item.current_bid:.2f} + ${MIN_BID_INCREMENT:.2f} minimum increment)."
        )

    bid = models.Bid(item_id=item_id, amount=bid_in.amount, contact=bid_in.contact)
    item.current_bid = bid_in.amount

    db.add(bid)
    db.commit()
    db.refresh(bid)
    db.refresh(item)

    return bid, None