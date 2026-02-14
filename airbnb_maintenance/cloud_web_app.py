from flask import Flask, jsonify, request, render_template, session
import os
from functools import wraps

print("Starting app...")

try:
    from airbnb_maintenance import cloud_db
    from airbnb_maintenance.cloud_db import AuthService
    print("Imported cloud_db")
except Exception as e:
    print(f"Error importing cloud_db: {e}")
    raise

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

print(f"SUPABASE_URL set: {bool(os.environ.get('SUPABASE_URL'))}")
print(f"SUPABASE_KEY set: {bool(os.environ.get('SUPABASE_KEY'))}")

PropertyDAO = cloud_db.PropertyDAO
ContactDAO = cloud_db.ContactDAO
TaskDAO = cloud_db.TaskDAO
ReportingService = cloud_db.ReportingService


def get_user_id():
    """Get user_id from session."""
    return session.get('user_id')


# Auth routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('login.html')


@app.route('/login')
def login_page():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('login.html')


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        result = AuthService.sign_up(data.get('email'), data.get('password'))
        return jsonify({'message': 'Signup successful. Please check your email to verify.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    try:
        result = AuthService.sign_in(data.get('email'), data.get('password'))
        # Convert user id to string
        user_id = str(result.user.id) if result.user else None
        session['user_id'] = user_id
        session['user'] = result.user.email
        return jsonify({'message': 'Login successful', 'user': result.user.email})
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({'user': session.get('user'), 'user_id': session.get('user_id')})
    return jsonify({'user': None})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'logged_in': 'user_id' in session})


# Properties
@app.route('/api/properties', methods=['GET'])
def get_properties():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        return jsonify(PropertyDAO.get_all(user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    prop = PropertyDAO.get_by_id(id, user_id)
    return jsonify(prop)

@app.route('/api/properties', methods=['POST'])
def create_property():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    pid = PropertyDAO.create({
        'name': data.get('name'),
        'address': data.get('address'),
        'status': data.get('status', 'active')
    }, user_id)
    return jsonify({'id': pid}), 201

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    PropertyDAO.update(id, {
        'name': data.get('name'),
        'address': data.get('address'),
        'status': data.get('status')
    }, user_id)
    return jsonify({'success': True})

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    PropertyDAO.delete(id, user_id)
    return jsonify({'success': True})


# Contacts
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    service_type = request.args.get('service_type')
    if service_type:
        return jsonify(ContactDAO.get_by_type(service_type, user_id))
    return jsonify(ContactDAO.get_all(user_id))

@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    contact = ContactDAO.get_by_id(id, user_id)
    return jsonify(contact)

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    cid = ContactDAO.create({
        'name': data.get('name'),
        'company': data.get('company', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'service_type': data.get('service_type', '')
    }, user_id)
    return jsonify({'id': cid}), 201

@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    ContactDAO.update(id, {
        'name': data.get('name'),
        'company': data.get('company', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'service_type': data.get('service_type', '')
    }, user_id)
    return jsonify({'success': True})

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    ContactDAO.delete(id, user_id)
    return jsonify({'success': True})


# Tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    property_id = request.args.get('property_id')
    status = request.args.get('status')
    
    if property_id:
        return jsonify(TaskDAO.get_by_property(int(property_id), user_id))
    elif status == 'unpaid':
        return jsonify(TaskDAO.get_unpaid(user_id))
    elif status == 'incomplete':
        return jsonify(TaskDAO.get_incomplete(user_id))
    elif status == 'recurring':
        return jsonify(TaskDAO.get_recurring(user_id))
    return jsonify(TaskDAO.get_all(user_id))

@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    task = TaskDAO.get_by_id(id, user_id)
    return jsonify(task)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    tid = TaskDAO.create({
        'property_id': data.get('property_id'),
        'contact_id': data.get('contact_id'),
        'description': data.get('description'),
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'cost': data.get('cost', 0),
        'payment_status': data.get('payment_status', 'unpaid'),
        'completion_status': data.get('completion_status', 'incomplete'),
        'recurring': data.get('recurring', 'no'),
        'recurrence_interval': data.get('recurrence_interval', ''),
        'notes': data.get('notes', '')
    }, user_id)
    return jsonify({'id': tid}), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    TaskDAO.update(id, {
        'property_id': data.get('property_id'),
        'contact_id': data.get('contact_id'),
        'description': data.get('description'),
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'cost': data.get('cost', 0),
        'payment_status': data.get('payment_status'),
        'completion_status': data.get('completion_status'),
        'recurring': data.get('recurring', 'no'),
        'recurrence_interval': data.get('recurrence_interval', ''),
        'notes': data.get('notes', '')
    }, user_id)
    return jsonify({'success': True})

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    TaskDAO.delete(id, user_id)
    return jsonify({'success': True})


# Reports
@app.route('/api/reports/summary', methods=['GET'])
def get_summary():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(ReportingService.cost_summary(user_id))

@app.route('/api/reports/projection', methods=['GET'])
def get_projection():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'yearly_projection': ReportingService.yearly_projection(user_id)})

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        from datetime import datetime
        now = datetime.now()
        year, month = now.year, now.month
    return jsonify(ReportingService.monthly_breakdown(year, month, user_id))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
