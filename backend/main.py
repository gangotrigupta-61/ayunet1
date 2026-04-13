import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import FRONTEND_URL
from routers import diagnosis, voice, calls, alerts, livekit
from services import graph as graph_service
from services import followup as followup_service


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("[AyuNet] Starting up...")

    # Wire WebSocket broadcast to followup service
    followup_service.set_ws_broadcast(alerts.broadcast_alert)

    # Warm up Neo4j
    await graph_service.warm_up()

    # Pre-cache PageRank
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, graph_service.refresh_pagerank)
        print("[AyuNet] PageRank cached")
    except Exception as e:
        print(f"[AyuNet] PageRank cache failed (will retry): {e}")


    # Schedule daily follow-up check
    scheduler.add_job(
        followup_service.check_and_trigger_followups,
        "cron",
        hour=9,
        minute=0,
        id="daily_followups",
    )

    scheduler.start()
    print("[AyuNet] Scheduler started")
    print("[AyuNet] Ready!")

    yield

    # --- Shutdown ---
    scheduler.shutdown()
    print("[AyuNet] Shut down.")


app = FastAPI(
    title="AyuNet",
    description="Graph-powered multilingual health intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagnosis.router)
app.include_router(voice.router)
app.include_router(calls.router)
app.include_router(alerts.router)
app.include_router(livekit.router)


@app.get("/")
async def root():
    return {"name": "AyuNet", "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
