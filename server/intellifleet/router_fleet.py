"""Fleet control endpoints – halt and resume robots.

These endpoints mutate the in‑memory robot state directly. The safety and
executor agents will later enforce additional checks, but for the basic UI we
need simple state changes.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..domain import state

router = APIRouter(prefix="/api/fleet", tags=["Fleet"])

@router.post("/robots/{robot_id}/halt", summary="Halt a robot")
async def halt_robot(robot_id: str):
    robot = state.global_state.robots.get(robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    robot.status = "halted"
    robot.last_updated = datetime.utcnow()
    return {"status": "halted", "robotId": robot_id}

@router.post("/robots/{robot_id}/resume", summary="Resume a halted robot")
async def resume_robot(robot_id: str):
    robot = state.global_state.robots.get(robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    # When resuming we revert to idle (or keep previous if known). Simplify to idle.
    robot.status = "idle"
    robot.last_updated = datetime.utcnow()
    return {"status": "idle", "robotId": robot_id}

# End of fleet router
