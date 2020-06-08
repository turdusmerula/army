
class A(object):
    def __init__(self):
        self._value = "test"
    
    @property
    def value(self):
        return self._value

class B(A):
    def __init__(self):
        pass
    
    @property
    def value(self):
        return "toto"

a = A()
print(a.value)

b = B()
print(b.value)
