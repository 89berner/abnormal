from AutoVivification import AutoVivification
from Target import Target

class AB:
    def __init__(self, proxies):
        self.targets = {}
        self.observer_list = proxies
        
    def add_target(self,urls,options):
        name = urls[0]
        target = Target(name,urls,self.observer_list,options)
        self.targets[name] = target
        
    def process(self):
        for name in self.targets:
            print "Starting for target %s" % name
            self.targets[name].process()
            
    def report(self):
        for name in self.targets:
            self.targets[name].report()
            print "-" * 50

    def get_var_observers(target_name,name,value = ""):
        target = self.targets[name]
        target.get_var_observers(name,value)

    def check_var(target_name,name):
        target = self.targets[name]
        target.check_var(name)