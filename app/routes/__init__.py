from app.routes.send_email import router as sender_router
from app.routes.sc import router as sc_router

__all__ = [
    "sender_router",
    "sc_router"
]