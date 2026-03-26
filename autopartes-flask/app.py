import os
import requests
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, Response, abort,
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")


# ── Helpers ───────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    """Llama a la API FastAPI inyectando el JWT de la sesión si existe."""
    token = session.get("token")
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        return requests.request(
            method, f"{API_URL}{path}",
            headers=headers, timeout=10, **kwargs,
        )
    except requests.ConnectionError:
        class _Err:
            ok = False
            status_code = 503
            def json(self): return {"detail": "No se pudo conectar con la API"}
        return _Err()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "token" not in session:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "token" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "token" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        resp = api("POST", "/auth/login", json={
            "email": request.form["email"],
            "password": request.form["password"],
        })
        if resp.status_code == 200:
            session["token"] = resp.json()["access_token"]
            me_resp = api("GET", "/auth/me")
            if me_resp.ok:
                me = me_resp.json()
                if me.get("role") == "customer":
                    session.clear()
                    flash("Acceso denegado: solo personal interno.", "danger")
                    return redirect(url_for("login"))
                session["user"] = me
                flash(f"Bienvenido, {me['full_name']}!", "success")
                return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    resp = api("GET", "/reports/summary")
    summary = resp.json() if resp.ok else {}
    return render_template("dashboard.html", summary=summary)


# ── Autopartes ────────────────────────────────────────────────────────────────

@app.route("/parts")
@login_required
def parts_index():
    resp = api("GET", "/parts", params={"limit": 100})
    parts = resp.json() if resp.ok else []
    return render_template("parts/index.html", parts=parts)


@app.route("/parts/new", methods=["GET", "POST"])
@login_required
def parts_create():
    if request.method == "POST":
        payload = {
            "sku":            request.form["sku"],
            "name":           request.form["name"],
            "description":    request.form.get("description") or None,
            "brand":          request.form.get("brand") or None,
            "category":       request.form.get("category") or None,
            "price":          float(request.form["price"]),
            "stock_quantity": int(request.form["stock_quantity"]),
        }
        resp = api("POST", "/parts", json=payload)
        if resp.ok:
            flash("Autoparte creada exitosamente.", "success")
            return redirect(url_for("parts_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("parts/form.html", part=None, action="Crear")


@app.route("/parts/<part_id>/edit", methods=["GET", "POST"])
@login_required
def parts_edit(part_id):
    part = api("GET", f"/parts/{part_id}").json()
    if request.method == "POST":
        payload = {
            "name":        request.form["name"],
            "description": request.form.get("description") or None,
            "brand":       request.form.get("brand") or None,
            "category":    request.form.get("category") or None,
            "price":       float(request.form["price"]),
        }
        resp = api("PUT", f"/parts/{part_id}", json=payload)
        if resp.ok:
            flash("Autoparte actualizada.", "success")
            return redirect(url_for("parts_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("parts/form.html", part=part, action="Editar")


@app.route("/parts/<part_id>/delete", methods=["POST"])
@login_required
def parts_delete(part_id):
    resp = api("DELETE", f"/parts/{part_id}")
    flash("Autoparte eliminada." if resp.ok else "No se pudo eliminar.", "success" if resp.ok else "danger")
    return redirect(url_for("parts_index"))


@app.route("/parts/<part_id>/stock", methods=["GET", "POST"])
@login_required
def parts_stock(part_id):
    part = api("GET", f"/parts/{part_id}").json()
    if request.method == "POST":
        payload = {
            "quantity": int(request.form["quantity"]),
            "reason":   request.form["reason"],
        }
        resp = api("PATCH", f"/parts/{part_id}/stock", json=payload)
        if resp.ok:
            flash("Stock actualizado.", "success")
            return redirect(url_for("parts_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("parts/stock.html", part=part)


# ── Pedidos ───────────────────────────────────────────────────────────────────

@app.route("/orders")
@login_required
def orders_index():
    resp = api("GET", "/orders", params={"limit": 100})
    orders = resp.json() if resp.ok else []
    return render_template("orders/index.html", orders=orders)


@app.route("/orders/<order_id>")
@login_required
def orders_detail(order_id):
    resp = api("GET", f"/orders/{order_id}")
    if not resp.ok:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("orders_index"))
    return render_template("orders/detail.html", order=resp.json())


@app.route("/orders/<order_id>/status", methods=["POST"])
@login_required
def orders_status(order_id):
    resp = api("PATCH", f"/orders/{order_id}/status", json={"status": request.form["status"]})
    if resp.ok:
        flash("Estado actualizado.", "success")
    else:
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return redirect(url_for("orders_detail", order_id=order_id))


# ── Reportes ──────────────────────────────────────────────────────────────────

@app.route("/reports")
@login_required
def reports_index():
    summary    = api("GET", "/reports/summary").json()
    orders_rep = api("GET", "/reports/orders").json()
    clients_rep = api("GET", "/reports/clients").json()
    inv_rep    = api("GET", "/reports/inventory").json()
    return render_template("reports/index.html",
                           summary=summary,
                           orders_rep=orders_rep,
                           clients_rep=clients_rep,
                           inv_rep=inv_rep)


@app.route("/reports/<report_type>/<fmt>")
@login_required
def reports_download(report_type, fmt):
    path_map = {
        ("summary",   "pdf"):  "/reports/summary/pdf",
        ("summary",   "xlsx"): "/reports/summary/xlsx",
        ("summary",   "docx"): "/reports/summary/docx",
        ("orders",    "pdf"):  "/reports/orders/pdf",
        ("clients",   "pdf"):  "/reports/clients/pdf",
        ("inventory", "pdf"):  "/reports/inventory/pdf",
    }
    path = path_map.get((report_type, fmt))
    if not path:
        abort(404)
    resp = api("GET", path)
    return Response(
        resp.content,
        status=resp.status_code,
        headers={
            "Content-Type":        resp.headers.get("Content-Type", "application/octet-stream"),
            "Content-Disposition": resp.headers.get("Content-Disposition",
                                                     f"attachment; filename={report_type}.{fmt}"),
        },
    )


# ── Inventario (logs de auditoría) ────────────────────────────────────────────

@app.route("/inventory/logs")
@login_required
def inventory_logs():
    resp = api("GET", "/inventory/logs", params={"limit": 100})
    logs = resp.json() if resp.ok else []
    return render_template("inventory/logs.html", logs=logs)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
