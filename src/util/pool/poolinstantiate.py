from datetime import datetime, timedelta
from src.util.pool.poolitem import PoolItem
from typing import Any, List
from threading import Lock

class PoolInstantiate():
    create_def: Any
    dispose: Any
    pool : List[PoolItem]
    def __init__(self, create_def, dispose) -> None:
        self.create_def = create_def
        self.dispose = dispose
        self._lock = Lock()
        self.pool = []
        
    def prepare(self, count: int):
        for _ in range(0, count):
            self.create()
        
    def get(self):
        with self._lock:
            for pool_item in self.pool:
                if pool_item.used_date < datetime.now() - timedelta(minutes=1):
                    pool_item.is_ready = True
                
                if pool_item.is_ready:
                    return pool_item.use()
                
            return self.create().use()
    
    def create(self):
        item = self.create_def()
        pool_item: PoolItem = PoolItem(item, self.dispose)
        self.pool.append(pool_item)
        
        return pool_item