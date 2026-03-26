import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_staff
from app.schemas.report import (
    ReportSummarySchema,
    OrdersReportSchema,
    ClientsReportSchema,
    InventoryReportSchema,
)
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

# ── helpers ────────────────────────────────────────────────────────────────

def _stream(data: bytes, media_type: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ══════════════════════════════════════════════════════════════════════
# REPORTE 1 — Resumen general de ventas  (JSON + PDF + xlsx + docx)
# ══════════════════════════════════════════════════════════════════════

@router.get("/summary", response_model=ReportSummarySchema)
def get_summary(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Resumen: total ventas, top 5 partes y pedidos por estado. Solo staff/admin."""
    return report_service.get_summary(db)


@router.get("/summary/pdf")
def get_summary_pdf(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el resumen de ventas en PDF."""
    data = report_service.get_summary(db)
    return _stream(report_service.generate_pdf(data), "application/pdf", "reporte_ventas.pdf")


@router.get("/summary/xlsx")
def get_summary_xlsx(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el resumen de ventas en Excel (.xlsx)."""
    data = report_service.get_summary(db)
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return _stream(report_service.generate_summary_xlsx(data), mime, "reporte_ventas.xlsx")


@router.get("/summary/docx")
def get_summary_docx(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el resumen de ventas en Word (.docx)."""
    data = report_service.get_summary(db)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return _stream(report_service.generate_summary_docx(data), mime, "reporte_ventas.docx")


# ══════════════════════════════════════════════════════════════════════
# REPORTE 2 — Pedidos detallado  (JSON + PDF)
# ══════════════════════════════════════════════════════════════════════

@router.get("/orders", response_model=OrdersReportSchema)
def get_orders_report(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Lista detallada de los últimos 200 pedidos con conteo de items."""
    return report_service.get_orders_report(db)


@router.get("/orders/pdf")
def get_orders_report_pdf(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el reporte de pedidos en PDF."""
    data = report_service.get_orders_report(db)
    return _stream(report_service.generate_orders_pdf(data), "application/pdf", "reporte_pedidos.pdf")


# ══════════════════════════════════════════════════════════════════════
# REPORTE 3 — Clientes por volumen de compras  (JSON + PDF)
# ══════════════════════════════════════════════════════════════════════

@router.get("/clients", response_model=ClientsReportSchema)
def get_clients_report(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Clientes externos ordenados por total gastado (excluye cancelados)."""
    return report_service.get_clients_report(db)


@router.get("/clients/pdf")
def get_clients_report_pdf(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el reporte de clientes en PDF."""
    data = report_service.get_clients_report(db)
    return _stream(report_service.generate_clients_pdf(data), "application/pdf", "reporte_clientes.pdf")


# ══════════════════════════════════════════════════════════════════════
# REPORTE 4 — Inventario actual  (JSON + PDF)
# ══════════════════════════════════════════════════════════════════════

@router.get("/inventory", response_model=InventoryReportSchema)
def get_inventory_report(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Stock actual de todas las autopartes activas. Marca low_stock si stock <= 5."""
    return report_service.get_inventory_report(db)


@router.get("/inventory/pdf")
def get_inventory_report_pdf(
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Descarga el reporte de inventario en PDF."""
    data = report_service.get_inventory_report(db)
    return _stream(report_service.generate_inventory_pdf(data), "application/pdf", "reporte_inventario.pdf")
