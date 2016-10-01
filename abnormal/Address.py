from BeautifulSoup import BeautifulSoup
import logging
import json
import re

class Address:
    def __init__(self, url, content):
        self.url = url
        self.content = content
        self.scripts = {}
        self.diff_scripts = []
        self.vars = {}
        self.set_data()

    def describe(self):
        return "Url: %s with content length: %s" % (self.url,len(self.content))

    def description(self):
        description = []
        description.append("Url: %s with content length: %s" % (self.url,len(self.content)))
        return description
    
    def describe_data(self):
        description = []
        for var in self.vars:
            description.append("\t%s : %s" % (var,self.vars[var]))
        return description

    def set_data(self):
        vars = self.parse_scripts()
        self.get_child("",vars,0)

    def parse_scripts(self):
        soup = BeautifulSoup(self.content)
        all_data = []
        res_dict = {}
        logging.debug("Parsing script for %s" % self.url)
        for script_part in soup.findAll('script'):
            try:
                json_data = re.findall('({.*})', script_part.string)
                for j_data in json_data:
                    try:
                        data = json.loads(j_data)
                        if len(data):
                            all_data.append(data)
                    except:
                        pass
            except:
                pass
        
        for data in all_data:
            res_dict.update(data)
        return res_dict
        
    ## Recursively populate self.vars map for js variables
    def get_child(self,name,child,place):
        if place == 5:
            return 
        if type(child) is dict:
            for leaf in child:
                if name != "":
                    use_name = name + "-" + str(leaf)
                else:
                    use_name = str(leaf)
                self.get_child(use_name,child[leaf],place + 1)
        else:
            self.vars[name] = child         

    def set_capture_file(self,filename):
        self.filename = filename
        