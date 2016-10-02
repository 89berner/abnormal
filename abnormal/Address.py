import logging
import json
import re
import time
from BeautifulSoup import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#Reduce logging for selenium
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

class Address:
    def __init__(self, url, content, observer):
        self.url = url
        self.content = content
        self.scripts = {}
        self.diff_scripts = []
        self.vars = {}
        self.links = {}
        self.filename = ""
        self.observer = observer
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
        self.parse_links()

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

    def parse_links(self):
        soup = BeautifulSoup(self.content)
        for link in soup.findAll('a'):
            if 'href' in link:
                link_name = link['href'].strip().replace(" ","")
                self.links[link_name] = 1

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

    def take_screenshot(self):
        max_wait = 300
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = ( self.observer.ua )

        service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=any']
        if not self.no_proxy:
            service_args.append("--proxy=%s" % self.ip)

        driver = webdriver.PhantomJS(service_log_path=os.path.devnull, desired_capabilities=dcap, service_args=service_args)
        try:
            driver.set_window_size(1280,800)
            driver.set_page_load_timeout(max_wait)
            driver.set_script_timeout(max_wait)
            driver.get(self.url)
            time.sleep(1)
            filename = "tmp/screen/%s" % Utils.as_filename("%s-%s.png" % (self.url,self.observer.ip))
            driver.save_screenshot(filename)
            self.filename = filename
            logging.debug("Saved %s" % filename)
        except Exception as e:
            print "Error taking screenshot: %s" % (traceback.format_exception(*sys.exc_info()))
        finally:
            driver.close()
            driver.quit()
        