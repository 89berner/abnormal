from AutoVivification import AutoVivification
import Utils
import cv2
import numpy as np
import hashlib
import pprint
import logging
import threading
import Queue
from sets import Set
from Result import Result
import traceback
import sys

from Observer import Observer

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
                if observer.request(): #Get content and screenshots
                    self.working_observers.append(observer)
                logging.debug("Count is now %s of %s" % (len(self.working_observers), self.max_ips) )
            self.queue.task_done()

class Target:
    def __init__(self, name, urls, ip_list, options):
        self.urls = urls
        self.max_threads = options.n_threads
        self.name    = name
        self.max_ips = options.n_proxies
        self.capture_on = options.capture_on

        self.possible_observers = []
        for ip in ip_list:
            self.possible_observers.append(Observer(ip,urls,options))

        self.diff_vars     = {}
        self.missing_vars  = {}
        self.missing_links = {}
        self.diff_images   = {}
        self.diff_marked_images   = {}
        for url in urls:
            self.diff_vars[url] = {}
            self.missing_vars[url] = Set()
            self.missing_links[url] = Set()
            self.diff_images[url] = {}
            self.diff_marked_images[url] = {}

        #Set instance variables
        self.observers    = []
        self.results = Result(name, urls)

        self.observers_vars = AutoVivification()
        self.processed      = AutoVivification()
        self.contourns = {}

    def process(self):
        
        #Get observers to use
        self.get_working_observers()

        #Set the data based on the content and the screenshot
        self.process_observers()

        #Check the difference between observers
        #populate missing_vars, diff_vars, missing_links, diff_images, diff_marked_images
        self.analyze_observers()

        #Compare observers to create Result object       
        self.compare_observers()

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
        self.observers = working_observers[:self.max_ips]
        logging.info("Got %s working observers" % len(working_observers))

    def process_observers(self):
        for observer in self.observers:
            for url in self.urls:
                address = observer.get_address(url)
                address.set_data()

    def analyze_observers(self):
        #For each url match observer by observer and see
        for url in self.urls:
            for observer1 in self.observers:
                for observer2 in self.observers:
                    if (observer1.ip != observer2.ip):
                        #what variables are missing or different
                        self.check_vars(observer1,observer2,url)
                        
                        #difference between screenshots                        
                        if self.capture_on:
                            self.check_screenshots(observer1,observer2,url)

                        #Find difference in links
                        self.check_links(observer1,observer2,url)

    def check_vars(self,observer1,observer2,url):
        logging.debug('Checking vars between %s-%s for %s' % (observer1.ip,observer2.ip,url))
        vars1 = observer1.get_address(url).vars
        vars2 = observer2.get_address(url).vars

        for var in vars1:
            logging.debug('Comparing for vars: %s %s' % (var,vars1[var]))
            if (var not in vars2):
                self.missing_vars[url].add(var)
            elif (vars1[var] != vars2[var]):
                if not var in self.diff_vars[url]:
                    self.diff_vars[url][var] = 0
                self.diff_vars[url][var] += 1

        #Populate observers index
        for var in vars1:
            self.observers_vars[observer1.ip][url][var] = vars1[var]
        for var in vars2:
            self.observers_vars[observer2.ip][url][var] = vars2[var]

    def check_screenshots(self, observer1, observer2, url):
        logging.debug('Comparing images between %s-%s for %s' % (observer1.ip,observer2.ip,url))
        image1 = observer1.read_image(url)
        image2 = observer2.read_image(url)

        Utils.resize_images(image1,image2)

        difference_1 = cv2.subtract(image1, image2)
        difference_2 = cv2.subtract(image2, image1)
        result = not np.any(difference_1)  

        if result is False: #and not self.get_processed(observer2,observer1,url,'screen')
            #First set up different types of images to have them on their own
            self.set_different_image(image1, url, observer1.get_image(url))
            self.set_different_image(image2, url, observer2.get_image(url))

            logging.debug('The images are different')
            filename_1 = "%s-%s-%s" % (observer1.ip, observer2.ip, url)
            cv2.imwrite("tmp/comp/%s.jpg" % Utils.as_filename(filename_1), difference_1)
            filename_2 = "%s-%s-%s" % (observer2.ip, observer1.ip, url)
            cv2.imwrite("tmp/comp/%s.jpg" % Utils.as_filename(filename_2), difference_2)
            
            concat_images = np.concatenate((image1, image2, difference_1, difference_2), axis=1)
            cv2.imwrite("tmp/comp_full/%s.jpg" % Utils.as_filename(filename_1), concat_images)

            contourn_image1 = Utils.draw_contourns(image1,image2)
            file_path = "tmp/comp_draw/%s.jpg" % Utils.as_filename(filename_1)
            cv2.imwrite(file_path, contourn_image1)
            self.set_different_marked_image(contourn_image1,url,file_path)

        self.set_processed(observer1,observer2,url,'screen')
        logging.debug("Finished comparing images..")
    
    def check_links(self,observer1,observer2,url):
        links1 = observer1.get_address(url).links 
        links2 = observer1.get_address(url).links

        for link in links1:
            logging.debug('Comparing links: %s' % link)
            if link not in links2:
                self.missing_links[url].add(var)

    def compare_observers(self):
        for url in self.urls:
            self.compare(url)

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

        #Looking for missing links
        for missing in self.missing_links[url]:
            logging.debug('Looking for %s' % missing)
            for observer in self.observers:
                addr = observer.get_address(url)
                if missing not in addr.links:
                    logging.debug("%s is missing" % missing)
                    url_results.set_missing_link(missing)

        #Looking for different captures
        for md5 in self.diff_images[url]:
            logging.debug('Looking for %s' % md5)
            url_results.set_diff_images(md5, self.diff_images[url][md5])

        #Looking for different marked captures
        for md5 in self.diff_marked_images[url]:
            logging.debug('Looking for %s' % md5)
            url_results.set_diff_marked_images(md5, self.diff_marked_images[url][md5])

    def set_different_image(self,image, url, filename):
        image_hash = hashlib.md5(image).hexdigest()
        if image_hash not in self.diff_images[url]:
            self.diff_images[url][image_hash] = filename

    def set_different_marked_image(self,image, url, filename):
        image_hash = hashlib.md5(image).hexdigest()
        if image_hash not in self.diff_marked_images[url]:
            self.diff_marked_images[url][image_hash] = filename

    def report(self):
        print "Report for %s" % self.name
        self.results.report()
        pp = pprint.PrettyPrinter(indent=4)
        logging.debug(pp.pprint(self.observers_vars))

    #Go through the observers looking that at least one has the var
    def check_var(self,name):
        for observer in self.observers:
            for url in observer.urls:
                if name in self.observers_vars[observer.ip][url]:
                    return True
        return False

    #Go through the observers looking for the ones that have the variables
    def get_var_observers(self,name,value):
        result = Set()
        for observer in self.observers:
            for url in observer.urls:
                observer_vars = self.observers_vars[observer.ip][url]
                for var in observer_vars:
                    if var == name:
                        if len(value):
                            if observer_vars[var] == value:
                                result.append(observer)
                        else:
                            result.append(observer)
        return result

    def set_processed(self,observer1,observer2,url,m_type):
        name = "%s-%s" % (observer1.ip, observer2.ip)
        self.processed[m_type][url][name] = 1

    def get_processed(self,observer1,observer2,url,m_type):
        name = "%s-%s" % (observer1.ip, observer2.ip)
        return self.processed[m_type][url][name]