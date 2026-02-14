from datetime import datetime, timedelta
from models import Property, Contact, Task
from dao import PropertyDAO, ContactDAO, TaskDAO
from services import ReportingService, RecurringService
from database import init_db

def seed_data():
    """Add sample data to the database."""
    print("Seeding sample data...")
    
    # Create properties
    p1 = Property(name="Downtown Loft", address="123 Main St, New York, NY", status="active")
    p2 = Property(name="Beach House", address="456 Ocean Dr, Miami, FL", status="active")
    p3 = Property(name="Mountain Cabin", address="789 Pine Rd, Denver, CO", status="inactive")
    
    p1_id = PropertyDAO.create(p1)
    p2_id = PropertyDAO.create(p2)
    p3_id = PropertyDAO.create(p3)
    print(f"Created 3 properties (IDs: {p1_id}, {p2_id}, {p3_id})")
    
    # Create contacts
    c1 = Contact(name="John Smith", company="Smith Plumbing", phone="555-0101", email="john@smithplumbing.com", service_type="plumber")
    c2 = Contact(name="Sarah Johnson", company="Johnson Electric", phone="555-0102", email="sarah@johnsonelectric.com", service_type="electrician")
    c3 = Contact(name="Mike Brown", company="Brown HVAC", phone="555-0103", email="mike@brownhvac.com", service_type="hvac")
    c4 = Contact(name="Lisa Davis", company="Davis Landscaping", phone="555-0104", email="lisa@davislscape.com", service_type="landscaping")
    c5 = Contact(name="Tom Wilson", company="Wilson Repairs", phone="555-0105", email="tom@wilsonrepairs.com", service_type="general")
    
    for c in [c1, c2, c3, c4, c5]:
        ContactDAO.create(c)
    print("Created 5 contacts")
    
    # Create tasks
    today = datetime.now().strftime("%Y-%m-%d")
    last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    tasks = [
        Task(property_id=p1_id, contact_id=1, description="Fix leaky faucet in kitchen", 
             start_date=last_month, end_date=today, cost=150, payment_status="paid", 
             completion_status="complete", recurring="no", notes="Kitchen sink"),
        Task(property_id=p1_id, contact_id=2, description="Electrical inspection", 
             start_date=last_month, end_date=last_month, cost=200, payment_status="paid", 
             completion_status="complete", recurring="no"),
        Task(property_id=p2_id, contact_id=1, description="Monthly pool maintenance", 
             start_date=last_month, end_date=next_month, cost=300, payment_status="unpaid", 
             completion_status="incomplete", recurring="yes", recurrence_interval="monthly"),
        Task(property_id=p2_id, contact_id=4, description="Lawn mowing", 
             start_date=last_month, end_date=last_month, cost=100, payment_status="paid", 
             completion_status="complete", recurring="yes", recurrence_interval="weekly"),
        Task(property_id=p1_id, contact_id=5, description="General repairs", 
             start_date=today, end_date=today, cost=75, payment_status="unpaid", 
             completion_status="incomplete", recurring="no", notes="Various small fixes"),
        Task(property_id=p3_id, contact_id=3, description="Heater inspection", 
             start_date=last_month, end_date=last_month, cost=180, payment_status="paid", 
             completion_status="complete", recurring="yes", recurrence_interval="yearly"),
        Task(property_id=p2_id, contact_id=2, description="Install outdoor lights", 
             start_date=today, end_date=today, cost=250, payment_status="unpaid", 
             completion_status="incomplete", recurring="no"),
        Task(property_id=p1_id, contact_id=1, description="Emergency pipe repair", 
             start_date=last_month, end_date=last_month, cost=400, payment_status="paid", 
             completion_status="complete", recurring="no"),
    ]
    
    for t in tasks:
        TaskDAO.create(t)
    print("Created 8 tasks")
    print("Seeding complete!")


def show_report():
    """Display cost reports."""
    print("\n=== COST SUMMARY ===")
    summary = ReportingService.cost_summary()
    print(f"Paid:   ${summary['paid']:.2f}")
    print(f"Unpaid: ${summary['unpaid']:.2f}")
    print(f"Total:  ${summary['total']:.2f}")
    
    print("\n=== YEARLY PROJECTION ===")
    projection = ReportingService.yearly_projection()
    print(f"Projected yearly cost: ${projection:.2f}")
    
    print("\n=== MONTHLY BREAKDOWN (Current Month) ===")
    now = datetime.now()
    breakdown = ReportingService.monthly_breakdown(now.year, now.month)
    for prop, cost in breakdown.items():
        if prop != 'total':
            print(f"  {prop}: ${cost:.2f}")
    print(f"  Total: ${breakdown.get('total', 0):.2f}")


def show_data():
    """Display all data in database."""
    print("\n=== PROPERTIES ===")
    for p in PropertyDAO.get_all():
        print(f"  {p.id}: {p.name} - {p.address} ({p.status})")
    
    print("\n=== CONTACTS ===")
    for c in ContactDAO.get_all():
        print(f"  {c.id}: {c.name} ({c.service_type}) - {c.phone}")
    
    print("\n=== TASKS ===")
    for t in TaskDAO.get_all():
        print(f"  {t.id}: {t.description} - ${t.cost} ({t.payment_status}, {t.completion_status})")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command>")
        print("Commands: init, seed, report, show, all")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init_db()
    elif cmd == "seed":
        seed_data()
    elif cmd == "report":
        show_report()
    elif cmd == "show":
        show_data()
    elif cmd == "all":
        init_db()
        seed_data()
        show_data()
        show_report()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
