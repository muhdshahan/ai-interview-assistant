""" Entry point """

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, interview, stt
from backend.db.database import engine, Base

app = FastAPI(title="AI Interview Platform")

# CORS middleware
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8501",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers8
app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(stt.router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # create all tables from imported models
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview API"}

