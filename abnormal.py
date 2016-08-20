import requests
from time import sleep
from lxml.html.diff import htmldiff
import pprint
import re
import sys
import traceback
from sets import Set
import requests
import json
from BeautifulSoup import BeautifulSoup
import re
import proxies

def parse_scripts(content):
    soup = BeautifulSoup(content)
    all_data = []
    res_dict = {}
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

class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

pp = pprint.PrettyPrinter(indent=4)

results = AutoVivification()
urls = []
count = 0

try:
    file = open('list.txt', 'r')
    for line in file:
        urls.append(line)
except:
    urls.append("https://www.instagram.com/")
    
class AB:
    def __init__(self):
        self.targets = []
        
    def add_target(self,name,urls,max_ips):
        target = Target(name,urls,self.observer_list,max_ips)
        self.targets.append(target)
        
    def process(self):
        for target in self.targets:
            print "Starting for target %s" % target.name
            target.process()
            
    def report(self):
        for target in self.targets:
            target.report()
            print "-" * 50
    
    def get_proxies(self, n_proxies = 5, threads = 10):
        self.observer_list = proxies.check_proxies(threads,n_proxies)
        
class Target:
    def __init__(self, name, urls, ip_list, max_ips):
        self.urls = urls
        self.possible_observers = []
        self.observers = []
        for ip in ip_list:
            self.possible_observers.append(Observer(ip,urls))
        self.name    = name
        self.max_ips = max_ips
        self.diff_vars    = {}
        self.missing_vars = {}
        for url in urls:
            self.diff_vars[url] = Set()
            self.missing_vars[url] = Set()
        self.compared_results = AutoVivification()

    def process(self):
        count = 0
        for observer in self.possible_observers:
            status = observer.request()
            
            if (status == 1): #Working observers
                self.observers.append(observer)
            
            count = count + status
            if count == self.max_ips:
                break
        print "Got %s working observers" % count
        
        compared = AutoVivification()
        for url in self.urls:
            for observer1 in self.observers:
                for observer2 in self.observers:
                    if (observer1.ip != observer2.ip):
                        self.check_vars(observer1,observer2,url)
            self.compare(url)
            break
                        
    def check_vars(self,observer1,observer2,url):
        vars1 = observer1.get_address(url).vars
        vars2 = observer2.get_address(url).vars
        for var in vars1:
            if (var not in vars2):
                self.missing_vars[url].add(var)
            elif (vars1[var] != vars2[var]):
                self.diff_vars[url].add(var)
                
    def compare(self,url):
        for missing in self.missing_vars[url]:
            self.compared_results[url]['missing_total'][missing] = 0
            for observer in self.observers:
                addr = observer.get_address(url)
                if missing not in addr.vars:
                    #print "%s is missing" % missing
                    self.compared_results[url]['missing_total'][missing] += 1
        for diff_var in self.diff_vars[url]:
            self.compared_results[url]['diff_vars'][diff_var] = Set()
            for observer in self.observers:
                addr = observer.get_address(url)
                if diff_var in addr.vars:
                    self.compared_results[url]['diff_vars'][diff_var].add(addr.vars[diff_var])

    def report(self):
        for url in self.compared_results:
            print "For %s" % url
            for val in self.compared_results[url]:
                print "%s: %s" % (val,self.compared_results[url][val])
        
        
class Observer:
    def __init__(self, ip, urls):
        self.ip = ip
        self.urls = urls
        self.address_map = {}
        self.session = requests.Session()
        
    def request(self):
        status = 0
        for url in urls:
            status = status + self.get_url(url)
        if status / len(urls) == 1:
            return 1
        else:
            return 0
        
    def get_url(self,url):
        proxies = {'http' : "http://%s" % self.ip, 'https': "https://%s" % self.ip}
        try:
            r = self.session.get(url, proxies=proxies, verify=False, timeout=5)
        except Exception as e:
            #print traceback.format_exception(*sys.exc_info())
            return 0
        address = Address(url,r.content)
        self.address_map[url] = address
        return 1
    
    def get_address(self,url):
        return self.address_map[url]
    
    def get_content(self,url):
        return self.address_map[url].content
            
    def description(self):
        description = []
        description.append("Observer %s" % self.ip)
        return "\n".join(description)
            
        
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
                    
    def set_data(self):
        vars = parse_scripts(self.content)
        self.get_child("",vars,0)
        
    ## Recursively create a hash for js variables
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
        
    def description(self):
        description = []
        description.append("Url: %s with content length: %s" % (self.url,len(self.content)))
        return description
    
    def describe_data(self):
        description = []
        for var in self.vars:
            description.append("\t%s : %s" % (var,self.vars[var]))
        return description

ab = AB()
ab.get_proxies()
ab.targets = []
ab.add_target("Instagram",urls,20)
ab.process()
ab.report()
