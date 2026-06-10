# app.py
# PharmaFlow — Pharmacy Inventory Management System (Flask + SQLAlchemy)

import os
import random
import io
from datetime import datetime, timedelta, date
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, make_response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from faker import Faker
from xhtml2pdf import pisa
from sqlalchemy import func

# -----------------------------------
# App config
# -----------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///pharma.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
fake = Faker("en_IN")

# -----------------------------------
# Models
# -----------------------------------
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # admin/pharmacist/doctor/inventory_manager/supplier/receptionist/auditor

class Medicine(db.Model):
    __tablename__ = "medicines"
    medicine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    stock = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    __tablename__ = "customers"
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

class Supplier(db.Model):
    __tablename__ = "suppliers"
    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    contact_no = db.Column(db.String(20))
    address = db.Column(db.String(255))

class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    doctor_name = db.Column(db.String(120))
    date = db.Column(db.Date, default=datetime.utcnow, index=True)
    customer = db.relationship("Customer", backref="orders")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.medicine_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Order", backref="items")
    medicine = db.relationship("Medicine")

class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"
    po_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.supplier_id"), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, index=True)
    status = db.Column(db.String(32), default="Pending")  # Pending, Received, Cancelled
    supplier = db.relationship("Supplier", backref="purchase_orders")

class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"
    poi_id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.po_id"), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.medicine_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_order = db.relationship("PurchaseOrder", backref="items")
    medicine = db.relationship("Medicine")

class MessageLog(db.Model):
    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

# -----------------------------------
# Helpers: auth and roles
# -----------------------------------
def login_required(view_func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def role_required(*roles):
    def decorator(view_func):
        def wrapper(*args, **kwargs):
            if "user_role" not in session:
                flash("Please login to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("user_role") not in roles:
                flash("You do not have permission.", "error")
                return redirect(url_for("index"))
            return view_func(*args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator

def is_near_expiry(expiry_date: date, days=30):
    return expiry_date <= (datetime.utcnow().date() + timedelta(days=days))

# -----------------------------------
# Seeding with optimized counts
# -----------------------------------
def seed_data():
    # Users
    if User.query.count() == 0:
        base_users = [
            ("Admin User", "admin@pharma.com", "admin123", "admin"),
            ("Pharmacist One", "pharma@pharma.com", "pharma123", "pharmacist"),
            ("Dr. Smith", "doctor@pharma.com", "doctor123", "doctor"),
            ("Inventory Manager", "inventory@pharma.com", "inventory123", "inventory_manager"),
            ("Supplier User", "supplier@pharma.com", "supplier123", "supplier"),
            ("Receptionist User", "reception@pharma.com", "reception123", "receptionist"),
            ("Auditor User", "auditor@pharma.com", "auditor123", "auditor"),
        ]
        for name, email, raw, role in base_users:
            db.session.add(User(name=name, email=email, password=generate_password_hash(raw), role=role))
        for _ in range(5):
            role = random.choice(["pharmacist", "doctor", "receptionist"])
            db.session.add(User(
                name=fake.name(),
                email=fake.unique.email(),
                password=generate_password_hash("password123"),
                role=role
            ))

    # Suppliers (10)
    if Supplier.query.count() < 10:
        for _ in range(10 - Supplier.query.count()):
            db.session.add(Supplier(
                name=fake.company(),
                contact_no=fake.phone_number(),
                address=fake.address().replace("\n", ", ")
            ))

    # Customers (50)
    if Customer.query.count() < 50:
        for _ in range(50 - Customer.query.count()):
            db.session.add(Customer(
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.unique.email()
            ))

    # Medicines (80)
    if Medicine.query.count() < 80:
        categories = ["Antibiotic", "Analgesic", "Supplement", "Antihistamine", "PPI", "NSAID"]
        bases = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Cetirizine", "Omeprazole", "Azithromycin"]
        for _ in range(80 - Medicine.query.count()):
            base = random.choice(bases)
            mg = f"{random.randint(100, 1000)}mg"
            form = random.choice(["Tablet", "Capsule", "Syrup"])
            name = f"{base} {mg} {form}"
            db.session.add(Medicine(
                name=name,
                category=random.choice(categories),
                price=round(random.uniform(10.0, 500.0), 2),
                expiry_date=datetime.utcnow().date() + timedelta(days=random.randint(15, 720)),
                stock=random.randint(0, 200)
            ))
    db.session.commit()

    # Orders with items (100)
    if Order.query.count() < 100:
        customers = Customer.query.all()
        medicines = Medicine.query.all()
        for _ in range(100 - Order.query.count()):
            cust = random.choice(customers)
            order_date = fake.date_between(start_date='-12mo', end_date='today')
            order = Order(customer_id=cust.customer_id, doctor_name=fake.name(), date=order_date)
            db.session.add(order)
            db.session.flush()
            items_count = random.randint(1, 3)
            used_meds = random.sample(medicines, k=min(items_count, len(medicines)))
            for med in used_meds:
                qty = random.randint(1, 5)
                db.session.add(OrderItem(order_id=order.order_id, medicine_id=med.medicine_id, quantity=qty))
                med.stock = max(0, med.stock - qty)
    db.session.commit()

    # Purchase orders with items (50)
    if PurchaseOrder.query.count() < 50:
        suppliers = Supplier.query.all()
        medicines = Medicine.query.all()
        for _ in range(50 - PurchaseOrder.query.count()):
            sup = random.choice(suppliers)
            po_date = fake.date_between(start_date='-12mo', end_date='today')
            status = random.choice(["Pending", "Received", "Cancelled"])
            po = PurchaseOrder(supplier_id=sup.supplier_id, date=po_date, status=status)
            db.session.add(po)
            db.session.flush()
            items_count = random.randint(1, 3)
            used_meds = random.sample(medicines, k=min(items_count, len(medicines)))
            for med in used_meds:
                qty = random.randint(10, 80)
                db.session.add(PurchaseOrderItem(po_id=po.po_id, medicine_id=med.medicine_id, quantity=qty))
                if status == "Received":
                    med.stock += qty
    db.session.commit()

# -----------------------------------
# PDF invoice route (xhtml2pdf)
# -----------------------------------
@app.route("/invoice/<int:order_id>")
@login_required
def invoice(order_id):
    order = Order.query.get_or_404(order_id)

    # Compute items and totals server-side
    items = []
    grand_total = 0.0
    for item in order.items:
        price = float(item.medicine.price or 0.0)
        total = price * item.quantity
        items.append({
            "name": item.medicine.name,
            "category": item.medicine.category,
            "quantity": item.quantity,
            "price": price,
            "total": total
        })
        grand_total += total

    html = render_template("invoice.html", order=order, items=items, grand_total=grand_total)
    pdf = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=invoice_{order_id}.pdf"
    return response

# -----------------------------------
# Core pages
# -----------------------------------
@app.route("/")
def index():
    low_stock = Medicine.query.filter(Medicine.stock < 10).count()
    near_expiry = Medicine.query.filter(Medicine.expiry_date <= (datetime.utcnow().date() + timedelta(days=30))).count()
    return render_template("index.html", low_stock=low_stock, near_expiry=near_expiry)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/features")
def features():
    return render_template("features.html")

# -----------------------------------
# Authentication
# -----------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["user_name"] = user.name
            session["user_role"] = user.role
            flash(f"Welcome, {user.name}.", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash("Invalid credentials.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# -----------------------------------
# Analytics Dashboard (Chart.js data)
# -----------------------------------
@app.route("/dashboard")
@login_required
@role_required("admin", "pharmacist", "doctor", "inventory_manager", "auditor")
def dashboard():
    # Monthly sales grouped by YYYY-MM (SQLite-friendly)
    monthly_rows = (
        db.session.query(
            func.strftime('%Y-%m', Order.date).label('ym'),
            func.count(Order.order_id).label('count')
        )
        .group_by('ym')
        .order_by('ym')
        .all()
    )
    sales_labels = [ym for ym, _ in monthly_rows]
    sales_values = [int(c) for _, c in monthly_rows]

    # Top-selling medicines
    top_rows = (
        db.session.query(
            Medicine.name,
            func.sum(OrderItem.quantity).label('total_sold')
        )
        .join(OrderItem, Medicine.medicine_id == OrderItem.medicine_id)
        .group_by(Medicine.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    top_meds_labels = [name for name, _ in top_rows]
    top_meds_values = [int(total or 0) for _, total in top_rows]

    # Stock usage trends (lowest stock)
    stock_rows = (
        db.session.query(Medicine.name, Medicine.stock)
        .order_by(Medicine.stock.asc(), Medicine.name.asc())
        .limit(10)
        .all()
    )
    stock_labels = [name for name, _ in stock_rows]
    stock_values = [int(stock or 0) for _, stock in stock_rows]

    # Expiry heatmap grouped by YYYY-MM
    expiry_rows = (
        db.session.query(
            func.strftime('%Y-%m', Medicine.expiry_date).label('month'),
            func.count(Medicine.medicine_id)
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    expiry_labels = [month for month, _ in expiry_rows]
    expiry_values = [int(count or 0) for _, count in expiry_rows]

    return render_template(
        "dashboard.html",
        sales_labels=sales_labels,
        sales_values=sales_values,
        top_meds_labels=top_meds_labels,
        top_meds_values=top_meds_values,
        stock_labels=stock_labels,
        stock_values=stock_values,
        expiry_labels=expiry_labels,
        expiry_values=expiry_values
    )

# -----------------------------------
# Medicines (with robust filters + expiry column)
# -----------------------------------
@app.route("/medicines")
@login_required
@role_required("admin", "pharmacist", "doctor", "inventory_manager", "auditor")
def medicines():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "name_asc").strip()

    current_date=datetime.utcnow().date()
    near_expiry_date = current_date + timedelta(days=30)

    query = Medicine.query

    if category:
        query = query.filter(Medicine.category.ilike(f"%{category}%"))

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Medicine.name.ilike(like)) |
            (Medicine.category.ilike(like))
        )

    # ✅ Sorting
    if sort == "name_desc":
        query = query.order_by(Medicine.name.desc())
    elif sort == "category_asc":
        query = query.order_by(Medicine.category.asc())
    elif sort == "category_desc":
        query = query.order_by(Medicine.category.desc())
    elif sort == "price_asc":
        query = query.order_by(Medicine.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Medicine.price.desc())
    elif sort == "stock_asc":
        query = query.order_by(Medicine.stock.asc())
    elif sort == "stock_desc":
        query = query.order_by(Medicine.stock.desc())
    elif sort == "expiry_asc":
        query = query.order_by(Medicine.expiry_date.asc())
    elif sort == "expiry_desc":
        query = query.order_by(Medicine.expiry_date.desc())
    else:
        query = query.order_by(Medicine.name.asc())

    meds = query.all()

    # Category List
    categories = [c[0] for c in db.session.query(Medicine.category).distinct().all()]

    return render_template(
        "medicines.html",
        medicines=meds,
        categories=categories,
        selected_category=category,
        search_term=search,
        sort=sort,
        current_date=current_date,
        near_expiry_date=near_expiry_date
    )

# -----------------------------------
# Suppliers (with search)
# -----------------------------------
@app.route("/suppliers")
@login_required
@role_required("admin", "pharmacist", "inventory_manager", "auditor")
def suppliers():
    search = (request.args.get("search") or "").strip()
    query = Supplier.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Supplier.name.ilike(like)) |
            (Supplier.contact_no.ilike(like)) |
            (Supplier.address.ilike(like))
        )
    sups = query.order_by(Supplier.name.asc()).all()
    return render_template("suppliers.html", suppliers=sups, search_term=search)

# -----------------------------------
# Customers (with search)
# -----------------------------------
@app.route("/customers")
@login_required
@role_required("admin", "pharmacist", "doctor", "receptionist", "auditor")
def customers():
    search = (request.args.get("search") or "").strip()
    query = Customer.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(like)) |
            (Customer.email.ilike(like)) |
            (Customer.phone.ilike(like))
        )
    custs = query.order_by(Customer.name.asc()).all()
    return render_template("customers.html", customers=custs, search_term=search)

# -----------------------------------
# Orders (create -> redirect to invoice)
# -----------------------------------
@app.route("/orders", methods=["GET", "POST"])
@login_required
@role_required("admin", "pharmacist", "doctor", "receptionist", "auditor")
def orders():
    if request.method == "POST":
        try:
            customer_id = int(request.form.get("customer_id"))
            doctor_name = request.form.get("doctor_name", "").strip()
            date_str = request.form.get("date")
            order_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()

            new_order = Order(customer_id=customer_id, doctor_name=doctor_name, date=order_date)
            db.session.add(new_order)
            db.session.flush()

            med_ids = request.form.getlist("item_medicine_id[]")
            qtys = request.form.getlist("item_quantity[]")

            valid_items = 0
            for m_id, q in zip(med_ids, qtys):
                if not m_id or not q:
                    continue
                m_id_int = int(m_id)
                q_int = int(q)
                if q_int <= 0:
                    continue

                med = Medicine.query.get(m_id_int)
                if not med:
                    continue

                if med.stock >= q_int:
                    db.session.add(OrderItem(order_id=new_order.order_id, medicine_id=m_id_int, quantity=q_int))
                    med.stock -= q_int
                    valid_items += 1
                else:
                    flash(f"Cannot add {med.name} — only {med.stock} in stock.", "warning")

            if valid_items == 0:
                db.session.rollback()
                flash("No valid items in order. Order was not placed.", "error")
                return redirect(url_for("orders"))

            db.session.commit()
            flash("Order created successfully.", "success")
            return redirect(url_for("invoice", order_id=new_order.order_id))

        except Exception as e:
            db.session.rollback()
            print("Error creating order:", e)
            flash("An error occurred while creating the order. Please try again.", "error")
            return redirect(url_for("orders"))

    orders_list = Order.query.order_by(Order.date.desc()).all()
    customers_list = Customer.query.order_by(Customer.name.asc()).all()
    medicines_list = Medicine.query.order_by(Medicine.name.asc()).all()
    return render_template(
        "orders.html",
        orders=orders_list,
        customers=customers_list,
        medicines=medicines_list,
        today=date.today()
    )

# -----------------------------------
# Purchase orders
# -----------------------------------
@app.route("/purchase_orders", methods=["GET", "POST"])
@login_required
@role_required("admin", "pharmacist", "inventory_manager", "supplier", "auditor")
def purchase_orders():
    # Supplier role: show only their POs (simple placeholder without user->supplier mapping)
    if session.get("user_role") == "supplier":
        supplier_user = Supplier.query.first()
        if not supplier_user:
            flash("No supplier record found.", "warning")
            return redirect(url_for("index"))
        purchase_orders_list = PurchaseOrder.query.filter_by(
            supplier_id=supplier_user.supplier_id
        ).order_by(PurchaseOrder.date.desc()).all()
        return render_template(
            "purchase_orders.html",
            purchase_orders=purchase_orders_list,
            suppliers=[supplier_user],
            medicines=Medicine.query.order_by(Medicine.name.asc()).all(),
            today=date.today()
        )

    if request.method == "POST":
        try:
            supplier_id = int(request.form.get("supplier_id"))
            date_str = request.form.get("date")
            po_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()

            new_po = PurchaseOrder(supplier_id=supplier_id, date=po_date, status="Pending")
            db.session.add(new_po)
            db.session.flush()

            med_ids = request.form.getlist("item_medicine_id[]")
            qtys = request.form.getlist("item_quantity[]")
            for m_id, q in zip(med_ids, qtys):
                if not m_id or not q:
                    continue
                m_id_int, q_int = int(m_id), int(q)
                if q_int <= 0:
                    continue
                db.session.add(PurchaseOrderItem(po_id=new_po.po_id, medicine_id=m_id_int, quantity=q_int))

            db.session.commit()
            flash("Purchase order created successfully.", "success")
            return redirect(url_for("purchase_orders"))
        except Exception as e:
            db.session.rollback()
            print("Error creating purchase order:", e)
            import traceback; traceback.print_exc()
            flash("An error occurred while creating the purchase order. Please try again.", "error")
            return redirect(url_for("purchase_orders"))

    purchase_orders_list = PurchaseOrder.query.order_by(PurchaseOrder.date.desc()).all()
    suppliers_list = Supplier.query.order_by(Supplier.name.asc()).all()
    medicines_list = Medicine.query.order_by(Medicine.name.asc()).all()
    return render_template(
        "purchase_orders.html",
        purchase_orders=purchase_orders_list,
        suppliers=suppliers_list,
        medicines=medicines_list,
        today=date.today()
    )

# Update PO status (handles receive and rollback stock)
@app.route("/purchase_orders/<int:po_id>/status", methods=["POST"])
@login_required
@role_required("admin", "pharmacist", "inventory_manager")
def update_po_status(po_id):
    new_status = request.form.get("status", "Pending")
    po = PurchaseOrder.query.get_or_404(po_id)
    try:
        if new_status == "Received" and po.status != "Received":
            for item in po.items:
                med = Medicine.query.get(item.medicine_id)
                if med:
                    med.stock += item.quantity
        elif po.status == "Received" and new_status != "Received":
            for item in po.items:
                med = Medicine.query.get(item.medicine_id)
                if med:
                    med.stock = max(0, med.stock - item.quantity)

        po.status = new_status
        db.session.commit()
        flash(f"Purchase order #{po_id} updated to {new_status}.", "success")
    except Exception as e:
        db.session.rollback()
        print("Error updating PO status:", e)
        import traceback; traceback.print_exc()
        flash("An error occurred while updating the status. Please try again.", "error")
    return redirect(url_for("purchase_orders"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message_text = request.form.get("message", "").strip()

        if not name or not email or not subject or not message_text:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for("contact"))

        try:
            db.session.add(MessageLog(name=name, email=email, subject=subject, message=message_text))
            db.session.commit()
            flash("Your message has been received. Thank you!", "success")
        except Exception as e:
            db.session.rollback()
            print("Error saving contact message:", e)
            flash("An error occurred while submitting your message.", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")

# -----------------------------------
# App start
# -----------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # If you want to reseed from scratch, delete pharma.db and rerun.
        seed_data()
    app.run(debug=True)
