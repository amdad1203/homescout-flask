# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import datetime
from decimal import Decimal
from db import fetchone, fetchall, execute, transaction
from utils import to_int, to_float, currency
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "change_this_secret_please")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- ADD CUSTOM FILTER HERE ---
@app.template_filter('format_price')
def format_price_filter(value):
    """Format price with commas for thousands"""
    try:
        if value is None:
            return "0"
        if isinstance(value, str):
            value = float(value.replace(',', ''))
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return str(value)

# --- helpers ---
def login_user_row(row):
    session['user_id'] = row['user_id']
    session['username'] = row['username']
    session['role'] = row['role']

def require_roles(*roles):
    def decorator(fn):
        def wrapped(*a, **kw):
            if session.get('role') not in roles:
                return redirect(url_for('index'))
            return fn(*a, **kw)
        wrapped.__name__ = fn.__name__
        return wrapped
    return decorator

# --- routes ---
@app.route('/')
def index():
    success = session.pop('_success', None)
    error = session.pop('_error', None)
    
    # Add featured properties for landing page
    featured_properties = [
        {
            'id': 1,
            'title': 'Modern Luxury Apartment',
            'location': 'Dhanmondi',
            'city': 'Dhaka',
            'bedrooms': 3,
            'bathrooms': 2,
            'area': 1800,
            'price': 9500000
        },
        {
            'id': 2,
            'title': 'Beachfront Villa',
            'location': 'Cox\'s Bazar',
            'city': 'Cox\'s Bazar',
            'bedrooms': 4,
            'bathrooms': 3,
            'area': 3200,
            'price': 22000000
        },
        {
            'id': 3,
            'title': 'City Center Penthouse',
            'location': 'Gulshan',
            'city': 'Dhaka',
            'bedrooms': 2,
            'bathrooms': 2,
            'area': 1500,
            'price': 18500000
        }
    ]
    
    return render_template('index.html', 
                         featured_properties=featured_properties,
                         success=success, 
                         error=error)

# Register (plain password)
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('username','').strip()
    email = request.form.get('email','').strip() or None
    phone = request.form.get('phone','').strip() or None
    password = request.form.get('password','')
    role = request.form.get('role','buyer')
    if not username or not password:
        session['_error'] = 'Missing username or password'
        return redirect(url_for('register'))
    existing = fetchone('SELECT user_id FROM users WHERE username=%s OR email=%s OR phone=%s', (username, email, phone))
    if existing:
        session['_error'] = 'Username/email/phone already exists'
        return redirect(url_for('register'))
    user_id = execute('INSERT INTO users (username,email,phone,password,role) VALUES (%s,%s,%s,%s,%s)', (username, email, phone, password, role))
    # create role record
    if role == 'buyer':
        execute('INSERT INTO buyers (buyer_id, full_name) VALUES (%s,%s)', (user_id, username))
    elif role == 'seller':
        execute('INSERT INTO sellers (seller_id, full_name) VALUES (%s,%s)', (user_id, username))
    elif role == 'employee':
        execute('INSERT INTO employees (employee_id, display_name) VALUES (%s,%s)', (user_id, username))
    elif role == 'investor':
        execute('INSERT INTO investors (investor_id, full_name) VALUES (%s,%s)', (user_id, username))
    session['_success'] = 'Registered. Please login.'
    return redirect(url_for('login'))

# Login (plain password)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    ident = request.form.get('identifier','').strip()
    password = request.form.get('password','')
    row = fetchone('SELECT user_id, username, role, password FROM users WHERE username=%s OR email=%s OR phone=%s', (ident, ident, ident))
    if not row or row.get('password') != password:
        session['_error'] = 'Invalid credentials'
        return redirect(url_for('login'))
    login_user_row(row)
    session['_success'] = 'Welcome ' + row['username']
    # redirect to role dashboard
    role = row['role']
    if role == 'admin': return redirect(url_for('admin_dashboard'))
    if role == 'seller': return redirect(url_for('seller_dashboard'))
    if role == 'buyer': return redirect(url_for('buyer_dashboard'))
    if role == 'employee': return redirect(url_for('agent_dashboard'))
    if role == 'investor': return redirect(url_for('investor_dashboard'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- admin ---
@app.route('/admin')
@require_roles('admin')
def admin_dashboard():
    totals = fetchone('SELECT (SELECT COUNT(*) FROM users) as users, (SELECT COUNT(*) FROM properties) as properties, (SELECT COUNT(*) FROM sales) as sales')
    top_locations = fetchall('SELECT city, COUNT(*) as cnt FROM properties GROUP BY city ORDER BY cnt DESC LIMIT 10')
    top_agents = fetchall('SELECT e.employee_id, e.display_name, COALESCE(SUM(s.final_price),0) as total_sales, COUNT(s.sale_id) as sales_count FROM employees e LEFT JOIN sales s ON e.employee_id=s.employee_id GROUP BY e.employee_id ORDER BY total_sales DESC LIMIT 10')
    return render_template('admin.html', totals=totals, top_locations=top_locations, top_agents=top_agents)

@app.route('/admin/users')
@require_roles('admin')
def admin_users():
    users = fetchall('SELECT user_id, username, email, phone, role, created_at FROM users ORDER BY user_id LIMIT 200')
    return render_template('admin_users.html', users=users)

@app.route('/admin/properties')
@require_roles('admin')
def admin_properties():
    props = fetchall('SELECT p.*, s.full_name as seller_name, e.display_name as agent_name FROM properties p LEFT JOIN sellers s ON p.seller_id=s.seller_id LEFT JOIN employees e ON p.listed_by_employee=e.employee_id ORDER BY p.created_at DESC LIMIT 500')
    return render_template('admin_properties.html', properties=props)

@app.route('/admin/remove_user/<int:user_id>', methods=['POST'])
@require_roles('admin')
def admin_remove_user(user_id):
    execute('DELETE FROM users WHERE user_id=%s', (user_id,))
    session['_success'] = 'User removed'
    return redirect(url_for('admin_users'))

@app.route('/admin/remove_property/<int:property_id>', methods=['POST'])
@require_roles('admin')
def admin_remove_property(property_id):
    execute('UPDATE properties SET lifecycle_status=%s, status=%s WHERE property_id=%s', ('Removed','Inactive',property_id))
    session['_success'] = 'Property removed'
    return redirect(url_for('admin_properties'))

# --- seller ---
@app.route('/seller')
@require_roles('seller')
def seller_dashboard():
    seller_id = session.get('user_id')
    requests = fetchall('SELECT * FROM seller_requests WHERE seller_id=%s ORDER BY created_at DESC', (seller_id,))
    properties = fetchall('SELECT * FROM properties WHERE seller_id=%s ORDER BY created_at DESC', (seller_id,))
    return render_template('seller.html', requests=requests, properties=properties)

@app.route('/seller/new_request', methods=['GET','POST'])
@require_roles('seller')
def seller_new_request():
    if request.method == 'GET':
        return render_template('add_request.html')
    seller_id = session.get('user_id')
    approx_location = request.form.get('approx_location')
    approx_city = request.form.get('approx_city')
    approx_price = to_float(request.form.get('approx_price'))
    approx_floor = to_int(request.form.get('approx_floor'))
    approx_rooms = to_int(request.form.get('approx_rooms'))
    notes = request.form.get('notes')
    execute('INSERT INTO seller_requests (seller_id, approx_location, approx_city, approx_price, approx_floor, approx_rooms, notes) VALUES (%s,%s,%s,%s,%s,%s,%s)', (seller_id, approx_location, approx_city, approx_price, approx_floor, approx_rooms, notes))
    session['_success'] = 'Request submitted'
    return redirect(url_for('seller_dashboard'))

# --- property completion (agent/admin) ---
@app.route('/property/complete/<int:property_id>', methods=['GET','POST'])
@require_roles('admin','employee')
def property_complete(property_id):
    if request.method == 'GET':
        prop = fetchone('SELECT p.*, s.full_name as seller_name FROM properties p JOIN sellers s ON p.seller_id=s.seller_id WHERE p.property_id=%s', (property_id,))
        return render_template('property_complete.html', prop=prop)
    listed_by_employee = session.get('user_id')
    title = request.form.get('title')
    description = request.form.get('description')
    area_sqft = to_int(request.form.get('area_sqft'))
    floor = to_int(request.form.get('floor'))
    total_rooms = to_int(request.form.get('total_rooms'))
    bathrooms = to_int(request.form.get('bathrooms'))
    balcony_count = to_int(request.form.get('balcony_count'))
    facing = request.form.get('facing')
    has_lift = 1 if request.form.get('has_lift')=='on' else 0
    open_kitchen = 1 if request.form.get('open_kitchen')=='on' else 0
    parking_type = request.form.get('parking_type') or 'None'
    base_price = to_float(request.form.get('base_price'))
    est_val = to_float(request.form.get('estimated_market_value') or base_price)
    execute("""UPDATE properties SET listed_by_employee=%s, title=%s, description=%s, area_sqft=%s, floor=%s,
               total_rooms=%s, bathrooms=%s, balcony_count=%s, facing=%s, has_lift=%s, open_kitchen=%s,
               parking_type=%s, base_price=%s, estimated_market_value=%s, lifecycle_status=%s, status=%s
               WHERE property_id=%s""",
            (listed_by_employee, title, description, area_sqft, floor, total_rooms, bathrooms, balcony_count, facing, has_lift, open_kitchen, parking_type, base_price, est_val, 'Enlisted', 'Available', property_id))
    session['_success'] = 'Property completed & enlisted'
    return redirect(url_for('admin_properties') if session.get('role')=='admin' else url_for('agent_dashboard'))

# --- buyer ---
@app.route('/buyer')
@require_roles('buyer')
def buyer_dashboard():
    properties = fetchall("SELECT * FROM properties WHERE status='Available' AND lifecycle_status='Enlisted' ORDER BY created_at DESC LIMIT 10")
    return render_template('buyer.html', properties=properties)

@app.route('/search')
def search_results():
    city = request.args.get('city')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_rooms = request.args.get('min_rooms')
    sql = "SELECT * FROM properties WHERE status='Available' AND lifecycle_status='Enlisted' "
    params = []
    if city:
        sql += "AND city=%s "; params.append(city)
    if min_price:
        sql += "AND base_price >= %s "; params.append(min_price)
    if max_price:
        sql += "AND base_price <= %s "; params.append(max_price)
    if min_rooms:
        sql += "AND total_rooms >= %s "; params.append(min_rooms)
    sql += "ORDER BY base_price ASC LIMIT 200"
    properties = fetchall(sql, tuple(params))
    return render_template('search_results.html', properties=properties, filters=request.args)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    prop = fetchone('SELECT p.*, s.full_name as seller_name, e.display_name as agent_name FROM properties p LEFT JOIN sellers s ON p.seller_id=s.seller_id LEFT JOIN employees e ON p.listed_by_employee=e.employee_id WHERE p.property_id=%s', (property_id,))
    photos = fetchall('SELECT * FROM property_photos WHERE property_id=%s ORDER BY is_primary DESC, uploaded_at DESC', (property_id,))
    return render_template('property_detail.html', prop=prop, photos=photos)

@app.route('/enquiry', methods=['POST'])
@require_roles('buyer')
def create_enquiry():
    property_id = int(request.form.get('property_id'))
    buyer_id = session.get('user_id')
    agent = fetchone('SELECT employee_id FROM employees WHERE status=%s LIMIT 1', ('Active',))
    if not agent:
        session['_error'] = 'No agent available'
        return redirect(url_for('property_detail', property_id=property_id))
    employee_id = agent['employee_id']
    enquiry_date = datetime.date.today()
    notes = request.form.get('notes')
    execute('INSERT INTO enquiries (property_id, buyer_id, employee_id, enquiry_date, notes) VALUES (%s,%s,%s,%s,%s)', (property_id, buyer_id, employee_id, enquiry_date, notes))
    session['_success'] = 'Enquiry created'
    return redirect(url_for('property_detail', property_id=property_id))

# --- agent ---
@app.route('/agent')
@require_roles('employee')
def agent_dashboard():
    emp_id = session.get('user_id')
    enquiries = fetchall('SELECT e.*, p.title, b.full_name as buyer_name FROM enquiries e JOIN properties p ON e.property_id=p.property_id JOIN buyers b ON e.buyer_id=b.buyer_id WHERE e.employee_id=%s ORDER BY e.enquiry_date DESC', (emp_id,))
    properties = fetchall('SELECT * FROM properties WHERE listed_by_employee=%s', (emp_id,))
    return render_template('agent.html', enquiries=enquiries, properties=properties)

@app.route('/agent/update_enquiry/<int:enquiry_id>', methods=['POST'])
@require_roles('employee')
def update_enquiry(enquiry_id):
    status = request.form.get('status')
    notes = request.form.get('notes')
    execute('UPDATE enquiries SET status=%s, notes=CONCAT(COALESCE(notes,""),%s) WHERE enquiry_id=%s', (status, '\n'+(notes or ''), enquiry_id))
    session['_success'] = 'Enquiry updated'
    return redirect(url_for('agent_dashboard'))

# --- sale completion ---
@app.route('/sale/complete', methods=['POST'])
@require_roles('employee','admin')
def sale_complete():
    property_id = int(request.form.get('property_id'))
    buyer_id = int(request.form.get('buyer_id'))
    final_price = Decimal(request.form.get('final_price') or 0)
    prop = fetchone('SELECT seller_id, listed_by_employee FROM properties WHERE property_id=%s', (property_id,))
    if not prop:
        session['_error'] = 'Property not found'
        return redirect(url_for('index'))
    seller_id = prop['seller_id']
    employee_id = prop['listed_by_employee'] or session.get('user_id')
    emp_comm = (final_price * Decimal('0.002'))  # 0.2%
    comp_comm = (final_price * Decimal('0.02'))  # 2%
    sale_date = datetime.date.today()
    try:
        with transaction() as (conn, cur):
            cur.execute('INSERT INTO sales (property_id,buyer_id,seller_id,employee_id,final_price,employee_commission,company_commission,sale_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (property_id, buyer_id, seller_id, employee_id, float(final_price), float(emp_comm), float(comp_comm), sale_date))
            sale_id = cur.lastrowid
            cur.execute('INSERT INTO payments (sale_id, from_user_id, to_user_id, payment_type, amount, notes) VALUES (%s,%s,%s,%s,%s,%s)', (sale_id, buyer_id, 1, 'BuyerToCompany', float(final_price), 'Buyer paid company'))
            payout_to_seller = float(final_price - (emp_comm + comp_comm))
            cur.execute('INSERT INTO payments (sale_id, from_user_id, to_user_id, payment_type, amount, notes) VALUES (%s,%s,%s,%s,%s,%s)', (sale_id, 1, seller_id, 'CompanyToSeller', payout_to_seller, 'Payout to seller'))
            cur.execute('INSERT INTO payments (sale_id, from_user_id, to_user_id, payment_type, amount, notes) VALUES (%s,%s,%s,%s,%s,%s)', (sale_id, 1, employee_id, 'CompanyToEmployee', float(emp_comm), 'Agent commission'))
            cur.execute('UPDATE properties SET status=%s, lifecycle_status=%s WHERE property_id=%s', ('Sold','Sold', property_id))
    except Exception as e:
        session['_error'] = f'Sale failed: {e}'
        return redirect(url_for('index'))
    session['_success'] = 'Sale completed'
    return redirect(url_for('admin_dashboard') if session.get('role')=='admin' else url_for('agent_dashboard'))

# --- investor ---
@app.route('/investor')
@require_roles('investor')
def investor_dashboard():
    investor_id = session.get('user_id')
    # Get investor info
    investor_info = fetchone('SELECT * FROM investors WHERE investor_id = %s', (investor_id,))
    
    # Get investor's investments
    investments = fetchall('''
        SELECT pi.*, p.title, p.city, p.base_price, p.status
        FROM property_investments pi
        JOIN properties p ON pi.property_id = p.property_id
        WHERE pi.investor_id = %s
        ORDER BY pi.created_at DESC
    ''', (investor_id,))
    
    # Get available properties for new investments
    available_properties = fetchall("""
        SELECT * FROM properties 
        WHERE status='Available' AND lifecycle_status='Enlisted' 
        LIMIT 50
    """)
    
    return render_template('investor.html', 
                         investments=investments,
                         investor_info=investor_info,
                         properties=available_properties)

@app.route('/invest', methods=['POST'])
@require_roles('investor')
def invest():
    """Handle investment form submission"""
    property_id = int(request.form.get('property_id'))
    amount = Decimal(request.form.get('amount') or 0)
    investor_id = session.get('user_id')
    with transaction() as (conn, cur):
        cur.execute('INSERT INTO property_investments (property_id, investor_id, invested_amount) VALUES (%s,%s,%s)', (property_id, investor_id, float(amount)))
        cur.execute('UPDATE investors SET total_invested = COALESCE(total_invested,0)+%s WHERE investor_id=%s', (float(amount), investor_id))
    session['_success'] = 'Investment recorded'
    return redirect(url_for('investor_dashboard'))

# --- reports / complex queries (admin) ---
@app.route('/reports')
@require_roles('admin')
def reports():
    return render_template('reports.html')

# API ENDPOINTS
@app.route('/api/best_employees')
@require_roles('admin')
def api_best_employees():
    rows = fetchall('SELECT e.employee_id, e.display_name, COUNT(s.sale_id) as sales_count, COALESCE(SUM(s.final_price),0) as total_value FROM employees e LEFT JOIN sales s ON e.employee_id=s.employee_id GROUP BY e.employee_id ORDER BY sales_count DESC, total_value DESC LIMIT 20')
    return jsonify(rows)

@app.route('/api/top_locations')
@require_roles('admin')
def api_top_locations():
    rows = fetchall('SELECT city, COUNT(*) as total_props, ROUND(AVG(base_price),2) as avg_price FROM properties GROUP BY city ORDER BY total_props DESC LIMIT 20')
    return jsonify(rows)

@app.route('/api/user_distribution')
@require_roles('admin')
def api_user_distribution():
    """Get user role distribution for pie chart"""
    distribution = fetchall('''
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role 
        ORDER BY count DESC
    ''')
    return jsonify(distribution)

@app.route('/api/district_properties')
@require_roles('admin')
def api_district_properties():
    """Get property count by Bangladeshi districts"""
    districts = fetchall('''
        SELECT city as district, COUNT(*) as properties, 
               AVG(base_price) as avg_price
        FROM properties 
        WHERE city IS NOT NULL AND city != ''
        GROUP BY city 
        ORDER BY properties DESC 
        LIMIT 10
    ''')
    
    if not districts:
        districts = [
            {'district': 'Dhaka', 'properties': 125, 'avg_price': 12500000},
            {'district': 'Chattogram', 'properties': 85, 'avg_price': 8500000},
            {'district': 'Cumilla', 'properties': 45, 'avg_price': 4500000},
            {'district': 'Rajshahi', 'properties': 38, 'avg_price': 3800000},
            {'district': 'Sylhet', 'properties': 32, 'avg_price': 5200000},
            {'district': 'Khulna', 'properties': 28, 'avg_price': 3500000},
            {'district': 'Barishal', 'properties': 22, 'avg_price': 3200000},
            {'district': 'Rangpur', 'properties': 18, 'avg_price': 2800000},
            {'district': 'Mymensingh', 'properties': 15, 'avg_price': 3000000},
            {'district': "Cox's Bazar", 'properties': 12, 'avg_price': 7500000}
        ]
    
    return jsonify(districts)

@app.route('/api/monthly_revenue')
@require_roles('admin')
def api_monthly_revenue():
    """Get monthly revenue trend"""
    monthly_data = fetchall('''
        SELECT DATE_FORMAT(sale_date, '%Y-%m') as month,
               SUM(final_price) as revenue,
               COUNT(*) as sales
        FROM sales 
        WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
        ORDER BY month
    ''')
    
    if not monthly_data:
        monthly_data = [
            {'month': '2024-01', 'revenue': 32000000, 'sales': 18},
            {'month': '2024-02', 'revenue': 28000000, 'sales': 15},
            {'month': '2024-03', 'revenue': 35000000, 'sales': 22},
            {'month': '2024-04', 'revenue': 41000000, 'sales': 25},
            {'month': '2024-05', 'revenue': 45000000, 'sales': 28},
            {'month': '2024-06', 'revenue': 38000000, 'sales': 21},
            {'month': '2024-07', 'revenue': 42000000, 'sales': 24},
            {'month': '2024-08', 'revenue': 48000000, 'sales': 27},
            {'month': '2024-09', 'revenue': 51000000, 'sales': 30},
            {'month': '2024-10', 'revenue': 49000000, 'sales': 29},
            {'month': '2024-11', 'revenue': 53000000, 'sales': 31},
            {'month': '2024-12', 'revenue': 62000000, 'sales': 35}
        ]
    
    return jsonify(monthly_data)

@app.route('/api/property_status_stats')
@require_roles('admin')
def api_property_status_stats():
    """Get property status statistics"""
    stats = fetchall('''
        SELECT status, COUNT(*) as count 
        FROM properties 
        GROUP BY status
    ''')
    return jsonify(stats)

@app.route('/api/weekly_summary')
@require_roles('admin')
def api_weekly_summary():
    """Get weekly performance summary"""
    summary = {
        'revenue': 12000000,
        'revenue_change': 12,
        'new_properties': 24,
        'properties_change': 8,
        'new_enquiries': 18,
        'enquiries_change': -5,
        'sales_completed': 7,
        'sales_change': 15
    }
    return jsonify(summary)

@app.route('/api/financial_overview')
@require_roles('admin')
def api_financial_overview():
    """Get financial overview"""
    overview = {
        'total_revenue': 45000000,
        'company_commission': 9000000,
        'agent_commission': 900000,
        'net_profit': 7500000,
        'expenses': 750000
    }
    return jsonify(overview)

@app.route('/testdb')
def testdb():
    try:
        r = fetchone('SELECT 1 as ok')
        return 'DB OK'
    except Exception as e:
        return f'DB error: {e}', 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)