# 💊 PharmaFlow — Pharmacy Inventory Management System

A full-stack web application for managing pharmacy operations including medicines, customers, suppliers, sales orders, purchase orders, and staff access — built as a DBMS Course Project.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, Flask 3.1 |
| ORM | Flask-SQLAlchemy |
| Database | SQLite (via SQLAlchemy) |
| Auth | Werkzeug (PBKDF2-SHA256 hashing) |
| Frontend | Jinja2, HTML, CSS, JavaScript |
| PDF Export | xhtml2pdf |
| Fake Data | Faker (en_IN) |

---

## ✨ Features

- 🔐 **Role-Based Authentication** — 7 roles: Admin, Pharmacist, Doctor, Inventory Manager, Supplier, Receptionist, Auditor
- 💊 **Medicine Management** — Add, edit, delete medicines with expiry tracking and low-stock alerts
- 🧾 **Sales Orders** — Create orders linked to customers and doctors, with PDF invoice export
- 🚚 **Purchase Orders** — Raise and track supplier purchase orders (Pending / Received / Cancelled)
- 👥 **Customer & Supplier Management** — Full CRUD with search
- 📊 **Dashboard** — Real-time stats: revenue, total orders, near-expiry medicines, low stock count
- 📬 **Contact Form** — Message logging to database

---

## 🗃️ Database Schema

8 normalized tables:

```
users → medicines → customers → suppliers
orders → order_items (links orders + medicines)
purchase_orders → purchase_order_items (links POs + medicines)
messages
```

Full schema available in [`database.sql`](database.sql)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/n-a-n-d-a-n/pharmaflow.git
cd pharmaflow
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
flask run
```

Visit: `http://127.0.0.1:5000`

> The database is created and seeded automatically on first run. No manual SQL setup needed.

---

## 🔑 Default Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@pharma.com | admin123 |
| Pharmacist | pharma@pharma.com | pharma123 |
| Doctor | doctor@pharma.com | doctor123 |
| Inventory Manager | inventory@pharma.com | inventory123 |
| Supplier | supplier@pharma.com | supplier123 |
| Receptionist | reception@pharma.com | reception123 |
| Auditor | auditor@pharma.com | auditor123 |

---

## 📁 Project Structure

```
DBMS_CP/
├── app.py               # Main Flask application (models, routes, logic)
├── database.sql         # Raw SQL schema + sample inserts
├── requirements.txt     # Python dependencies
├── static/
│   ├── style.css
│   ├── script.js
│   └── images/
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── medicines.html
    ├── orders.html
    ├── purchase_orders.html
    ├── customers.html
    ├── suppliers.html
    ├── invoice.html
    ├── about.html
    ├── features.html
    └── contact.html
```

---

### DBMS Concepts Demonstrated

- Relational schema design & normalization
- Primary keys, foreign keys, referential integrity
- Indexing on frequently queried columns
- Aggregation queries (`SUM`, `COUNT`, `GROUP BY`) for dashboard stats
- Multi-table JOINs (orders → items → medicines)
- CRUD operations via ORM
- Role-based access control at the application layer

---

## 📄 License

This project is for educational purposes.