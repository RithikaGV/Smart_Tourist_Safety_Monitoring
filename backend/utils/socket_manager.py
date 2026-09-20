"""
utils/socket_manager.py
A single shared python-socketio AsyncServer instance. python-socketio speaks
the same wire protocol as Node's socket.io, so the existing frontend
(socket.io-client, e.g. frontend-integration/LiveMap.jsx) does not need to
change to talk to this Python backend.

Rooms:
  - "admin-room"      -> joined by any admin Command Center connection
  - f"user-{user_id}" -> joined by that user's own device(s), and by any
                          admin who calls admin:watch-user for that user
"""
import os
import socketio

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=os.getenv("CLIENT_ORIGIN", "*"),
)


@sio.event
async def connect(sid, environ, auth):
    auth = auth or {}
    user_id = auth.get("userId")
    role = auth.get("role")

    if role == "admin":
        await sio.enter_room(sid, "admin-room")
    elif user_id:
        await sio.enter_room(sid, f"user-{user_id}")

    print(f"[socket] connected sid={sid} role={role} userId={user_id}")


@sio.event
async def disconnect(sid):
    print(f"[socket] disconnected sid={sid}")


@sio.on("admin:watch-user")
async def admin_watch_user(sid, target_user_id):
    await sio.enter_room(sid, f"user-{target_user_id}")


@sio.on("location:push")
async def location_push(sid, data):
    # Imported here (not at module load) to avoid a circular import between
    # socket_manager and the controller that also emits via `sio`.
    from controllers.location_controller import ingest_location_ping

    try:
        result = await ingest_location_ping(
            user_id=data.get("userId"),
            trip_id=data.get("tripId"),
            lat=data["lat"],
            lng=data["lng"],
            speed_kmh=data.get("speedKmh"),
            heading=data.get("heading"),
            accuracy_meters=data.get("accuracyMeters"),
            battery_level=data.get("batteryLevel"),
            is_offline=data.get("isOffline", False),
        )
        return {"success": True, "incident": result.get("incident")}
    except Exception as err:
        print(f"[socket] location:push failed: {err}")
        return {"success": False, "message": str(err)}
