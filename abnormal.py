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
import logging
from optparse import OptionParser

from abnormal import AutoVivification
from abnormal import AB
from abnormal import Target
from abnormal import Observer
from abnormal import Address
from abnormal import proxies
from abnormal import Cli

parser = OptionParser()
parser.add_option("-u", "--url", dest="url",
                  help="Url to use")
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
parser.add_option("-f", "--file",
                  dest="url_file",
                  help="File of urls to process")
parser.add_option("-d", "--debug",
                  dest="debug", default=0,
                  help="Debug mode")
parser.add_option("-n", "--no_proxy",
                  dest="no_proxy", default=0,
                  help="Avoid using proxies, only for debug purpouses")
parser.add_option("-c", "--cli",
                  dest="cli", default=0,
                  help="Use command line interface to interact with observers")
parser.add_option("-s", "--screen_shot",
                  dest="capture_on", default=0,
                  help="Compare screenshots of site")


(options, args) = parser.parse_args()

if not options.url:   # if filename is not given
    parser.error('A url was not given')

#Set up logging
numeric_level = getattr(logging, options.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % options.loglevel)
logging.basicConfig(level=numeric_level)
logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()

#Start
urls = []
if options.url:
    urls = [ options.url ]
else:
    #open file
    pass

working_proxies = proxies.get_proxies()
#working_proxies = proxies.check_proxies(options.n_threads,options.n_proxies)

ab = AB(working_proxies)
ab.add_target(urls,options)
ab.process()
ab.report()

if (options.cli):
  cli.start(ab)