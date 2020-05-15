from army.api.config import Config, ConfigException,  ConfigString, ConfigInt

def raised(func, *args,**kwargs):
    res = False
    try:
        func(*args,**kwargs)
    except Exception as e:
        res = type(e)
#         print(e)
    return res

s = ConfigString(value="value")
assert str(s)=="value"

# check raise with improper values
assert raised(ConfigString)==ConfigException
assert raised(ConfigString, 0)==ConfigException
assert raised(ConfigString, True)==ConfigException
assert raised(ConfigInt)==ConfigException
assert raised(ConfigInt, "aaaaa")==ConfigException

class TestConfig(Config):
    def __init__(self, value=None, parent=None):
        super(TestConfig, self).__init__(value, parent,
            fields={
                'value1': [ ConfigString, "v1" ],
                'value2': [ ConfigInt, 5 ],
                'value3': [ ConfigInt, 10 ]
            })
    

# no config set, check we are finding the default values
c1 = TestConfig() ;
assert str(c1.get('value1'))=='v1'
assert int(c1.get('value2'))==5
assert int(c1.get('value3'))==10

# values are set, check that we find them 
c2 = TestConfig(value={
    "value1": "v2",
    "value2": 1
    })
assert str(c2.get('value1'))=='v2'
assert int(c2.get('value2'))== 1
assert int(c2.get('value3'))== 10

# child configuration overrides 
c3 = TestConfig(value={
    "value2": 2
    }, parent=c2)
assert str(c3.get('value1'))=='v2'
assert int(c3.get('value2'))==2
assert int(c3.get('value3'))==10

class ConfigStringEnum(ConfigString):
    def __init__(self, value=None, parent=None):
        super(ConfigStringEnum, self).__init__(value, parent)

    def check(self):
        super(ConfigStringEnum, self).check() 
        if self.value() not in {"a", "b", "c"}:
            raise ConfigException(f"'{self.value()}': invalid value")

assert raised(ConfigStringEnum)==ConfigException
assert raised(ConfigStringEnum, "d")==ConfigException
c4 = ConfigStringEnum("a")
assert str(c4)=='a'


class TestConfig2(Config):
    def __init__(self, value=None, parent=None):
        super(TestConfig2, self).__init__(value, parent,
            fields={
                'config1': [ TestConfig, {} ],
                'config2': [ TestConfig, { "value1": "test" } ],
                'value1': [ ConfigStringEnum, "b" ]
            })
    

c5 = TestConfig2()
print("c5:", c5.expand())
assert str(c5.get("config1").get("value1"))=="v1"
assert int(c5.get("config1").get("value2"))==5
assert str(c5.get("config2").get("value1"))=="test"
assert int(c5.get("config2").get("value2"))==5
assert str(c5.get("value1"))=="b"

c6 = TestConfig2(value={
    "config1": {"value1": 'test1'},
    "value1": "c"
    })
print("c6:", c6.expand())
assert str(c6.get("config1").get("value1"))=="test1"
assert int(c6.get("config1").get("value2"))==5
assert str(c6.get("config2").get("value1"))=="test"
assert int(c6.get("config2").get("value2"))==5
assert str(c6.get("value1"))=="c"

c7 = TestConfig2(value={
    "config1": {"value2": 10},
    }, parent=c6)
print("c7:", c7.expand())
assert str(c7.get("config1").get("value1"))=="v1"
assert int(c7.get("config1").get("value2"))==10
assert str(c7.get("config2").get("value1"))=="test"
assert int(c7.get("config2").get("value2"))==5
assert str(c7.get("value1"))=="c"
