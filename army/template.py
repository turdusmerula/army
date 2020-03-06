import tornado.template as template

class ArmyTemplate(template.Template):
    def __init__(self, filename):
        self.filename = filename
        file = open(filename, "r") 
        content = file.read()
        super(ArmyTemplate, self).__init__(content)
    
    def generate(self, **kwargs)->bytes:
        res = template.Template.generate(self, **kwargs)
        file = open(self.filename, "w") 
        file.write(res.decode("utf-8"))
        
