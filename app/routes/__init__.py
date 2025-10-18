from app.routes.send_email import router as sender_router
from app.routes.rc import router as rc_router

__all__ = [
    "sender_router",
    "rc_router"
]