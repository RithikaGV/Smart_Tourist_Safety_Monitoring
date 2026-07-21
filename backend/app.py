"""
app.py
------
Entrypoint. Wires together:
  - FastAPI (REST API, mounted under /api/*)
  - python-socketio (real-time location/SOS/incident feed, protocol-compatible
    with the socket.io-client already used in frontend-integration/LiveMap.jsx)
  - MongoDB (Motor async client) -> SmartTouristDB
  - APScheduler cron (periodic AI safety score refresh)

Run with:
    uvicorn app:socket_app --reload --port 5000
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from database.db import connect_db, close_db, ensure_indexes
from middleware.error_handler import register_error_handlers
from utils.socket_manager import sio
from utils.safety_score_job import start_safety_score_job, scheduler

from routes import (
    auth_routes,
    trip_routes,
    location_routes,
    geofence_routes,
    sos_routes,
    emergency_routes,
    safety_routes,
    notification_routes,
    efir_routes,
    admin_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    await ensure_indexes()
    start_safety_score_job()
    print("[server] SafeTour Python backend ready")
    yield
    scheduler.shutdown(wait=False)
    await close_db()


app = FastAPI(title="SafeTour Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CLIENT_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/health")
async def health():
    from datetime import datetime

    return {"success": True, "status": "ok", "time": datetime.utcnow().isoformat()}


app.include_router(auth_routes.router)
app.include_router(trip_routes.router)
app.include_router(location_routes.router)
app.include_router(geofence_routes.router)
app.include_router(sos_routes.router)
app.include_router(emergency_routes.router)
app.include_router(safety_routes.router)
app.include_router(notification_routes.router)
app.include_router(efir_routes.router)
app.include_router(admin_routes.router)

# Wrap the FastAPI ASGI app with the Socket.io ASGI app so both share one
# server/port. `socket_app` (not `app`) is what uvicorn should run.
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="socket.io")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5000"))
    uvicorn.run("app:socket_app", host="0.0.0.0", port=port, reload=True)
