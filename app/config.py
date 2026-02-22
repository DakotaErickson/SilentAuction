import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AUCTION_END: datetime = datetime.fromisoformat(
    os.getenv("AUCTION_END_TIME", "2099-01-01T00:00:00")
)

def auction_is_open() -> bool:
    return datetime.now() < AUCTION_END