import tornado.template as template

class ArmyTemplate(template.Template):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        with open(self.source, "r") as file:
            content = file.read()
        
        super(ArmyTemplate, self).__init__(content)
    
    def generate(self, **kwargs)->bytes:
        res = template.Template.generate(self, **kwargs)
        file = open(self.filename, "w") 
        file.write(res.decode("utf-8"))
        file.close()
