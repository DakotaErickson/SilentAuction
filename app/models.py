from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    starting_bid: Mapped[float] = mapped_column(Float, nullable=False)
    current_bid: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="item", order_by="Bid.id.desc()")


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    contact: Mapped[str] = mapped_column(String, nullable=False)  # email or phone

    item: Mapped["Item"] = relationship("Item", back_populates="bids")