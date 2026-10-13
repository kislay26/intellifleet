"""FastAPI entry point for the IntelliFleet backend.

The app imports the global in‑memory state, seeds initial data on startup, and
exposes the minimal set of endpoints required by the specification (health and
snapshot). Additional routers will be added later.
"""

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from .domain import seed, state

app = FastAPI(title="IntelliFleet", version="0.1.0")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
health_router = APIRouter()

@health_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

app.include_router(health_router)

# ---------------------------------------------------------------------------
# Snapshot endpoint – aggregates the whole system state for the UI.
# ---------------------------------------------------------------------------
snapshot_router = APIRouter(prefix="/api")

@snapshot_router.get("/snapshot", tags=["Snapshot"])
async def get_snapshot():
    # The domain.state.snapshot() returns a dict that is JSON‑serialisable.
    return JSONResponse(content=state.global_state.snapshot())

app.include_router(snapshot_router)

# ---------------------------------------------------------------------------
# Startup / shutdown hooks
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    # Populate the in‑memory store before the server begins handling requests.
    seed.seed_all()
    from .simulation import start_background_tick
    start_background_tick()
    from .router_fleet import router as fleet_router
    app.include_router(fleet_router)

@app.on_event("shutdown")
async def on_shutdown():
    # Currently nothing to clean up; placeholder for future resources.
    pass

# End of main.py

