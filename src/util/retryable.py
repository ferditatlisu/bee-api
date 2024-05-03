from typing import Any


def retry_return_with_exception(func: Any, max_retry: int = 15):
    retry_count =  0
    while True:
        try:
            return func()
        except Exception as ex:
            retry_count +=1
            if(retry_count > max_retry):
                raise ex