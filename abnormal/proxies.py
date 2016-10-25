#!/usr/bin/env python
import Queue
import threading
import urllib2
import time

import re
from time import sleep
import requests
import logging

output = []
count = 0

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

def from_cyber_syndrome():
    """
    From "http://www.cybersyndrome.net/"
    :return:
    """
    urls = [
        'http://www.cybersyndrome.net/pld.html',
        'http://www.cybersyndrome.net/pla.html'
    ]

    proxies = []
    for url in urls[:1]:
        r = requests.get(url)
        res = r.content
        proxies += re.findall('(\d+\.\d+\.\d+\.\d+:\d+)', res)
    return proxies

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            proxy_info = self.queue.get()
            global count
            global output
            count = count + 1
            if (count % 100 == 0):
                logging.info("Processed %s proxies" % count)

            try:
                proxy_handler = urllib2.ProxyHandler({'https':proxy_info})
                opener = urllib2.build_opener(proxy_handler)
                opener.addheaders = [('User-agent','Mozilla/5.0')]
                urllib2.install_opener(opener)
                req = urllib2.Request("https://www.google.com")
                sock=urllib2.urlopen(req, timeout= 7)
                rs = sock.read(1000)
                if '<title>Google</title>' in rs:
                    output.append(proxy_info)
                else:
                    raise "Not Google"
            except:
                pass
            self.queue.task_done()

def get_proxies():

    proxies = from_cyber_syndrome()
    logging.info("Got %s proxies from cyber syndrome" % len(proxies))

    return proxies


def check_proxies(threads, proxies_amount):
    queue = Queue.Queue()

    for i in range(threads):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

    proxies = from_cyber_syndrome()[:proxies_amount*4]
    proxies = list(set(proxies))

    for proxy in proxies:
        queue.put(proxy)

    #wait on the queue until everything has been processed     
    queue.join()
    return "\n".join(output)
