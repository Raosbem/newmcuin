from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.order import Order, OrderItem, OrderStatus
from app.models.part import Part
from app.schemas.order import OrderCreateSchema, OrderOut, OrderStatusUpdateSchema

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    items = []
    total = 0

    for line in payload.items:
        part = db.query(Part).filter(Part.id == line.part_id, Part.is_active == True).first()
        if not part:
            raise HTTPException(404, detail=f"Autoparte {line.part_id} no encontrada")
        if part.stock_quantity < line.quantity:
            raise HTTPException(400, detail=f"Stock insuficiente para '{part.name}'. Disponible: {part.stock_quantity}")

        subtotal = part.price * line.quantity
        total += subtotal
        items.append(OrderItem(
            part_id    = part.id,
            quantity   = line.quantity,
            unit_price = part.price,
            subtotal   = subtotal,
        ))

    order = Order(
        user_id      = current_user.id,
        total_amount = total,
        items        = items,
    )
    db.add(order)

    # descontar stock
    for line in payload.items:
        part = db.query(Part).filter(Part.id == line.part_id).first()
        part.stock_quantity -= line.quantity

    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=list[OrderOut])
def list_orders(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Order)

    if current_user.role == "customer":
        query = query.filter(Order.user_id == current_user.id)

    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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
    current_user=Depends(get_current_user)
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
    order.cancelled_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(
    order_id: str,
    payload: OrderStatusUpdateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff)
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