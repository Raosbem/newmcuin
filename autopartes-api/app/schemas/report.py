from pydantic import BaseModel
from typing import List, Dict, Optional
from decimal import Decimal


# ── Reporte 1: Resumen de ventas ──────────────────────────────────────────

class TopPartSchema(BaseModel):
    part_id: str
    name: str
    sku: str
    total_quantity_sold: int
    total_revenue: Decimal


class ReportSummarySchema(BaseModel):
    total_sales: Decimal
    total_orders: int
    top_parts: List[TopPartSchema]
    orders_by_status: Dict[str, int]


# ── Reporte 2: Pedidos detallado ──────────────────────────────────────────

class OrderReportItemSchema(BaseModel):
    id: str
    user_id: str
    status: str
    total_amount: Decimal
    items_count: int
    created_at: Optional[str]


class OrdersReportSchema(BaseModel):
    orders: List[OrderReportItemSchema]
    total: int


# ── Reporte 3: Clientes ───────────────────────────────────────────────────

class ClientReportItemSchema(BaseModel):
    user_id: str
    full_name: str
    email: str
    total_orders: int
    total_spent: Decimal


class ClientsReportSchema(BaseModel):
    clients: List[ClientReportItemSchema]
    total_clients: int


# ── Reporte 4: Inventario ─────────────────────────────────────────────────

class InventoryReportItemSchema(BaseModel):
    id: str
    sku: str
    name: str
    category: Optional[str]
    stock_quantity: int
    price: Decimal
    low_stock: bool


class InventoryReportSchema(BaseModel):
    parts: List[InventoryReportItemSchema]
    total_parts: int
    low_stock_count: int
