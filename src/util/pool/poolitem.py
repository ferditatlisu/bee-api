from datetime import datetime, timedelta
from typing import Any


class PoolItem():
    item: Any
    is_ready: bool
    dispose: Any
    used_date: datetime
    def __init__(self, item, dispose) -> None:
        self.item = item
        self.dispose = dispose
        self.is_ready = True
        self.used_date = datetime.now() - timedelta(minutes=2)
    
    def get_item(self):
        return self.item
    
    def use(self):
        self.is_ready = False
        self.used_date = datetime.now()
        
        return self
    
    def release(self):
        self.dispose(self.item)
        self.used_date = datetime.now()
        self.is_ready = True