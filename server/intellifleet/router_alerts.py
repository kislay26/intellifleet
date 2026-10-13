"""Alert router – list alerts and acknowledge.

The UI expects:
* GET /api/alerts – list all open alerts (already part of snapshot but a dedicated endpoint is handy)
* POST /api/alerts/{alert_id}/ack – mark an alert as acknowledged.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..domain import state

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", summary="List all alerts")
async def list_alerts():
    return list(state.global_state.alerts.values())

@router.post("/{alert_id}/ack", summary="Acknowledge an alert")
async def ack_alert(alert_id: str):
    alert = state.global_state.alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "acknowledged"
    alert.last_updated = datetime.utcnow()
    return {"status": "acknowledged", "alertId": alert_id}

# End of alerts router

