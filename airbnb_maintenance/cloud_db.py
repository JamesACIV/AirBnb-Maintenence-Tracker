import os
from supabase import create_client, Client
from typing import Optional, List

def get_client() -> Client:
    supabase_url = os.environ.get('SUPABASE_URL', '')
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    return create_client(supabase_url, supabase_key)


class AuthService:
    @staticmethod
    def sign_up(email: str, password: str):
        client = get_client()
        return client.auth.sign_up({"email": email, "password": password})
    
    @staticmethod
    def sign_in(email: str, password: str):
        client = get_client()
        return client.auth.sign_in_with_password({"email": email, "password": password})
    
    @staticmethod
    def sign_out():
        client = get_client()
        return client.auth.sign_out()
    
    @staticmethod
    def get_user(token: str):
        client = get_client()
        return client.auth.get_user(token)


class PropertyDAO:
    @staticmethod
    def create(data: dict, user_id: str) -> int:
        client = get_client()
        data['user_id'] = user_id
        result = client.table('properties').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int, user_id: str) -> Optional[dict]:
        client = get_client()
        result = client.table('properties').select('*').eq('id', id).eq('user_id', user_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('properties').select('*').eq('user_id', user_id).order('name').execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict, user_id: str) -> None:
        client = get_client()
        client.table('properties').update(data).eq('id', id).eq('user_id', user_id).execute()
    
    @staticmethod
    def delete(id: int, user_id: str) -> None:
        client = get_client()
        client.table('properties').delete().eq('id', id).eq('user_id', user_id).execute()


class ContactDAO:
    @staticmethod
    def create(data: dict, user_id: str) -> int:
        client = get_client()
        data['user_id'] = user_id
        result = client.table('contacts').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int, user_id: str) -> Optional[dict]:
        client = get_client()
        result = client.table('contacts').select('*').eq('id', id).eq('user_id', user_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('contacts').select('*').eq('user_id', user_id).order('name').execute()
        return result.data
    
    @staticmethod
    def get_by_type(service_type: str, user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('contacts').select('*').eq('service_type', service_type).eq('user_id', user_id).execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict, user_id: str) -> None:
        client = get_client()
        client.table('contacts').update(data).eq('id', id).eq('user_id', user_id).execute()
    
    @staticmethod
    def delete(id: int, user_id: str) -> None:
        client = get_client()
        client.table('contacts').delete().eq('id', id).eq('user_id', user_id).execute()


class TaskDAO:
    @staticmethod
    def create(data: dict, user_id: str) -> int:
        client = get_client()
        data['user_id'] = user_id
        result = client.table('tasks').insert(data).execute()
        return result.data[0]['id']
    
    @staticmethod
    def get_by_id(id: int, user_id: str) -> Optional[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('id', id).eq('user_id', user_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('user_id', user_id).order('start_date', desc=True).execute()
        return result.data
    
    @staticmethod
    def get_by_property(property_id: int, user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('property_id', property_id).eq('user_id', user_id).execute()
        return result.data
    
    @staticmethod
    def get_unpaid(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('payment_status', 'unpaid').eq('user_id', user_id).execute()
        return result.data
    
    @staticmethod
    def get_incomplete(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('completion_status', 'incomplete').eq('user_id', user_id).execute()
        return result.data
    
    @staticmethod
    def get_recurring(user_id: str) -> List[dict]:
        client = get_client()
        result = client.table('tasks').select('*').eq('recurring', 'yes').eq('user_id', user_id).execute()
        return result.data
    
    @staticmethod
    def update(id: int, data: dict, user_id: str) -> None:
        client = get_client()
        client.table('tasks').update(data).eq('id', id).eq('user_id', user_id).execute()
    
    @staticmethod
    def delete(id: int, user_id: str) -> None:
        client = get_client()
        client.table('tasks').delete().eq('id', id).eq('user_id', user_id).execute()


class ReportingService:
    @staticmethod
    def monthly_breakdown(year: int, month: int, user_id: str) -> dict:
        client = get_client()
        month_str = f"{year}-{month:02d}%"
        
        result = client.table('tasks').select('property_id,cost,properties!inner(name)').like('start_date', month_str).eq('tasks.user_id', user_id).execute()
        
        breakdown = {}
        total = 0
        for row in result.data:
            if row.get('properties'):
                prop_name = row['properties']['name']
                cost = row['cost'] or 0
                breakdown[prop_name] = breakdown.get(prop_name, 0) + cost
                total += cost
        
        breakdown['total'] = total
        return breakdown
    
    @staticmethod
    def yearly_projection(user_id: str) -> float:
        client = get_client()
        
        result = client.table('tasks').select('cost,recurrence_interval').eq('recurring', 'yes').eq('completion_status', 'complete').eq('user_id', user_id).execute()
        
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
    def cost_summary(user_id: str) -> dict:
        client = get_client()
        
        paid_result = client.table('tasks').select('cost').eq('payment_status', 'paid').eq('user_id', user_id).execute()
        unpaid_result = client.table('tasks').select('cost').eq('payment_status', 'unpaid').eq('user_id', user_id).execute()
        
        paid = sum(r['cost'] or 0 for r in paid_result.data)
        unpaid = sum(r['cost'] or 0 for r in unpaid_result.data)
        
        return {'paid': paid, 'unpaid': unpaid, 'total': paid + unpaid}
