import logging
from optparse import OptionParser

from abnormal import AB
from abnormal import Target
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
parser.add_option("-x", "--no_source",
                  dest="no_source", default=0,
                  help="Avoid analysis of source code")

(options, args) = parser.parse_args()
if not options.url: 
    parser.error('A url was not given')

#Set up logging
numeric_level = getattr(logging, options.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % options.loglevel)
logging.basicConfig(level=numeric_level)

#Start
urls = []
if options.url:
    if ',' in options.url:
      urls = options.url.split(",")
    else:
      urls = [ options.url ]
else:
    #open file
    pass

if options.n_threads > options.n_proxies:
  options.n_threads = options.n_proxies

working_proxies = proxies.get_proxies()

ab = AB(working_proxies)
ab.add_target(urls,options)
ab.process()
ab.report()

if (options.cli):
  cli = Cli(ab)
  cli.start()

ab.close()