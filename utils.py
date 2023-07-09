import logging
from typing import Callable
from time import sleep
from random import random

class CountCalls: 
    def __init__(self, func: Callable): 
        self._count = 0 
        self._func = func 
    def __call__(self, *args, **kwargs): 
        self._count += 1 
        return self._func(*args,**kwargs) 
    @property 
    def call_count(self): 
        return self._count 
    
    def purge_count(self): 
        self._count = 0 
        return self._count
    

def exception_handler(func: Callable):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f'Exception in {func.__name__}: {e}')
            return None
    return inner

def retry(max_retries: int=3, wait_time: int=30, random_wait: bool=True):
    if random_wait:
        wait_time = random() * wait_time
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    retry_count += 1
                    logging.error(f'Exception in {func.__name__}: {e}, retrying in {round(wait_time)} seconds ({retry_count}/{max_retries})')
                    if retry_count == max_retries:
                        raise e 
                    sleep(wait_time)
        return wrapper
    return decorator