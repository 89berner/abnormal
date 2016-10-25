import Utils
import logging
import requests
import traceback
import sys
import cv2
from fake_useragent import UserAgent
#Reduce logging from requests
logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()

from Address import Address

ua = UserAgent()
agent = ua.random

class Observer:
    def __init__(self, ip, urls, options):
        self.ip = ip
        self.urls = urls
        self.options = options
        self.session = requests.Session()

        #Map of addresses
        self.address_map = {}

        #Set user agent for observer
        self.ua = agent
        self.session.headers.update({'user-agent' : self.ua})

    def request(self):
        for url in self.urls:
            address = Address(url,self,self.options)
            if (not self.options.no_source):
                status = address.get_url(url)
            else:
                status = 1
            if (status):
                if (self.options.capture_on):
                    try:
                        screenshot_status = address.take_screenshot()
                        if (screenshot_status == 0):
                            return 0
                    except Exception as e:
                        print "Error taking screenshot: %s" % (traceback.format_exception(*sys.exc_info()))
                        return 0
                self.address_map[url] = address
            else:
                return 0
        return 1 #Only then will the observer be used

    def get_address(self,url):
        return self.address_map[url]
    
    def get_content(self,url):
        return self.address_map[url].content

    def get_image(self,url):
        return self.address_map[url].image_filename

    def read_image(self,url):
        return self.address_map[url].read_image()