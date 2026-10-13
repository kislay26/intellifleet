"""Domain data models for IntelliFleet.

All models are deliberately simple Pydantic BaseModel classes that mirror the
specification. They are used by the in‑memory state store and by the FastAPI
endpoints.
"""

from __future__ import annotations

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator

# ---------------------------------------------------------------------------
# Robot model
# ---------------------------------------------------------------------------
class Pose(BaseModel):
    x: float
    y: float
    theta: float = 0.0

class Robot(BaseModel):
    id: str
    vendor: str
    model: str
    maxPayloadKg: float
    pose: Pose
    battery_soc: float = Field(..., ge=0, le=100)
    sequence: int = 0
    status: Literal["idle", "in_progress", "charging", "docked", "halted"]
    eng_status: str = "OK"
    localization_status: str = "OK"
    current_task: Optional[str] = None
    reservedFor: Optional[str] = None
    temperature_c: float = 25.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @validator("battery_soc")
    def _round_battery(cls, v: float) -> float:
        # keep a single decimal place for consistency
        return round(v, 1)

# ---------------------------------------------------------------------------
# Zone model
# ---------------------------------------------------------------------------
class Zone(BaseModel):
    name: str
    position: Pose
    restrictedRoles: List[str] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# VDA‑5050 task model
# ---------------------------------------------------------------------------
class Action(BaseModel):
    type: str
    parameters: dict = Field(default_factory=dict)

class Node(BaseModel):
    nodeId: str
    position: Pose
    orientation: float = 0.0
    actions: List[Action] = Field(default_factory=list)

class Task(BaseModel):
    taskName: str
    taskId: str
    customerId: str
    mapName: str
    priority: Literal["low", "normal", "high"] = "normal"
    pickupZone: str
    dropZone: str
    status: Literal["created", "assigned", "in_progress", "completed", "failed"] = "created"
    order: dict  # raw VDA‑5050 order payload – keep as dict for flexibility

# ---------------------------------------------------------------------------
# Alert model
# ---------------------------------------------------------------------------
class Alert(BaseModel):
    alertId: str
    robotId: str
    kind: str
    severity: Literal["info", "warning", "critical"]
    status: Literal["open", "acknowledged", "resolved"] = "open"
    findings: List[str] = Field(default_factory=list)
    recommendedAction: Optional[str] = None
    predictedFailureHours: Optional[float] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------------------------
# Work order model
# ---------------------------------------------------------------------------
class WorkOrder(BaseModel):
    workOrderId: str
    robotId: str
    summary: str
    partType: str
    status: Literal["open", "in_progress", "completed", "canceled"] = "open"
    scheduledAt: Optional[datetime] = None

# ---------------------------------------------------------------------------
# Inventory model
# ---------------------------------------------------------------------------
class InventoryItem(BaseModel):
    sku: str
    item: str
    zone: str
    quantity: int

# ---------------------------------------------------------------------------
# Sales order model (warehouse order)
# ---------------------------------------------------------------------------
class OrderItem(BaseModel):
    sku: str
    quantity: int

class SalesOrder(BaseModel):
    orderId: str
    priority: Literal["normal", "high"] = "normal"
    sku: str
    quantity: int
    fromZone: str
    toZone: str
    status: Literal["open", "reserved", "fulfilled", "canceled"] = "open"
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# End of models

