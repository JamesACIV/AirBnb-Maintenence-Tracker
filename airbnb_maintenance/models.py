from dataclasses import dataclass
from typing import Optional

@dataclass
class Property:
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    status: str = "active"

@dataclass
class Contact:
    id: Optional[int] = None
    name: str = ""
    company: str = ""
    phone: str = ""
    email: str = ""
    service_type: str = ""

@dataclass
class Task:
    id: Optional[int] = None
    property_id: Optional[int] = None
    contact_id: Optional[int] = None
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    cost: float = 0
    payment_status: str = "unpaid"
    completion_status: str = "incomplete"
    recurring: str = "no"
    recurrence_interval: str = ""
    notes: str = ""
