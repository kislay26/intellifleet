"""Background simulation loop for IntelliFleet.

The simulation runs at a fixed 1 Hz rate (once per second). It updates robot
battery levels, progresses robot poses (placeholder), records telemetry and
creates alerts when any of the defined anomaly thresholds are exceeded.
"""

import asyncio
from datetime import datetime
from typing import Dict

from .state import TelemetryRecord, global_state
from .models import Alert

# ---------------------------------------------------------------------------
# Helper – compute Euclidean distance (used later for pose advancement)
# ---------------------------------------------------------------------------
def _distance(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

# ---------------------------------------------------------------------------
# Tick implementation – runs once per second
# ---------------------------------------------------------------------------
async def _tick_once():
    for robot in list(global_state.robots.values()):
        # Preserve previous battery to detect rapid drain
        prev_battery = robot.battery_soc
        # Battery logic
        if robot.status == "in_progress":
            robot.battery_soc = max(0.0, robot.battery_soc - 0.05)
        elif robot.status == "docked":
            robot.battery_soc = min(100.0, robot.battery_soc + 0.5)
        # Update timestamp
        robot.last_updated = datetime.utcnow()
        # Record telemetry
        rec = TelemetryRecord(
            robot_id=robot.id,
            battery_soc=robot.battery_soc,
            temperature_c=robot.temperature_c,
            pose_x=robot.pose.x,
            pose_y=robot.pose.y,
        )
        global_state._append_telemetry(rec)
        # ---------------------------------------------------------------
        # Anomaly detection (per spec)
        # ---------------------------------------------------------------
        alerts: Dict[str, Alert] = global_state.alerts
        # Battery drain >6% per minute -> >0.1% per second
        if prev_battery - robot.battery_soc > 0.1:
            alert_id = global_state.next_alert_id()
            alerts[alert_id] = Alert(
                alertId=alert_id,
                robotId=robot.id,
                kind="BatteryDrain",
                severity="critical",
                status="open",
                findings=[f"Battery dropped {prev_battery - robot.battery_soc:.2f}% in 1s"],
                recommendedAction="Check charging station",
                predictedFailureHours=None,
            )
        # Temperature >44°C (motor) – we reuse robot.temperature_c as a proxy
        if robot.temperature_c > 44.0:
            alert_id = global_state.next_alert_id()
            alerts[alert_id] = Alert(
                alertId=alert_id,
                robotId=robot.id,
                kind="Overheat",
                severity="warning",
                status="open",
                findings=[f"Temperature {robot.temperature_c:.1f}°C"],
                recommendedAction="Inspect cooling system",
                predictedFailureHours=None,
            )
        # Localization error – simplified check on status field
        if robot.localization_status != "OK":
            alert_id = global_state.next_alert_id()
            alerts[alert_id] = Alert(
                alertId=alert_id,
                robotId=robot.id,
                kind="LocalizationLoss",
                severity="warning",
                status="open",
                findings=["Localization status not OK"],
                recommendedAction="Reset localization",
                predictedFailureHours=None,
            )
        # Placeholder for pose advancement – not implemented yet
        # (would normally move robot along its assigned route)

# ---------------------------------------------------------------------------
# Background task manager – start once on app startup
# ---------------------------------------------------------------------------
_background_task: asyncio.Task | None = None

def start_background_tick():
    """Spawn the 1 Hz simulation loop.

    Called once from the FastAPI ``on_event('startup')`` hook. The task runs
    forever (or until the process exits). If the task already exists it is
    ignored – this makes the function idempotent.
    """
    global _background_task
    if _background_task is None:
        _background_task = asyncio.create_task(_run_loop())

async def _run_loop():
    while True:
        await _tick_once()
        await asyncio.sleep(1)

# End of simulation.py
