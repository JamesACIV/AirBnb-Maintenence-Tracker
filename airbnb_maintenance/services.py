from datetime import datetime, timedelta
from typing import List, Dict
from .database import get_connection
from .models import Task

class ReportingService:
    @staticmethod
    def monthly_breakdown(year: int, month: int) -> Dict[str, float]:
        """Get total costs by property for a specific month."""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Format month with leading zero
        month_str = f"{year}-{month:02d}%"
        
        cursor.execute("""
            SELECT p.name, SUM(t.cost) as total
            FROM tasks t
            JOIN properties p ON t.property_id = p.id
            WHERE t.start_date LIKE ?
            GROUP BY p.name
        """, (month_str,))
        
        results = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Also get total
        cursor.execute("SELECT SUM(cost) FROM tasks WHERE start_date LIKE ?", (month_str,))
        total = cursor.fetchone()[0] or 0
        results['total'] = total
        
        conn.close()
        return results
    
    @staticmethod
    def yearly_projection() -> float:
        """Project yearly costs based on recurring tasks."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(cost) FROM tasks 
            WHERE recurring = 'yes' AND completion_status = 'complete'
        """)
        monthly_total = cursor.fetchone()[0] or 0
        
        # Project: daily * 365, weekly * 52, monthly * 12, yearly * 1
        cursor.execute("""
            SELECT recurrence_interval, cost FROM tasks 
            WHERE recurring = 'yes' AND completion_status = 'complete'
        """)
        
        yearly_total = 0
        for interval, cost in cursor.fetchall():
            if interval == 'daily':
                yearly_total += cost * 365
            elif interval == 'weekly':
                yearly_total += cost * 52
            elif interval == 'monthly':
                yearly_total += cost * 12
            elif interval == 'yearly':
                yearly_total += cost
            else:
                yearly_total += cost  # fallback
        
        conn.close()
        return yearly_total
    
    @staticmethod
    def cost_summary() -> Dict[str, float]:
        """Get total paid vs unpaid costs."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(cost) FROM tasks WHERE payment_status = 'paid'")
        paid = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(cost) FROM tasks WHERE payment_status = 'unpaid'")
        unpaid = cursor.fetchone()[0] or 0
        
        conn.close()
        return {'paid': paid, 'unpaid': unpaid, 'total': paid + unpaid}


class RecurringService:
    @staticmethod
    def get_next_occurrence(task: Task) -> str:
        """Calculate next occurrence date based on interval."""
        if not task.end_date:
            return ""
        
        try:
            end_date = datetime.strptime(task.end_date, "%Y-%m-%d")
        except ValueError:
            return ""
        
        if task.recurring == 'yes':
            if task.recurrence_interval == 'daily':
                next_date = end_date + timedelta(days=1)
            elif task.recurrence_interval == 'weekly':
                next_date = end_date + timedelta(weeks=1)
            elif task.recurrence_interval == 'monthly':
                next_date = end_date + timedelta(days=30)
            elif task.recurrence_interval == 'yearly':
                next_date = end_date + timedelta(days=365)
            else:
                return ""
            return next_date.strftime("%Y-%m-%d")
        
        return ""
    
    @staticmethod
    def generate_next_task(original_task: Task) -> Task:
        """Create a new task based on the recurring pattern."""
        next_date = RecurringService.get_next_occurrence(original_task)
        
        return Task(
            property_id=original_task.property_id,
            contact_id=original_task.contact_id,
            description=original_task.description,
            start_date=original_task.end_date,
            end_date=next_date,
            cost=original_task.cost,
            payment_status='unpaid',
            completion_status='incomplete',
            recurring=original_task.recurring,
            recurrence_interval=original_task.recurrence_interval,
            notes=original_task.notes
        )
