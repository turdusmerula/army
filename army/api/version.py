
class VersionException(Exception):
    def __init__(self, message):
        self.message = message


class Version():
    
    def __init__(self, value):
        self.major = None
        self.minor = None
        self.revision = None
        self.build = None
        self.dev = False
        
        version = value
        
#         if value=='dev':
#             self.dev = True
#             return 
        
        # extract build number
        if '-' in value:
            s = value.split('-', 1)
            self.build = s[1]
            value = s[0]
        
        if '.' in value:
            s = value.split('.')
            
            if(len(s)>3):
                raise VersionException(f"Invalid version {version}")
                
            try:
                if len(s)==3:
                    self.major = int(s[0])
                    self.minor = int(s[1])
                    self.revision = int(s[2])
                elif len(s)==2:
                    self.major = int(s[0])
                    self.minor = int(s[1])
            except Exception as e:
                raise VersionException(f"Invalid version {version}")
                
        else:
            try:
                self.major = int(value)
            except Exception as e:
                raise VersionException(f"Invalid version {version}")
        
        if self.build and ( self.major is None or self.minor is None or self.revision is None):
            raise VersionException(f"Invalid version {version}")
        elif self.build and self.build=="dev":
            self.dev = True
        
    def compare(self, version):
        l = [self.major, self.minor, self.revision, self.build]
        r = [version.major, version.minor, version.revision, version.build]
        
        if self.dev and version.dev:
            return 0
        elif self.dev and not version.dev:
            return -1
        elif not self.dev and version.dev:
            return 1
        
        res = 0
        for i in range(3):
            if res==0:
                if l[i] is None or r[i] is None:
                    res = 0
                elif l[i] is not None and r[i] is not None:
                    if l[i]<r[i]:
                        res = -1
                    if l[i]>r[i]:
                        res = 1
                
        if l[3] is not None and r[3] is None:
            return -1
        if l[3] is None and r[3] is not None:
            return 1
        if l[3] is not None and r[3] is not None:
            if l[3]<r[3]:
                return -1
            elif l[3]==r[3]:
                return 0
            elif l[3]>r[3]:
                return 1

        return res
    
    def __str__(self):
        version = f"{self.major}"
        if self.minor:
            version += f".{self.minor}"
        if self.revision:
            version += f".{self.revision}"
        if self.build:
            version += f"-{self.build}"
        return version

    def __eq__(self, other):
        return self.compare(other)==0
    
    def __lt__(self, other):
        return self.compare(other)<0

    def __le__(self, other):
        return self.compare(other)<=0
