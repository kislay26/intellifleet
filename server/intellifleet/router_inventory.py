"""Inventory router – list and query inventory items.

The UI polls `/api/inventory` to display SKU quantities and their locations.
"""

from fastapi import APIRouter, HTTPException
from ..domain import state

router = APIRouter(prefix="/api/inventory", tags=["Inventory"]) 

@router.get("", summary="List all inventory items")
async def list_inventory():
    return list(state.global_state.inventory.values())

@router.get("/{sku}", summary="Get inventory for a specific SKU")
async def get_inventory(sku: str):
    item = state.global_state.inventory.get(sku)
    if not item:
        raise HTTPException(status_code=404, detail="SKU not found")
    return item

# End of inventory router

