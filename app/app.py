from app import rc_router, sender_router
from fastapi import FastAPI

app = FastAPI(
    title="LICA HR Email Automation"
)

app.include_router(rc_router, prefix="/generate", tags=["report-card"])
app.include_router(sender_router, prefix="/send", tags=["send-email"])

@app.get("/")
def root():
    return "Working."