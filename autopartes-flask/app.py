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


def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user", {}).get("role") != "superadmin":
            abort(403)
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
    if resp.ok:
        summary = resp.json()
    else:
        summary = {
            "total_sales": 0,
            "total_orders": 0,
            "top_parts": [],
            "orders_by_status": {},
        }
    return render_template("dashboard.html", summary=summary)


# ── Autopartes ────────────────────────────────────────────────────────────────

@app.route("/parts")
@login_required
def parts_index():
    resp = api("GET", "/parts", params={"limit": 100})
    parts = resp.json() if resp.ok else []
    return render_template("parts/index.html", parts=parts)


def _get_brands_and_categories():
    br = api("GET", "/brands")
    ca = api("GET", "/categories")
    return (br.json() if br.ok else []), (ca.json() if ca.ok else [])


@app.route("/parts/new", methods=["GET", "POST"])
@login_required
def parts_create():
    if request.method == "POST":
        payload = {
            "name":           request.form["name"],
            "description":    request.form.get("description") or None,
            "brand_id":       request.form.get("brand_id") or None,
            "category_id":    request.form.get("category_id") or None,
            "price":          float(request.form["price"]),
            "stock_quantity": int(request.form["stock_quantity"]),
        }
        resp = api("POST", "/parts", json=payload)
        if resp.ok:
            part_data = resp.json()
            image = request.files.get("image")
            if image and image.filename:
                api("POST", f"/parts/{part_data['id']}/image",
                    files={"file": (image.filename, image.stream, image.content_type)})
            flash("Autoparte creada exitosamente.", "success")
            return redirect(url_for("parts_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    brands, categories = _get_brands_and_categories()
    return render_template("parts/form.html", part=None, action="Crear",
                           brands=brands, categories=categories)


@app.route("/parts/<part_id>/edit", methods=["GET", "POST"])
@login_required
def parts_edit(part_id):
    part = api("GET", f"/parts/{part_id}").json()
    if request.method == "POST":
        payload = {
            "name":        request.form["name"],
            "description": request.form.get("description") or None,
            "brand_id":    request.form.get("brand_id") or None,
            "category_id": request.form.get("category_id") or None,
            "price":       float(request.form["price"]),
        }
        resp = api("PUT", f"/parts/{part_id}", json=payload)
        if resp.ok:
            image = request.files.get("image")
            if image and image.filename:
                api("POST", f"/parts/{part_id}/image",
                    files={"file": (image.filename, image.stream, image.content_type)})
            flash("Autoparte actualizada.", "success")
            return redirect(url_for("parts_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    brands, categories = _get_brands_and_categories()
    return render_template("parts/form.html", part=part, action="Editar",
                           brands=brands, categories=categories)


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
    start_date = request.args.get("start_date", "")
    end_date   = request.args.get("end_date", "")
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    summary     = api("GET", "/reports/summary",  params=params).json()
    orders_rep  = api("GET", "/reports/orders",   params=params).json()
    clients_rep = api("GET", "/reports/clients",  params=params).json()
    inv_rep     = api("GET", "/reports/inventory").json()

    qs = ""
    if start_date:
        qs += f"?start_date={start_date}"
    if end_date:
        qs += ("&" if start_date else "?") + f"end_date={end_date}"

    return render_template("reports/index.html",
                           summary=summary,
                           orders_rep=orders_rep,
                           clients_rep=clients_rep,
                           inv_rep=inv_rep,
                           start_date=start_date,
                           end_date=end_date,
                           date_qs=qs)


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
    params = {}
    if request.args.get("start_date"):
        params["start_date"] = request.args.get("start_date")
    if request.args.get("end_date"):
        params["end_date"] = request.args.get("end_date")
    resp = api("GET", path, params=params)
    return Response(
        resp.content,
        status=resp.status_code,
        headers={
            "Content-Type":        resp.headers.get("Content-Type", "application/octet-stream"),
            "Content-Disposition": resp.headers.get("Content-Disposition",
                                                     f"attachment; filename={report_type}.{fmt}"),
        },
    )


# ── Inventario ────────────────────────────────────────────────────────────────

@app.route("/inventory")
@login_required
def inventory_index():
    resp = api("GET", "/parts", params={"limit": 200})
    parts = resp.json() if resp.ok else []
    return render_template("inventory/index.html", parts=parts)


@app.route("/inventory/logs")
@login_required
def inventory_logs():
    resp = api("GET", "/inventory/logs", params={"limit": 100})
    logs = resp.json() if resp.ok else []
    return render_template("inventory/logs.html", logs=logs)


# ── Gestión de Administradores (solo superadmin) ──────────────────────────────

@app.route("/admin-users")
@login_required
@superadmin_required
def admin_users_index():
    resp = api("GET", "/users", params={"role": "admin", "limit": 100})
    admins = resp.json() if resp.ok else []
    return render_template("admins/index.html", admins=admins)


@app.route("/admin-users/new", methods=["GET", "POST"])
@login_required
@superadmin_required
def admin_users_create():
    if request.method == "POST":
        payload = {
            "email":     request.form["email"],
            "password":  request.form["password"],
            "full_name": request.form["full_name"],
            "role":      "admin",
        }
        resp = api("POST", "/users", json=payload)
        if resp.ok:
            flash("Administrador creado exitosamente.", "success")
            return redirect(url_for("admin_users_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("admins/form.html", admin_user=None, action="Crear")


@app.route("/admin-users/<user_id>/edit", methods=["GET", "POST"])
@login_required
@superadmin_required
def admin_users_edit(user_id):
    user_resp = api("GET", f"/users/{user_id}")
    admin_user = user_resp.json() if user_resp.ok else {}
    if request.method == "POST":
        payload = {"full_name": request.form["full_name"]}
        resp = api("PUT", f"/users/{user_id}", json=payload)
        if resp.ok:
            flash("Administrador actualizado.", "success")
            return redirect(url_for("admin_users_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("admins/form.html", admin_user=admin_user, action="Editar")


@app.route("/admin-users/<user_id>/toggle", methods=["POST"])
@login_required
@superadmin_required
def admin_users_toggle(user_id):
    resp = api("PATCH", f"/users/{user_id}/toggle-active")
    if resp.ok:
        estado = "activado" if resp.json().get("is_active") else "desactivado"
        flash(f"Administrador {estado}.", "success")
    else:
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return redirect(url_for("admin_users_index"))


# ── Marcas ────────────────────────────────────────────────────────────────────

@app.route("/brands")
@login_required
def brands_index():
    resp = api("GET", "/brands")
    brands = resp.json() if resp.ok else []
    return render_template("brands/index.html", brands=brands)


@app.route("/brands/new", methods=["GET", "POST"])
@login_required
def brands_create():
    if request.method == "POST":
        resp = api("POST", "/brands", json={"name": request.form["name"]})
        if resp.ok:
            flash("Marca creada exitosamente.", "success")
            return redirect(url_for("brands_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("brands/form.html", brand=None, action="Crear")


@app.route("/brands/<brand_id>/edit", methods=["GET", "POST"])
@login_required
def brands_edit(brand_id):
    brand_resp = api("GET", f"/brands/{brand_id}")
    brand = brand_resp.json() if brand_resp.ok else {}
    if request.method == "POST":
        resp = api("PUT", f"/brands/{brand_id}", json={"name": request.form["name"]})
        if resp.ok:
            flash("Marca actualizada.", "success")
            return redirect(url_for("brands_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("brands/form.html", brand=brand, action="Editar")


@app.route("/brands/<brand_id>/delete", methods=["POST"])
@login_required
def brands_delete(brand_id):
    resp = api("DELETE", f"/brands/{brand_id}")
    if resp.ok:
        flash("Marca eliminada.", "success")
    else:
        flash(f"Error: {resp.json().get('detail', 'No se pudo eliminar')}", "danger")
    return redirect(url_for("brands_index"))


# ── Categorías ────────────────────────────────────────────────────────────────

@app.route("/categories")
@login_required
def categories_index():
    resp = api("GET", "/categories")
    categories = resp.json() if resp.ok else []
    return render_template("categories/index.html", categories=categories)


@app.route("/categories/new", methods=["GET", "POST"])
@login_required
def categories_create():
    if request.method == "POST":
        resp = api("POST", "/categories", json={"name": request.form["name"]})
        if resp.ok:
            flash("Categoría creada exitosamente.", "success")
            return redirect(url_for("categories_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("categories/form.html", category=None, action="Crear")


@app.route("/categories/<category_id>/edit", methods=["GET", "POST"])
@login_required
def categories_edit(category_id):
    cat_resp = api("GET", f"/categories/{category_id}")
    category = cat_resp.json() if cat_resp.ok else {}
    if request.method == "POST":
        resp = api("PUT", f"/categories/{category_id}", json={"name": request.form["name"]})
        if resp.ok:
            flash("Categoría actualizada.", "success")
            return redirect(url_for("categories_index"))
        flash(f"Error: {resp.json().get('detail', 'Error desconocido')}", "danger")
    return render_template("categories/form.html", category=category, action="Editar")


@app.route("/categories/<category_id>/delete", methods=["POST"])
@login_required
def categories_delete(category_id):
    resp = api("DELETE", f"/categories/{category_id}")
    if resp.ok:
        flash("Categoría eliminada.", "success")
    else:
        flash(f"Error: {resp.json().get('detail', 'No se pudo eliminar')}", "danger")
    return redirect(url_for("categories_index"))


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
