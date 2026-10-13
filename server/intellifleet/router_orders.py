"""Orders router – list, create, reserve inventory, and generate VDA‑5050 tasks.

Endpoints:
* GET /api/orders – list all sales orders
* POST /api/orders – create a new order (validates inventory)
* POST /api/orders/{order_id}/reserve – reserve inventory for the order
* POST /api/orders/{order_id}/fulfill – convert the order into transport tasks
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..domain import state, tools

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("", summary="List all sales orders")
async def list_orders():
    return list(state.global_state.sales_orders.values())

@router.post("", summary="Create a new sales order")
async def create_order(order: dict):
    # Expected keys: orderId, priority, sku, quantity, fromZone, toZone
    required = {"orderId", "priority", "sku", "quantity", "fromZone", "toZone"}
    if not required.issubset(order.keys()):
        raise HTTPException(status_code=400, detail="Missing required fields")
    if order["orderId"] in state.global_state.sales_orders:
        raise HTTPException(status_code=400, detail="Order ID already exists")
    # Basic validation – ensure SKU exists
    sku = order["sku"]
    if sku not in state.global_state.inventory:
        raise HTTPException(status_code=404, detail="SKU not found in inventory")
    new_order = tools.SalesOrder(**order)
    state.global_state.sales_orders[new_order.orderId] = new_order
    return new_order

@router.post("/{order_id}/reserve", summary="Reserve inventory for an order")
async def reserve_order(order_id: str):
    order = state.global_state.sales_orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "open":
        raise HTTPException(status_code=400, detail="Order not open for reservation")
    # Call domain tool to reserve inventory atomically
    success = tools.reserve_inventory(order.sku, order.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient inventory to reserve")
    order.status = "reserved"
    order.createdAt = datetime.utcnow()
    return {"status": "reserved", "orderId": order_id}

@router.post("/{order_id}/fulfill", summary="Convert order to transport tasks and dispatch")
async def fulfill_order(order_id: str):
    order = state.global_state.sales_orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "reserved":
        raise HTTPException(status_code=400, detail="Order must be reserved before fulfillment")
    # Convert order into a VDA‑5050 task using the domain tool
    task = tools.convert_order_to_tasks(order)
    # Persist the task and let the coordinator handle scheduling/execution
    tools.persist_task(task)
    order.status = "fulfilled"
    return {"status": "fulfilled", "orderId": order_id, "taskId": task.taskId}

# End of orders router

