import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud, models
from app.config import auction_is_open, AUCTION_END
from app.database import Base, engine, get_db
from app.schemas import AuctionResults, BidCreate, BidResult, ItemResponse, ItemResult, WinnerInfo
from app.ws_manager import manager


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Silent Auction",
    description="Real-time silent auction backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend() -> HTMLResponse:
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/auction/status")
def auction_status() -> dict:
    """Returns whether the auction is currently open and when it ends."""
    return {
        "is_open": auction_is_open(),
        "ends_at": AUCTION_END.isoformat(),
    }


@app.get("/items", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)) -> list[models.Item]:
    """Return all auction items with their current bids."""
    return crud.get_all_items(db)


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)) -> models.Item:
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return item


@app.post("/items/{item_id}/bid", response_model=BidResult, status_code=status.HTTP_201_CREATED)
async def place_bid(
    item_id: int,
    bid_in: BidCreate,
    db: Session = Depends(get_db),
) -> BidResult:
    """Place a bid on an item. Broadcasts updated price to all WebSocket clients."""
    bid, error = crud.place_bid(db, item_id, bid_in)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    item = crud.get_item(db, item_id)
    assert item is not None  # guaranteed: bid succeeded so item exists

    result = BidResult(
        item_id=item.id,
        item_name=item.name,
        current_bid=item.current_bid,
        bid_id=bid.id,
    )

    await manager.broadcast(result.model_dump())

    return result



@app.get("/admin/results", response_model=AuctionResults)
def admin_results(token: str, db: Session = Depends(get_db)) -> AuctionResults:
    """
    Returns full auction results including winner and bid history for every item.
    Protected by ADMIN_TOKEN environment variable.
    Access via: /admin/results?token=your_secret_token
    """
    if token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

    items = crud.get_auction_results(db)

    results: list[ItemResult] = []
    for item in items:
        # bids are ordered descending by id, so first is the winning bid
        winning_bid = item.bids[0] if item.bids else None
        winner = WinnerInfo(amount=winning_bid.amount, contact=winning_bid.contact) if winning_bid else None

        results.append(ItemResult(
            id=item.id,
            name=item.name,
            description=item.description,
            starting_bid=item.starting_bid,
            final_bid=item.current_bid,
            total_bids=len(item.bids),
            winner=winner,
            bid_history=item.bids,
        ))

    items_with_bids = sum(1 for r in results if r.total_bids > 0)

    return AuctionResults(
        total_items=len(results),
        items_with_bids=items_with_bids,
        items_without_bids=len(results) - items_with_bids,
        results=results,
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; we only push from server
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)