
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
        
        if value=='dev':
            self.dev = True
            return 
        
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
    
    # return -1 if self<version
    # return 0 if self==version
    # return 1 if self>version
    def compare(self, version):
        l = self
        r = version
        
        if l.dev and r.dev:
            return 0
        elif l.dev and not r.dev:
            return 1
        elif not l.dev and r.dev:
            return -1
        
        if l.major>r.major:
            return 1
        elif l.major<r.major:
            return -1
        
        lminor = l.minor
        if lminor is None:
            lminor = 0
        rminor = r.minor
        if rminor is None:
            rminor = 0
        if lminor>rminor:
            return 1
        elif lminor<rminor:
            return -1

        lrevision = l.revision
        if lrevision is None:
            lrevision = 0
        rrevision = r.revision
        if rrevision is None:
            rrevision = 0
        if lrevision>rrevision:
            return 1
        elif lrevision<rrevision:
            return -1

        if l.build or r.build:
            lbuild = l.build
            if lbuild is None:
                lbuild = ''
            rbuild = r.build
            if rbuild is None:
                rbuild = ''
            if lbuild>rbuild:
                return 1
            elif lbuild<rbuild:
                return -1
        
        return 0

    def __str__(self):
        if self.dev:
            return 'dev'
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
