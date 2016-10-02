import Utils
import logging
import traceback
import requests
from fake_useragent import UserAgent
#Reduce logging from requests
logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()

from Address import Address

ua = UserAgent()
agent = ua.random

class Observer:
    def __init__(self, ip, urls, debug, no_proxy):
        self.ip = ip
        self.urls = urls
        self.address_map = {}
        self.session = requests.Session()
        self.debug = debug
        self.no_proxy = no_proxy

        #Set user agent for observer
        self.ua = agent
        self.session.headers.update({'user-agent' : self.ua})

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
            r = self.session.get(url, proxies=proxies, verify=False, timeout=5)
        except Exception as e:
            #logging.debug(traceback.format_exception(*sys.exc_info()))
            return 0
        address = Address(url,r.content,self)
        self.address_map[url] = address

        #Save source
        filename = "tmp/source/%s" % Utils.as_filename("%s-%s.txt" % (url, self.ip))
        f = open(filename, 'w')
        f.write(r.content)

        return 1

    def take_screenshots(self):
        for address in self.address_map:
            address.take_screenshot()             

    def get_address(self,url):
        return self.address_map[url]
    
    def get_content(self,url):
        return self.address_map[url].content

    def get_image(self,url):
        return self.address_map[url].filename
            
    def description(self):
        description = []
        description.append("Observer %s" % self.ip)
        return "\n".join(description)