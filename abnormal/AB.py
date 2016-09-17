import sys
import traceback
import requests
from AutoVivification import AutoVivification
from BeautifulSoup import BeautifulSoup
from sets import Set
import Queue
import threading

import re
import json
import logging
from Result import Result

class ThreadProcessTarget(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, working_observers, max_ips):
        threading.Thread.__init__(self)
        self.queue = queue
        self.working_observers = working_observers
        self.max_ips = max_ips

    def run(self):
        while True:
            observer = self.queue.get()
            if len(self.working_observers) < self.max_ips:
                status = observer.request()
                if (status == 1): #Working observers
                    self.working_observers.append(observer)
                    logging.debug("Count is now %s of %s" % (len(self.working_observers), self.max_ips) )
                else:
                    #logging.debug("Observer %s failed" % observer.ip)
                    pass
            self.queue.task_done()


class AB:
    def __init__(self, proxies):
        self.targets = []
        self.observer_list = proxies
        
    def add_target(self,name,urls,max_ips, max_threads):
        target = Target(name,urls,self.observer_list,max_ips, max_threads)
        self.targets.append(target)
        
    def process(self):
        for target in self.targets:
            print "Starting for target %s" % target.name
            target.process()
            
    def report(self):
        for target in self.targets:
            target.report()
            print "-" * 50

class Target:
    def __init__(self, name, urls, ip_list, max_ips, max_threads):
        self.urls = urls
        self.max_threads = max_threads
        self.name    = name
        self.max_ips = max_ips

        self.possible_observers = []
        for ip in ip_list:
            self.possible_observers.append(Observer(ip,urls))

        self.diff_vars    = {}
        self.missing_vars = {}
        for url in urls:
            self.diff_vars[url] = Set()
            self.missing_vars[url] = Set()

        #Set instance variables
        self.observers    = []
        self.results = Result(name, urls)

    def process(self):
        #Move to multi threading
        working_observers = []
        queue = Queue.Queue()
        for i in range(self.max_threads):
            t = ThreadProcessTarget(queue,working_observers,self.max_ips)
            t.setDaemon(True)
            t.start()

        for observer in self.possible_observers:
            queue.put(observer)

        queue.join()
        self.observers = working_observers[:self.max_ips]
        logging.info("Got %s working observers" % len(working_observers))
        
        #For each url match observer by observer and see
        #what variables are missing or different
        for url in self.urls:
            for observer1 in self.observers:
                for observer2 in self.observers:
                    if (observer1.ip != observer2.ip):
                        self.check_vars(observer1,observer2,url)

            #Per type of check, count and append occurances 
            self.compare(url)
            break
                        
    def check_vars(self,observer1,observer2,url):
        logging.debug('Checking vars between %s-%s for %s' % (observer1.ip,observer2.ip,url))
        vars1 = observer1.get_address(url).vars
        vars2 = observer2.get_address(url).vars

        for var in vars1:
            logging.debug('Comparing for %s %s' % (var,vars1[var]))
            if (var not in vars2):
                self.missing_vars[url].add(var)
            elif (vars1[var] != vars2[var]):
                self.diff_vars[url].add(var)
                
    def compare(self,url):
        logging.debug('Doing compare for %s' % url)

        url_results = self.results.get(url)
        #Looking for missing js variables
        for missing in self.missing_vars[url]:
            logging.debug('Looking for %s' % missing)
            for observer in self.observers:
                addr = observer.get_address(url)
                if missing not in addr.vars:
                    logging.debug("%s is missing" % missing)
                    url_results.set_missing_var(missing)

        #Looking for differences in js variables
        for diff_var in self.diff_vars[url]:
            logging.debug('Comparing %s' % diff_var)
            for observer in self.observers:
                addr = observer.get_address(url)
                if diff_var in addr.vars:
                    var_value = addr.vars[diff_var]
                    url_results.set_diff_var(diff_var,var_value)

    def report(self):
        print "Report for %s" % self.name
        for url in self.urls:
            results = self.results.print_table(url)        
        
class Observer:
    def __init__(self, ip, urls):
        self.ip = ip
        self.urls = urls
        self.address_map = {}
        self.session = requests.Session()
        
    def request(self):
        status = 0
        for url in self.urls:
            status = status + self.get_url(url)
        if status / len(self.urls) == 1:
            return 1
        else:
            return 0
        
    def get_url(self,url):
        proxies = {'http' : "http://%s" % self.ip, 'https': "https://%s" % self.ip}
        try:
            r = self.session.get(url, proxies=proxies, verify=False, timeout=5)
        except Exception as e:
            #logging.debug(traceback.format_exception(*sys.exc_info()))
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
        vars = self.parse_scripts()
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
