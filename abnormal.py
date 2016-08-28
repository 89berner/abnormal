import requests
from time import sleep
from lxml.html.diff import htmldiff
import pprint
import re
import sys
import traceback
import requests
import json
import re
import proxies
from optparse import OptionParser

from abnormal import AutoVivification
from abnormal import AB
from abnormal import Target
from abnormal import Observer
from abnormal import Address

#Set up logging
import logging
parser = OptionParser()
parser.add_option("-u", "--url", dest="url",
                  help="Url to use", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-t", "--threads", type="int",
                  dest="n_threads", default=10,
                  help="Amount of threads to use in parallel")
parser.add_option("-p", "--proxies", type="int",
                  dest="n_proxies", default=5,
                  help="Amount of proxies to use")
parser.add_option("-l", "--log", default="WARNING",
                  dest="loglevel",
                  help="Log level")
parser.add_option("-m", "--max", type="int",
                  dest="max_ips", default=20,
                  help="Max amount of proxies to use")
parser.add_option("-m", "--urls",
                  dest="urls",
                  help="File of urls to process")
(options, args) = parser.parse_args()

if not options.url:   # if filename is not given
    parser.error('A url was not given')

numeric_level = getattr(logging, options.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % options.loglevel)
logging.basicConfig(level=numeric_level)
logging.getLogger("requests").setLevel(logging.WARNING)

#Start
urls = []
if not urls in options:
    urls = [ options.url ]
else:
    #open file
    pass

working_proxies = proxies.check_proxies(options.n_threads,options.n_proxies)
ab = AB(working_proxies)
ab.targets = []
ab.add_target(options.url,urls,options.max_ips)
ab.process()
ab.report()
