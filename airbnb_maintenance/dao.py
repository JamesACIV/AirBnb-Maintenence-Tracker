import sqlite3
from typing import Optional, List
from .database import get_connection
from .models import Property, Contact, Task

class PropertyDAO:
    @staticmethod
    def create(property: Property) -> Optional[int]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO properties (name, address, status) VALUES (?, ?, ?)",
            (property.name, property.address, property.status)
        )
        conn.commit()
        pid = cursor.lastrowid
        conn.close()
        return pid
    
    @staticmethod
    def get_by_id(id: int) -> Optional[Property]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Property(id=row[0], name=row[1], address=row[2], status=row[3])
        return None
    
    @staticmethod
    def get_all() -> List[Property]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [Property(id=r[0], name=r[1], address=r[2], status=r[3]) for r in rows]
    
    @staticmethod
    def update(property: Property) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE properties SET name=?, address=?, status=? WHERE id=?",
            (property.name, property.address, property.status, property.id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM properties WHERE id=?", (id,))
        conn.commit()
        conn.close()


class ContactDAO:
    @staticmethod
    def create(contact: Contact) -> Optional[int]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, company, phone, email, service_type) VALUES (?, ?, ?, ?, ?)",
            (contact.name, contact.company, contact.phone, contact.email, contact.service_type)
        )
        conn.commit()
        cid = cursor.lastrowid
        conn.close()
        return cid
    
    @staticmethod
    def get_by_id(id: int) -> Optional[Contact]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Contact(id=row[0], name=row[1], company=row[2], phone=row[3], email=row[4], service_type=row[5])
        return None
    
    @staticmethod
    def get_all() -> List[Contact]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [Contact(id=r[0], name=r[1], company=r[2], phone=r[3], email=r[4], service_type=r[5]) for r in rows]
    
    @staticmethod
    def get_by_type(service_type: str) -> List[Contact]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE service_type = ?", (service_type,))
        rows = cursor.fetchall()
        conn.close()
        return [Contact(id=r[0], name=r[1], company=r[2], phone=r[3], email=r[4], service_type=r[5]) for r in rows]
    
    @staticmethod
    def update(contact: Contact) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts SET name=?, company=?, phone=?, email=?, service_type=? WHERE id=?",
            (contact.name, contact.company, contact.phone, contact.email, contact.service_type, contact.id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id=?", (id,))
        conn.commit()
        conn.close()


class TaskDAO:
    @staticmethod
    def create(task: Task) -> Optional[int]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (property_id, contact_id, description, start_date, end_date, 
               cost, payment_status, completion_status, recurring, recurrence_interval, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task.property_id, task.contact_id, task.description, task.start_date, task.end_date,
             task.cost, task.payment_status, task.completion_status, task.recurring, 
             task.recurrence_interval, task.notes)
        )
        conn.commit()
        tid = cursor.lastrowid
        conn.close()
        return tid
    
    @staticmethod
    def get_by_id(id: int) -> Optional[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Task(id=row[0], property_id=row[1], contact_id=row[2], description=row[3],
                       start_date=row[4], end_date=row[5], cost=row[6], payment_status=row[7],
                       completion_status=row[8], recurring=row[9], recurrence_interval=row[10], notes=row[11])
        return None
    
    @staticmethod
    def get_all() -> List[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY start_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], property_id=r[1], contact_id=r[2], description=r[3],
                   start_date=r[4], end_date=r[5], cost=r[6], payment_status=r[7],
                   completion_status=r[8], recurring=r[9], recurrence_interval=r[10], notes=r[11]) for r in rows]
    
    @staticmethod
    def get_by_property(property_id: int) -> List[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE property_id = ?", (property_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], property_id=r[1], contact_id=r[2], description=r[3],
                   start_date=r[4], end_date=r[5], cost=r[6], payment_status=r[7],
                   completion_status=r[8], recurring=r[9], recurrence_interval=r[10], notes=r[11]) for r in rows]
    
    @staticmethod
    def get_unpaid() -> List[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE payment_status = 'unpaid'")
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], property_id=r[1], contact_id=r[2], description=r[3],
                   start_date=r[4], end_date=r[5], cost=r[6], payment_status=r[7],
                   completion_status=r[8], recurring=r[9], recurrence_interval=r[10], notes=r[11]) for r in rows]
    
    @staticmethod
    def get_incomplete() -> List[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE completion_status = 'incomplete'")
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], property_id=r[1], contact_id=r[2], description=r[3],
                   start_date=r[4], end_date=r[5], cost=r[6], payment_status=r[7],
                   completion_status=r[8], recurring=r[9], recurrence_interval=r[10], notes=r[11]) for r in rows]
    
    @staticmethod
    def get_recurring() -> List[Task]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE recurring = 'yes'")
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], property_id=r[1], contact_id=r[2], description=r[3],
                   start_date=r[4], end_date=r[5], cost=r[6], payment_status=r[7],
                   completion_status=r[8], recurring=r[9], recurrence_interval=r[10], notes=r[11]) for r in rows]
    
    @staticmethod
    def update(task: Task) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE tasks SET property_id=?, contact_id=?, description=?, start_date=?, end_date=?,
               cost=?, payment_status=?, completion_status=?, recurring=?, recurrence_interval=?, notes=? 
               WHERE id=?""",
            (task.property_id, task.contact_id, task.description, task.start_date, task.end_date,
             task.cost, task.payment_status, task.completion_status, task.recurring,
             task.recurrence_interval, task.notes, task.id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
        conn.commit()
        conn.close()
