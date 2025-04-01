# app/utils.py (create new file)
import pytz
from datetime import datetime

def utc_to_eat(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to East Africa Time (EAT)"""
    if not utc_dt:
        return None
    
    utc = pytz.utc
    eat = pytz.timezone('Africa/Nairobi')
    return utc.localize(utc_dt).astimezone(eat)