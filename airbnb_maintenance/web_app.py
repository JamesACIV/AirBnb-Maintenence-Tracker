from flask import Flask, jsonify, request, render_template
from airbnb_maintenance import (
    PropertyDAO, ContactDAO, TaskDAO, ReportingService, RecurringService,
    Property, Contact, Task
)

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

def serialize(obj):
    """Convert dataclass to dict for JSON serialization."""
    if obj is None:
        return None
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    result = {}
    for field in ['id', 'name', 'address', 'status', 'company', 'phone', 'email', 
                  'service_type', 'property_id', 'contact_id', 'description', 
                  'start_date', 'end_date', 'cost', 'payment_status', 
                  'completion_status', 'recurring', 'recurrence_interval', 'notes']:
        if hasattr(obj, field):
            result[field] = getattr(obj, field)
    return result


# Properties
@app.route('/api/properties', methods=['GET'])
def get_properties():
    return jsonify(serialize(PropertyDAO.get_all()))

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    prop = PropertyDAO.get_by_id(id)
    return jsonify(serialize(prop))

@app.route('/api/properties', methods=['POST'])
def create_property():
    data = request.json
    prop = Property(
        name=data.get('name'),
        address=data.get('address'),
        status=data.get('status', 'active')
    )
    pid = PropertyDAO.create(prop)
    return jsonify({'id': pid}), 201

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    data = request.json
    prop = Property(
        id=id,
        name=data.get('name'),
        address=data.get('address'),
        status=data.get('status')
    )
    PropertyDAO.update(prop)
    return jsonify({'success': True})

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    PropertyDAO.delete(id)
    return jsonify({'success': True})


# Contacts
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    service_type = request.args.get('service_type')
    if service_type:
        return jsonify(serialize(ContactDAO.get_by_type(service_type)))
    return jsonify(serialize(ContactDAO.get_all()))

@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    contact = ContactDAO.get_by_id(id)
    return jsonify(serialize(contact))

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    contact = Contact(
        name=data.get('name'),
        company=data.get('company', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        service_type=data.get('service_type', '')
    )
    cid = ContactDAO.create(contact)
    return jsonify({'id': cid}), 201

@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    data = request.json
    contact = Contact(
        id=id,
        name=data.get('name'),
        company=data.get('company', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        service_type=data.get('service_type', '')
    )
    ContactDAO.update(contact)
    return jsonify({'success': True})

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    ContactDAO.delete(id)
    return jsonify({'success': True})


# Tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    property_id = request.args.get('property_id')
    status = request.args.get('status')
    
    if property_id:
        return jsonify(serialize(TaskDAO.get_by_property(int(property_id))))
    elif status == 'unpaid':
        return jsonify(serialize(TaskDAO.get_unpaid()))
    elif status == 'incomplete':
        return jsonify(serialize(TaskDAO.get_incomplete()))
    elif status == 'recurring':
        return jsonify(serialize(TaskDAO.get_recurring()))
    return jsonify(serialize(TaskDAO.get_all()))

@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = TaskDAO.get_by_id(id)
    return jsonify(serialize(task))

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    task = Task(
        property_id=data.get('property_id'),
        contact_id=data.get('contact_id'),
        description=data.get('description'),
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        cost=data.get('cost', 0),
        payment_status=data.get('payment_status', 'unpaid'),
        completion_status=data.get('completion_status', 'incomplete'),
        recurring=data.get('recurring', 'no'),
        recurrence_interval=data.get('recurrence_interval', ''),
        notes=data.get('notes', '')
    )
    tid = TaskDAO.create(task)
    return jsonify({'id': tid}), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.json
    task = Task(
        id=id,
        property_id=data.get('property_id'),
        contact_id=data.get('contact_id'),
        description=data.get('description'),
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        cost=data.get('cost', 0),
        payment_status=data.get('payment_status'),
        completion_status=data.get('completion_status'),
        recurring=data.get('recurring', 'no'),
        recurrence_interval=data.get('recurrence_interval', ''),
        notes=data.get('notes', '')
    )
    TaskDAO.update(task)
    return jsonify({'success': True})

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    TaskDAO.delete(id)
    return jsonify({'success': True})


# Reports
@app.route('/api/reports/summary', methods=['GET'])
def get_summary():
    return jsonify(ReportingService.cost_summary())

@app.route('/api/reports/projection', methods=['GET'])
def get_projection():
    return jsonify({'yearly_projection': ReportingService.yearly_projection()})

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        from datetime import datetime
        now = datetime.now()
        year, month = now.year, now.month
    return jsonify(ReportingService.monthly_breakdown(year, month))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
