import io
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.inventory_log import InventoryLog, InventoryAction
from app.models.order import Order, OrderItem, OrderStatus
from app.models.part import Part
from app.schemas.order import OrderCreateSchema, OrderOut, OrderStatusUpdateSchema
from app.services import report_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items = []
    total = 0
    # Guardamos la referencia al objeto Part para no hacer doble query
    parts_map: dict[str, Part] = {}

    # ── Fase 1: validar todo ANTES de mutar stock ─────────────────────────
    for line in payload.items:
        part = db.query(Part).filter(
            Part.id == line.part_id, Part.is_active == True
        ).first()
        if not part:
            raise HTTPException(404, detail=f"Autoparte {line.part_id} no encontrada")
        if part.stock_quantity < line.quantity:
            raise HTTPException(
                400,
                detail=f"Stock insuficiente para '{part.name}'. Disponible: {part.stock_quantity}",
            )
        parts_map[str(part.id)] = part
        subtotal = part.price * line.quantity
        total += subtotal
        items.append(OrderItem(
            part_id    = part.id,
            quantity   = line.quantity,
            unit_price = part.price,
            subtotal   = subtotal,
        ))

    # ── Fase 2: crear pedido (sin commit aún) ────────────────────────────
    order = Order(
        user_id      = current_user.id,
        total_amount = total,
        items        = items,
    )
    db.add(order)

    # ── Fase 3: descontar stock y registrar log, todo en la misma transacción
    logs = []
    for line in payload.items:
        part = parts_map[str(line.part_id)]
        qty_before = part.stock_quantity
        part.stock_quantity -= line.quantity
        logs.append(InventoryLog(
            part_id         = part.id,
            user_id         = current_user.id,
            action_type     = InventoryAction.SALE,
            quantity_before = qty_before,
            quantity_after  = part.stock_quantity,
            delta           = -line.quantity,
            reason          = f"Venta automática al crear pedido",
        ))

    db.add_all(logs)
    db.commit()          # ← único commit de toda la operación
    db.refresh(order)
    return order


@router.get("/", response_model=list[OrderOut])
def list_orders(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Order)
    if current_user.role == "customer":
        query = query.filter(Order.user_id == current_user.id)
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")
    if current_user.role == "customer" and str(order.user_id) != str(current_user.id):
        raise HTTPException(403, detail="No tienes acceso a este pedido")
    return order


@router.patch("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")
    if current_user.role == "customer" and str(order.user_id) != str(current_user.id):
        raise HTTPException(403, detail="No puedes cancelar este pedido")
    if order.status == OrderStatus.SHIPPED:
        raise HTTPException(400, detail="No se puede cancelar un pedido ya enviado")
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(400, detail="El pedido ya está cancelado")

    order.status       = OrderStatus.CANCELLED
    order.cancelled_at = datetime.now(timezone.utc)   # corregido: utcnow() deprecado

    # ── Devolver stock y registrar log por cada item ──────────────────────
    logs = []
    for item in order.items:
        part = db.query(Part).filter(Part.id == item.part_id).first()
        if part:
            qty_before = part.stock_quantity
            part.stock_quantity += item.quantity
            logs.append(InventoryLog(
                part_id         = part.id,
                user_id         = current_user.id,
                action_type     = InventoryAction.RETURN,
                quantity_before = qty_before,
                quantity_after  = part.stock_quantity,
                delta           = item.quantity,
                reason          = f"Devolución por cancelación de pedido {order_id}",
            ))

    db.add_all(logs)
    db.commit()          # ← único commit
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(
    order_id: str,
    payload: OrderStatusUpdateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(400, detail="No se puede cambiar el estado de un pedido cancelado")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}/pdf")
def get_order_pdf(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Descarga el recibo/documento del pedido en PDF.
    Clientes solo pueden descargar sus propios pedidos.
    Staff y admin pueden descargar cualquiera.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")
    if current_user.role == "customer" and str(order.user_id) != str(current_user.id):
        raise HTTPException(403, detail="No tienes acceso a este pedido")

    pdf_bytes = report_service.generate_order_pdf(order)
    short_id = str(order.id)[:8].upper()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pedido_{short_id}.pdf"},
    )
