from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud, models
from app.config import auction_is_open, AUCTION_END
from app.database import Base, engine, get_db
from app.schemas import BidCreate, BidResult, ItemResponse
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

@app.get("/auction/status")
def auction_status() -> dict:
    return {
        "is_open": auction_is_open(),
        "ends_at": AUCTION_END.isoformat(),
    }

@app.get("/", response_class=HTMLResponse)
async def serve_frontend() -> HTMLResponse:
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())


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
    print(f"bid_in: {bid_in}")
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; we only push from server
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)