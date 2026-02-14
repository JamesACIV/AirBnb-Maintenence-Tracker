import os
from supabase import create_client, Client
from typing import Optional, List

def get_client() -> Client:
    """Get Supabase client."""
    supabase_url = os.environ.get('SUPABASE_URL', '')
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    return create_client(supabase_url, supabase_key)


class PropertyDAO:
    @staticmethod
    def create(data: dict) -> int:
        client = get_client()
        result = client.table('properties').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int) -> Optional[dict]:
        client = get_client()
        result = client.table('properties').select('*').eq('id', id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all() -> List[dict]:
        client = get_client()
        result = client.table('properties').select('*').order('name').execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict) -> None:
        client = get_client()
        client.table('properties').update(data).eq('id', id).execute()
    
    @staticmethod
    def delete(id: int) -> None:
        client = get_client()
        client.table('properties').delete().eq('id', id).execute()


class ContactDAO:
    @staticmethod
    def create(data: dict) -> int:
        client = get_client()
        result = client.table('contacts').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int) -> Optional[dict]:
        client = get_client()
        result = client.table('contacts').select('*').eq('id', id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all() -> List[dict]:
        client = get_client()
        result = client.table('contacts').select('*').order('name').execute()
        return result.data
    
    @staticmethod
    def get_by_type(service_type: str) -> List[dict]:
        client = get_client()
        result = client.table('contacts').select('*').eq('service_type', service_type).execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict) -> None:
        client = get_client()
        client.table('contacts').update(data).eq('id', id).execute()
    
    @staticmethod
    def delete(id: int) -> None:
        client = get_client()
        client.table('contacts').delete().eq('id', id).execute()


class TaskDAO:
    @staticmethod
    def create(data: dict) -> int:
        client = get_client()
        result = client.table('tasks').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int) -> Optional[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('id', id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all() -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').order('start_date', desc=True).execute()
        return result.data
    
    @staticmethod
    def get_by_property(property_id: int) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('property_id', property_id).execute()
        return result.data
    
    @staticmethod
    def get_unpaid() -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('payment_status', 'unpaid').execute()
        return result.data
    
    @staticmethod
    def get_incomplete() -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('completion_status', 'incomplete').execute()
        return result.data
    
    @staticmethod
    def get_recurring() -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('recurring', 'yes').execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict) -> None:
        client = get_client()
        client.table('tasks').update(data).eq('id', id).execute()
    
    @staticmethod
    def delete(id: int) -> None:
        client = get_client()
        client.table('tasks').delete().eq('id', id).execute()


class ReportingService:
    @staticmethod
    def monthly_breakdown(year: int, month: int) -> dict:
        client = get_client()
        month_str = f"{year}-{month:02d}%"
        
        result = client.table('tasks').select('property_id,cost,properties!inner(name)').like('start_date', month_str).execute()
        
        breakdown = {}
        total = 0
        for row in result.data:
            prop_name = row['properties']['name']
            cost = row['cost'] or 0
            breakdown[prop_name] = breakdown.get(prop_name, 0) + cost
            total += cost
        
        breakdown['total'] = total
        return breakdown
    
    @staticmethod
    def yearly_projection() -> float:
        client = get_client()
        
        result = client.table('tasks').select('cost,recurrence_interval').eq('recurring', 'yes').eq('completion_status', 'complete').execute()
        
        yearly_total = 0
        for row in result.data:
            cost = row['cost'] or 0
            interval = row.get('recurrence_interval', '')
            
            if interval == 'daily':
                yearly_total += cost * 365
            elif interval == 'weekly':
                yearly_total += cost * 52
            elif interval == 'monthly':
                yearly_total += cost * 12
            elif interval == 'yearly':
                yearly_total += cost
            else:
                yearly_total += cost
        
        return yearly_total
    
    @staticmethod
    def cost_summary() -> dict:
        client = get_client()
        
        paid_result = client.table('tasks').select('cost').eq('payment_status', 'paid').execute()
        unpaid_result = client.table('tasks').select('cost').eq('payment_status', 'unpaid').execute()
        
        paid = sum(r['cost'] or 0 for r in paid_result.data)
        unpaid = sum(r['cost'] or 0 for r in unpaid_result.data)
        
        return {'paid': paid, 'unpaid': unpaid, 'total': paid + unpaid}
