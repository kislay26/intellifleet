"""Seed the in‑memory state with the initial robots, zones, inventory and sales orders.

This module is imported by the FastAPI startup event so the backend is ready
as soon as the server starts.
"""

from __future__ import annotations

from datetime import datetime
from .state import global_state
from .models import Robot, Pose, Zone, InventoryItem, SalesOrder


def seed_robots():
    robots = [
        Robot(
            id="AMR-IF-001",
            vendor="Virya",
            model="Vi-Lite",
            maxPayloadKg=250,
            pose=Pose(x=1.3, y=1.3),
            battery_soc=92.0,
            status="idle",
            eng_status="OK",
            localization_status="OK",
        ),
        Robot(
            id="AMR-IF-002",
            vendor="Virya",
            model="Vi-Pro",
            maxPayloadKg=500,
            pose=Pose(x=4.0, y=3.0),
            battery_soc=78.0,
            status="idle",
            eng_status="OK",
            localization_status="OK",
        ),
        Robot(
            id="AMR-IF-003",
            vendor="OTTO",
            model="100",
            maxPayloadKg=200,
            pose=Pose(x=12.0, y=6.0),
            battery_soc=26.4,
            status="charging",
            eng_status="OK",
            localization_status="OK",
        ),
        Robot(
            id="AMR-IF-005",
            vendor="6 River",
            model="Chuck",
            maxPayloadKg=400,
            pose=Pose(x=8.5, y=2.5),
            battery_soc=88.0,
            status="in_progress",
            eng_status="OK",
            localization_status="OK",
        ),
        Robot(
            id="AMR-IF-664",
            vendor="Locus",
            model="Origin",
            maxPayloadKg=320,
            pose=Pose(x=0.0, y=0.0),
            battery_soc=65.0,
            status="idle",
            eng_status="OK",
            localization_status="OK",
        ),
    ]
    for r in robots:
        global_state.robots[r.id] = r
        # initialise empty telemetry buffer for each robot
        global_state.telemetry[r.id] = []


def seed_zones():
    zones = [
        Zone(name="Aisle 1", position=Pose(x=1.8, y=4.5)),
        Zone(name="Aisle 2", position=Pose(x=2.8, y=5.5)),
        Zone(name="Aisle 3", position=Pose(x=3.6, y=4.0)),
        Zone(name="Pack 1", position=Pose(x=7.0, y=5.0)),
        Zone(name="Pack 2", position=Pose(x=8.0, y=4.0)),
        Zone(name="Dispatch Bay 1", position=Pose(x=12.5, y=5.5)),
        Zone(name="Dispatch Bay 2", position=Pose(x=13.0, y=6.5)),
        Zone(name="Dispatch Bay 3", position=Pose(x=13.5, y=7.5)),
        Zone(name="Charging Dock", position=Pose(x=1.3, y=1.3)),
        Zone(name="Cold Storage", position=Pose(x=11.0, y=2.5), restrictedRoles=["supervisor"]),
    ]
    for z in zones:
        global_state.zones[z.name] = z


def seed_inventory():
    items = [
        InventoryItem(sku="SKU-1001", item="Carton 12x12", zone="Aisle 1", quantity=120),
        InventoryItem(sku="SKU-1002", item="Carton 24x24", zone="Aisle 2", quantity=80),
        InventoryItem(sku="SKU-1003", item="Pallet small", zone="Aisle 3", quantity=48),
        InventoryItem(sku="SKU-1004", item="Pallet large", zone="Pack 1", quantity=15),
        InventoryItem(sku="SKU-1005", item="Cold chain box", zone="Cold Storage", quantity=25),
    ]
    for i in items:
        global_state.inventory[i.sku] = i


def seed_sales_orders():
    orders = [
        SalesOrder(
            orderId="SO-1001",
            priority="normal",
            sku="SKU-1003",
            quantity=1,
            fromZone="Aisle 3",
            toZone="Dispatch Bay 2",
        ),
        SalesOrder(
            orderId="SO-1002",
            priority="normal",
            sku="SKU-1001",
            quantity=2,
            fromZone="Aisle 1",
            toZone="Pack 1",
        ),
        SalesOrder(
            orderId="SO-1003",
            priority="high",
            sku="SKU-1004",
            quantity=1,
            fromZone="Pack 1",
            toZone="Dispatch Bay 1",
        ),
    ]
    for o in orders:
        global_state.sales_orders[o.orderId] = o


def seed_all():
    seed_robots()
    seed_zones()
    seed_inventory()
    seed_sales_orders()

# End of seed module

