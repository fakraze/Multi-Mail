from fastapi import FastAPI

from app.api.google_oauth import router as google_oauth_router

app = FastAPI()
app.include_router(google_oauth_router)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}
