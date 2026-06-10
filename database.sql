-- database.sql
-- Schema + sample inserts (compatible with SQLite; adjust types for MySQL if needed)

DROP TABLE IF EXISTS purchase_order_items;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL
);

CREATE TABLE medicines (
  medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price REAL NOT NULL,
  expiry_date DATE NOT NULL,
  stock INTEGER NOT NULL
);

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT
);

CREATE TABLE suppliers (
  supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  contact_no TEXT,
  address TEXT
);

CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  doctor_name TEXT,
  date DATE,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  medicine_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

CREATE TABLE messages (
  message_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL
);

-- 🆕 New tables for supplier purchase orders
CREATE TABLE purchase_orders (
  po_id INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_id INTEGER NOT NULL,
  date DATE,
  status TEXT DEFAULT 'Pending',
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE purchase_order_items (
  poi_id INTEGER PRIMARY KEY AUTOINCREMENT,
  po_id INTEGER NOT NULL,
  medicine_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
);

-- Sample data
INSERT INTO users (name, email, password, role) VALUES
('Admin User', 'admin@pharma.com', '$pbkdf2:sha256$260000$sample$hashedadmin', 'admin'),
('Pharmacist One', 'pharma@pharma.com', '$pbkdf2:sha256$260000$sample$hashedpharma', 'pharmacist'),
('Dr. Smith', 'doctor@pharma.com', '$pbkdf2:sha256$260000$sample$hasheddoctor', 'doctor');

-- Note: Password hashes above are placeholders if using raw SQL.
-- The app seeds real hashed passwords automatically on first run.

INSERT INTO suppliers (name, contact_no, address) VALUES
('MediSupply Pvt Ltd', '+91-9876543210', 'Pune, MH'),
('HealthLine Distributors', '+91-9012345678', 'Mumbai, MH'),
('CarePharm Co.', '+91-9123456780', 'Delhi'),
('Wellness Traders', '+91-9988776655', 'Bengaluru, KA'),
('LifeMedic Suppliers', '+91-9090909090', 'Hyderabad, TS');

INSERT INTO customers (name, phone, email) VALUES
('Nandan', '+91-8888888888', 'nandan@example.com'),
('Asha Verma', '+91-7777777777', 'asha@example.com'),
('Rahul Mehta', '+91-6666666666', 'rahul@example.com'),
('Priya Singh', '+91-5555555555', 'priya@example.com'),
('Vikas Patil', '+91-4444444444', 'vikas@example.com');

INSERT INTO medicines (name, category, price, expiry_date, stock) VALUES
('Paracetamol 500mg', 'Analgesic', 25.0, DATE('now','+180 day'), 50),
('Amoxicillin 250mg', 'Antibiotic', 120.0, DATE('now','+60 day'), 8),
('Ibuprofen 200mg', 'NSAID', 45.0, DATE('now','+25 day'), 12),
('Cetirizine 10mg', 'Antihistamine', 30.0, DATE('now','+365 day'), 100),
('Omeprazole 20mg', 'PPI', 80.0, DATE('now','+90 day'), 9),
('Metformin 500mg', 'Antidiabetic', 60.0, DATE('now','+200 day'), 40),
('Azithromycin 500mg', 'Antibiotic', 150.0, DATE('now','+45 day'), 20),
('Losartan 50mg', 'Antihypertensive', 110.0, DATE('now','+400 day'), 60),
('Vitamin D3 60000 IU', 'Supplement', 90.0, DATE('now','+300 day'), 15),
('Insulin 100 IU/ml', 'Hormone', 350.0, DATE('now','+30 day'), 5);

-- Orders + items
INSERT INTO orders (customer_id, doctor_name, date) VALUES
(1, 'Dr. Smith', DATE('now')),
(2, 'Dr. Gupta', DATE('now')),
(3, 'Dr. Kumar', DATE('now'));

INSERT INTO order_items (order_id, medicine_id, quantity) VALUES
(1, 1, 2),
(1, 3, 1),
(2, 2, 1),
(3, 4, 3);

-- 🆕 Sample purchase orders
INSERT INTO purchase_orders (supplier_id, date, status) VALUES
(1, DATE('now'), 'Pending'),
(2, DATE('now','-7 day'), 'Received');

INSERT INTO purchase_order_items (po_id, medicine_id, quantity) VALUES
(1, 2, 50),
(1, 5, 30),
(2, 1, 100),
(2, 4, 40);
