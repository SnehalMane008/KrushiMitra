from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import pooling
from functools import wraps
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['ESTABLISHMENT_DATE'] = "April 9, 2025"

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'your-app-password'     # Replace with your app password

# OTP storage dictionary - In production, use a database
otp_store = {}  # Format: {'email': {'otp': '123456', 'expiry': datetime}}

# Database connection pool
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'agri_store',
    'pool_name': 'krushimitra_pool',
    'pool_size': 10
}

# Initialize the connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(**db_config)
    print("Connection pool created successfully")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")

# Cache for frequently accessed data
cache = {
    'products': {'data': None, 'timestamp': 0, 'ttl': 300},  # 5 minutes TTL
    'customers': {'data': None, 'timestamp': 0, 'ttl': 300},
    'suppliers': {'data': None, 'timestamp': 0, 'ttl': 300},
}

# DB connection from pool
def get_db_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error getting connection from pool: {err}")
        # Fallback to direct connection if pool fails
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='agri_store'
        )

# Get cached data or fetch from database
def get_cached_data(cache_key, query, params=None):
    current_time = time.time()
    cache_item = cache.get(cache_key)
    
    # If cache exists and is not expired, return cached data
    if (cache_item and cache_item['data'] is not None and 
            current_time - cache_item['timestamp'] < cache_item['ttl']):
        return cache_item['data']
    
    # Otherwise, fetch from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
        
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Update cache
    cache[cache_key] = {
        'data': data,
        'timestamp': current_time,
        'ttl': cache.get(cache_key, {}).get('ttl', 300)
    }
    
    return data

# Clear cache for a specific key
def clear_cache(cache_key=None):
    if cache_key:
        if cache_key in cache:
            cache[cache_key]['data'] = None
            cache[cache_key]['timestamp'] = 0
    else:
        # Clear all cache
        for key in cache:
            cache[key]['data'] = None
            cache[key]['timestamp'] = 0

# Generate OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Send email with OTP
def send_otp_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = email
        msg['Subject'] = 'KrushiMitra - Email Verification OTP'
        
        body = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ padding: 20px; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #27ae60; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .otp {{ font-size: 24px; font-weight: bold; text-align: center; padding: 15px; 
                        background-color: #f5f5f5; margin: 20px 0; letter-spacing: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>KrushiMitra - Email Verification</h2>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Thank you for registering with KrushiMitra. To complete your registration, please use the following One-Time Password (OTP):</p>
                    <div class="otp">{otp}</div>
                    <p>This OTP is valid for 10 minutes. If you did not request this code, please ignore this email.</p>
                    <p>Regards,<br>KrushiMitra Team</p>
                </div>
                <div class="footer">
                    <p>KrushiMitra - Agricultural Management System<br>
                    Developed by Dreamers - AISSMS IOIT, AI&DS Department<br>
                    Under guidance of Dr. Sayali Belhe</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        text = msg.as_string()
        server.sendmail(app.config['MAIL_USERNAME'], email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------- ROUTES --------------------

# Home / Welcome Page
@app.route('/')
def home():
    return render_template('welcome.html', establishment_date=app.config['ESTABLISHMENT_DATE'])

# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html', username=username, email=email)
        
        # Check if username already exists
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('register.html', email=email)
        
        # Generate and store OTP
        otp = generate_otp()
        expiry = datetime.now() + timedelta(minutes=10)
        otp_store[email] = {
            'otp': otp,
            'expiry': expiry,
            'username': username,
            'password': password
        }
        
        # Send OTP via email
        if send_otp_email(email, otp):
            flash('OTP sent to your email', 'success')
            return render_template('register.html', step='verify_otp', email=email, username=username, password=password)
        else:
            flash('Failed to send OTP. Please try again.', 'danger')
            return render_template('register.html', username=username, email=email)
    
    return render_template('register.html')

# Verify OTP and complete registration
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    otp = request.form['otp']
    
    # Check if OTP exists and is valid
    if email not in otp_store or otp_store[email]['otp'] != otp:
        flash('Invalid OTP', 'danger')
        return render_template('register.html', step='verify_otp', email=email, username=username, password=password)
    
    # Check if OTP is expired
    if datetime.now() > otp_store[email]['expiry']:
        flash('OTP has expired. Please try again.', 'danger')
        otp_store.pop(email, None)
        return redirect(url_for('register'))
    
    # Register the user
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Use 'staff' as the default role for new registrations
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                    (username, password, 'staff'))
        conn.commit()
        
        # Clean up OTP
        otp_store.pop(email, None)
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'danger')
        return redirect(url_for('register'))
    finally:
        cursor.close()
        conn.close()

# Login and Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Debug information
        print(f"Login attempt: Username={username}, Password={password}")
        
        try:
            # Query to find the user
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            
            if user:
                # Debug information for successful login
                print(f"Login successful: {user}")
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Get all users for debugging
                cursor.execute("SELECT * FROM users")
                all_users = cursor.fetchall()
                print(f"All users in database: {all_users}")
                
                flash('Invalid username or password', 'danger')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash(f'Error during login: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html', establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get some summary data for the dashboard
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total products
    cursor.execute("SELECT COUNT(*) as product_count FROM products")
    product_count = cursor.fetchone()['product_count']
    
    # Total customers
    cursor.execute("SELECT COUNT(*) as customer_count FROM customers")
    customer_count = cursor.fetchone()['customer_count']
    
    # Total suppliers
    cursor.execute("SELECT COUNT(*) as supplier_count FROM suppliers")
    supplier_count = cursor.fetchone()['supplier_count']
    
    # Recent sales
    cursor.execute("""
        SELECT s.sale_id, c.name as customer, s.sale_date, 
        SUM(si.quantity * si.price) as total
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN sales_items si ON s.sale_id = si.sale_id
        GROUP BY s.sale_id
        ORDER BY s.sale_date DESC
        LIMIT 5
    """)
    recent_sales = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                          product_count=product_count,
                          customer_count=customer_count,
                          supplier_count=supplier_count,
                          recent_sales=recent_sales,
                          establishment_date=app.config['ESTABLISHMENT_DATE'])

# Manage Customers
@app.route('/customers')
@login_required
def customers():
    customers_data = get_cached_data('customers', "SELECT * FROM customers")
    return render_template('customers.html', customers=customers_data, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (name, address, phone) VALUES (%s, %s, %s)", 
                    (name, address, phone))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clear customers cache
        clear_cache('customers')
        
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html', establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        
        cursor.execute("UPDATE customers SET name = %s, address = %s, phone = %s WHERE customer_id = %s",
                    (name, address, phone, customer_id))
        conn.commit()
        
        # Clear customers cache
        clear_cache('customers')
        
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers'))
    
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_customer.html', customer=customer, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/delete_customer/<int:customer_id>')
@login_required
@admin_required
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First check if customer has any sales
    cursor.execute("SELECT COUNT(*) FROM sales WHERE customer_id = %s", (customer_id,))
    if cursor.fetchone()[0] > 0:
        flash('Cannot delete customer with existing sales', 'danger')
        return redirect(url_for('customers'))
    
    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Clear customers cache
    clear_cache('customers')
    
    flash('Customer deleted successfully', 'success')
    return redirect(url_for('customers'))

# Manage Products
@app.route('/products')
@login_required
def products():
    products_data = get_cached_data('products', """
        SELECT p.*, GROUP_CONCAT(s.name SEPARATOR ', ') as suppliers
        FROM products p
        LEFT JOIN product_supplier ps ON p.product_id = ps.product_id
        LEFT JOIN suppliers s ON ps.supplier_id = s.supplier_id
        GROUP BY p.product_id
    """)
    return render_template('products.html', products=products_data, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        supplier_ids = request.form.getlist('suppliers')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert product
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
        product_id = cursor.lastrowid
        
        # Link product to suppliers
        for supplier_id in supplier_ids:
            cursor.execute("INSERT INTO product_supplier (product_id, supplier_id) VALUES (%s, %s)",
                        (product_id, supplier_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clear products cache
        clear_cache('products')
        
        flash('Product added successfully', 'success')
        return redirect(url_for('products'))
    
    # Get suppliers for dropdown
    suppliers_data = get_cached_data('suppliers', "SELECT * FROM suppliers")
    
    return render_template('add_product.html', suppliers=suppliers_data, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        supplier_ids = request.form.getlist('suppliers')
        
        # Update product
        cursor.execute("UPDATE products SET name = %s, price = %s WHERE product_id = %s",
                    (name, price, product_id))
        
        # Update suppliers
        cursor.execute("DELETE FROM product_supplier WHERE product_id = %s", (product_id,))
        for supplier_id in supplier_ids:
            cursor.execute("INSERT INTO product_supplier (product_id, supplier_id) VALUES (%s, %s)",
                        (product_id, supplier_id))
        
        conn.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('products'))
    
    # Get product data
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    
    # Get selected suppliers
    cursor.execute("SELECT supplier_id FROM product_supplier WHERE product_id = %s", (product_id,))
    selected_suppliers = [row['supplier_id'] for row in cursor.fetchall()]
    
    # Get all suppliers
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_product.html', product=product, suppliers=suppliers, 
                         selected_suppliers=selected_suppliers, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/delete_product/<int:product_id>')
@login_required
@admin_required
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product is in any sales
    cursor.execute("SELECT COUNT(*) FROM sales_items WHERE product_id = %s", (product_id,))
    if cursor.fetchone()[0] > 0:
        flash('Cannot delete product that has been sold', 'danger')
        return redirect(url_for('products'))
    
    # Delete product_supplier entries
    cursor.execute("DELETE FROM product_supplier WHERE product_id = %s", (product_id,))
    
    # Delete product
    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    conn.commit()
    conn.close()
    
    # Clear products cache
    clear_cache('products')
    
    flash('Product deleted successfully', 'success')
    return redirect(url_for('products'))

# Manage Suppliers
@app.route('/suppliers')
@login_required
def suppliers():
    suppliers_data = get_cached_data('suppliers', """
        SELECT s.*, COUNT(ps.product_id) as product_count
        FROM suppliers s
        LEFT JOIN product_supplier ps ON s.supplier_id = ps.supplier_id
        GROUP BY s.supplier_id
    """)
    return render_template('suppliers.html', suppliers=suppliers_data, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO suppliers (name, address, phone) VALUES (%s, %s, %s)",
                    (name, address, phone))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clear suppliers cache
        clear_cache('suppliers')
        
        flash('Supplier added successfully', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('add_supplier.html', establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        
        cursor.execute("UPDATE suppliers SET name = %s, address = %s, phone = %s WHERE supplier_id = %s",
                    (name, address, phone, supplier_id))
        conn.commit()
        
        # Clear suppliers cache
        clear_cache('suppliers')
        
        flash('Supplier updated successfully', 'success')
        return redirect(url_for('suppliers'))
    
    cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_supplier.html', supplier=supplier, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/delete_supplier/<int:supplier_id>')
@login_required
@admin_required
def delete_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if supplier has deliveries
    cursor.execute("SELECT COUNT(*) FROM deliveries WHERE supplier_id = %s", (supplier_id,))
    if cursor.fetchone()[0] > 0:
        flash('Cannot delete supplier with existing deliveries', 'danger')
        return redirect(url_for('suppliers'))
    
    # Check if supplier is linked to products
    cursor.execute("SELECT COUNT(*) FROM product_supplier WHERE supplier_id = %s", (supplier_id,))
    if cursor.fetchone()[0] > 0:
        flash('Cannot delete supplier linked to products', 'danger')
        return redirect(url_for('suppliers'))
    
    cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Clear suppliers cache
    clear_cache('suppliers')
    
    flash('Supplier deleted successfully', 'success')
    return redirect(url_for('suppliers'))

# Manage Deliveries
@app.route('/deliveries')
@login_required
def deliveries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, s.name as supplier_name
        FROM deliveries d
        JOIN suppliers s ON d.supplier_id = s.supplier_id
        ORDER BY d.delivery_date DESC
    """)
    deliveries = cursor.fetchall()
    conn.close()
    
    return render_template('deliveries.html', deliveries=deliveries, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_delivery', methods=['GET', 'POST'])
@login_required
def add_delivery():
    if request.method == 'POST':
        supplier_id = request.form['supplier_id']
        delivery_date = request.form['delivery_date']
        quantity = request.form['quantity']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO deliveries (supplier_id, delivery_date, quantity) VALUES (%s, %s, %s)",
                    (supplier_id, delivery_date, quantity))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Delivery added successfully', 'success')
        return redirect(url_for('deliveries'))
    
    # Get suppliers for dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_delivery.html', suppliers=suppliers, establishment_date=app.config['ESTABLISHMENT_DATE'])

# Manage Sales
@app.route('/sales')
@login_required
def sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, c.name as customer_name, 
        SUM(si.quantity * si.price) as total_amount
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN sales_items si ON s.sale_id = si.sale_id
        GROUP BY s.sale_id
        ORDER BY s.sale_date DESC
    """)
    sales = cursor.fetchall()
    conn.close()
    
    return render_template('sales.html', sales=sales, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_sale', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        sale_date = request.form['sale_date'] or datetime.now().strftime('%Y-%m-%d')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create sale record
        cursor.execute("INSERT INTO sales (customer_id, sale_date) VALUES (%s, %s)",
                     (customer_id, sale_date))
        sale_id = cursor.lastrowid
        
        # Add sale items
        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = quantities[i]
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            price = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO sales_items (sale_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (sale_id, product_id, quantity, price))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Sale added successfully', 'success')
        return redirect(url_for('sales'))
    
    # Get customers and products for dropdowns
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('add_sale.html', customers=customers, products=products, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/view_sale/<int:sale_id>')
@login_required
def view_sale(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get sale info
    cursor.execute("""
        SELECT s.*, c.name as customer_name, c.address, c.phone
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        WHERE s.sale_id = %s
    """, (sale_id,))
    sale = cursor.fetchone()
    
    # Get sale items
    cursor.execute("""
        SELECT si.*, p.name as product_name
        FROM sales_items si
        JOIN products p ON si.product_id = p.product_id
        WHERE si.sale_id = %s
    """, (sale_id,))
    items = cursor.fetchall()
    
    # Calculate total
    total = sum(item['quantity'] * item['price'] for item in items)
    
    conn.close()
    
    return render_template('view_sale.html', sale=sale, items=items, total=total, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/users')
@login_required
@admin_required
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return render_template('users.html', users=users, establishment_date=app.config['ESTABLISHMENT_DATE'])

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            flash('Username already exists', 'danger')
            return redirect(url_for('add_user'))
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('User added successfully', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html', establishment_date=app.config['ESTABLISHMENT_DATE'])

if __name__ == '__main__':
    app.run(debug=True)
