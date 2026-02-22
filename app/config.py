import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AUCTION_END: datetime = datetime.fromisoformat(
    os.getenv("AUCTION_END_TIME", "2026-04-17T20:59:59")
)

def auction_is_open() -> bool:
    return datetime.now() < AUCTION_END