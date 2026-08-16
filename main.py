from fastapi import FastAPI
from app.api.recommend import router as recommend_router
from app.api.sessions import router as sessions_router
from app.engine.db_init import init_db

app = FastAPI(title="x-engine")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(recommend_router)
app.include_router(sessions_router)
