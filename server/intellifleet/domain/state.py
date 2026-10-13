"""In‑memory state holder for IntelliFleet.

The state is a singleton instance that lives for the duration of the
process. All FastAPI routers and agents import the same ``global_state``
object so they share a consistent view.
"""

from __future__ import annotations

import itertools
import threading
from collections import deque
from datetime import datetime
from typing import Dict, List, Deque

from .models import (
    Robot,
    Zone,
    Task,
    Alert,
    WorkOrder,
    InventoryItem,
    SalesOrder,
)

# ---------------------------------------------------------------------------
# Telemetry record
# ---------------------------------------------------------------------------
class TelemetryRecord:
    def __init__(self, robot_id: str, battery_soc: float, temperature_c: float, pose_x: float, pose_y: float, timestamp: datetime | None = None):
        self.robot_id = robot_id
        self.battery_soc = battery_soc
        self.temperature_c = temperature_c
        self.pose_x = pose_x
        self.pose_y = pose_y
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        return {
            "robot_id": self.robot_id,
            "battery_soc": self.battery_soc,
            "temperature_c": self.temperature_c,
            "pose_x": self.pose_x,
            "pose_y": self.pose_y,
            "timestamp": self.timestamp.isoformat(),
        }

# ---------------------------------------------------------------------------
# Global state singleton
# ---------------------------------------------------------------------------
class _GlobalState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # thread‑safe singleton creation
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # The ``__init__`` may be called many times but we only initialise once.
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # Core collections – keyed by their IDs for O(1) lookup.
        self.robots: Dict[str, Robot] = {}
        self.zones: Dict[str, Zone] = {}
        self.tasks: Dict[str, Task] = {}
        self.alerts: Dict[str, Alert] = {}
        self.work_orders: Dict[str, WorkOrder] = {}
        self.inventory: Dict[str, InventoryItem] = {}
        self.sales_orders: Dict[str, SalesOrder] = {}

        # Telemetry ring buffers – one per robot, capped at 1 000 entries.
        self.telemetry: Dict[str, Deque[TelemetryRecord]] = {}

        # Simple counters used for generating stable IDs when needed.
        self._alert_counter = itertools.count(1)
        self._wo_counter = itertools.count(1)
        self._task_counter = itertools.count(1)

    # ---------------------------------------------------------------------
    # Helper methods for telemetry
    # ---------------------------------------------------------------------
    def get_telemetry_window(self, robot_id: str, max_records: int = 1000) -> List[dict]:
        """Return the most recent telemetry records for ``robot_id`` as a list of dicts.
        The underlying deque is capped at 1 000 entries, so we never grow unbounded.
        """
        buf = self.telemetry.get(robot_id, deque())
        # Return a shallow copy to avoid callers mutating the internal buffer.
        return [rec.to_dict() for rec in list(buf)[-max_records:]]

    def _append_telemetry(self, rec: TelemetryRecord):
        buf = self.telemetry.setdefault(rec.robot_id, deque(maxlen=1000))
        buf.append(rec)

    # ---------------------------------------------------------------------
    # ID generation helpers (public API used by domain tools)
    # ---------------------------------------------------------------------
    def next_alert_id(self) -> str:
        return f"ALRT-{next(self._alert_counter):04d}"

    def next_work_order_id(self) -> str:
        return f"WO-{next(self._wo_counter):04d}"

    def next_task_id(self) -> str:
        return f"TASK-{next(self._task_counter):04d}"

    # ---------------------------------------------------------------------
    # Snapshot convenience – collate everything for the FastAPI `/snapshot`.
    # ---------------------------------------------------------------------
    def snapshot(self) -> dict:
        return {
            "robots": [r.dict() for r in self.robots.values()],
            "zones": [z.dict() for z in self.zones.values()],
            "tasks": [t.dict() for t in self.tasks.values()],
            "alerts": [a.dict() for a in self.alerts.values()],
            "workOrders": [wo.dict() for wo in self.work_orders.values()],
            "inventory": [i.dict() for i in self.inventory.values()],
            "orders": [o.dict() for o in self.sales_orders.values()],
            # Packing stations, dispatch bays, dock appointments, forecast, and VDA messages
            # are derived from zones/tasks – placeholder empty lists for now.
            "packingStations": [],
            "dispatchBays": [],
            "dockAppointments": [],
            "forecast": [],
            "vdaMessages": [],
        }

# Export a single shared instance
global_state = _GlobalState()

# End of state module

