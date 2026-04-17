import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AUCTION_END: datetime = datetime.fromisoformat(
    os.getenv("AUCTION_END_TIME", "2026-04-20T19:59:59")
)

def auction_is_open() -> bool:
    return datetime.fromisoformat("2026-04-13T07:59:59") < datetime.now() < AUCTION_END