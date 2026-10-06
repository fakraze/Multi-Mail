from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.google_oauth import router as google_oauth_router
from app.api.mailbox import router as mailbox_router
from app.services.google_oauth import frontend_url

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[frontend_url().rstrip("/")], allow_methods=["GET"], allow_headers=["Accept"])
app.include_router(google_oauth_router)
app.include_router(mailbox_router)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}
