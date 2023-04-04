class CountCalls: 
    def __init__(self, func): 
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