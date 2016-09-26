import sys
import os
import signal
import traceback
import requests
from sets import Set
import Queue
import threading
import re
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#Reduce logging for selenium
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from Result import Result
from Address import Address
from AutoVivification import AutoVivification

class ThreadProcessTarget(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, working_observers, max_ips, capture_on):
        threading.Thread.__init__(self)
        self.queue = queue
        self.working_observers = working_observers
        self.max_ips = max_ips
        self.capture_on = capture_on

    def run(self):
        while True:
            observer = self.queue.get()
            if len(self.working_observers) < self.max_ips:
                status = observer.request()
                if (status == 1): #Working observers
                    self.working_observers.append(observer)
                    if self.capture_on:
                        try:
                            observer.take_screenshots()
                        except:
                            pass
                    logging.debug("Count is now %s of %s" % (len(self.working_observers), self.max_ips) )
                else:
                    #logging.debug("Observer %s failed" % observer.ip)
                    pass
            self.queue.task_done()

class AB:
    def __init__(self, proxies):
        self.targets = {}
        self.observer_list = proxies
        
    def add_target(self,name,urls,max_ips, max_threads, debug, no_proxy, capture_on):
        target = Target(name,urls,self.observer_list,max_ips, max_threads, debug, no_proxy, capture_on)
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

class Target:
    def __init__(self, name, urls, ip_list, max_ips, max_threads, debug, no_proxy, capture_on):
        self.urls = urls
        self.max_threads = max_threads
        self.name    = name
        self.max_ips = max_ips
        self.capture_on = capture_on

        self.possible_observers = []
        for ip in ip_list:
            self.possible_observers.append(Observer(ip,urls,debug,no_proxy))

        self.diff_vars    = {}
        self.missing_vars = {}
        for url in urls:
            self.diff_vars[url] = Set()
            self.missing_vars[url] = Set()

        #Set instance variables
        self.observers    = []
        self.results = Result(name, urls)

        self.observers_vars = AutoVivification( )

    def process(self):
        
        #Get observers to use
        self.get_working_observers()

        #Check the difference between observers
        self.analyze_observers()

        #Compare observers        
        self.compare_observers()

    def analyze_observers(self):
        #For each url match observer by observer and see
        #what variables are missing or different
        for url in self.urls:
            for observer1 in self.observers:
                for observer2 in self.observers:
                    if (observer1.ip != observer2.ip):
                        self.check_vars(observer1,observer2,url)

    def compare_observers(self):
        for url in self.urls:
            self.compare(url)

    def get_working_observers(self):
        working_observers = []
        queue = Queue.Queue()
        for i in range(self.max_threads):
            t = ThreadProcessTarget(queue,working_observers,self.max_ips,self.capture_on)
            t.setDaemon(True)
            t.start()

        for observer in self.possible_observers:
            queue.put(observer)

        queue.join()
        logging.info("Got %s working observers" % len(working_observers))
        self.observers = working_observers[:self.max_ips]

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

        #Populate observers index
        for var in vars1:
            self.observers_vars[observer1.ip][var] = vars1[var]
        for var in vars2:
            self.observers_vars[observer2.ip][var] = vars2[var]
                
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
        self.results.report()
        logging.debug(self.observers_vars)

    #Go through the observers looking that at least one has the var
    def check_var(name):
        for observer in self.observers_vars:
            for var in self.observers_vars[observer]:
                return True
        return False

    #Go through the observers looking for the ones that have the variables
    def get_var_observers(name,value):
        result = []
        for observer in self.observers_vars:
            for var in self.observers_vars[observer]:
                if var == name:
                    if len(value) and self.observers_vars[observer][var] == value:
                        result.append(observer)
                    else:
                        result.append(observer)

class Observer:
    def __init__(self, ip, urls, debug, no_proxy):
        self.ip = ip
        self.urls = urls
        self.address_map = {}
        self.session = requests.Session()
        self.debug = debug
        self.no_proxy = no_proxy
        
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
        if self.no_proxy:
            proxies = {}
        try:
            #r = self.session.get(url, proxies=proxies, verify=False, timeout=5)
            r = self.session.get(url, verify=False, timeout=5)
        except Exception as e:
            #logging.debug(traceback.format_exception(*sys.exc_info()))
            return 0
        address = Address(url,r.content)
        self.address_map[url] = address
        if (self.debug):
            f = open("tmp/%s-%s.txt" % (url.replace("/",""), self.ip ), 'w')
            f.write(r.content)
        return 1

    def take_screenshots(self):
        for url in self.urls:
            self.take_screenshot(url)

    def take_screenshot(self,url):
        max_wait = 60
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36"
        )

        service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=any']
        if not self.no_proxy:
            service_args.append("--proxy=%s" % self.ip)

        driver = webdriver.PhantomJS(service_log_path=os.path.devnull, desired_capabilities=dcap, service_args=service_args)
        try:
            driver.set_window_size(1280,800)
            driver.set_page_load_timeout(max_wait)
            driver.set_script_timeout(max_wait)
            driver.get(url)
            if (self.debug):
                driver.save_screenshot("tmp/python_org-%s.png" % self.ip)
        finally:
            driver.close()
            driver.quit()             

    def get_address(self,url):
        return self.address_map[url]
    
    def get_content(self,url):
        return self.address_map[url].content
            
    def description(self):
        description = []
        description.append("Observer %s" % self.ip)
        return "\n".join(description)