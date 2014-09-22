import json
import logging
import os.path
import re
import urllib2
from bs4 import BeautifulSoup

from datetime import datetime
from apscheduler.schedulers.tornado import TornadoScheduler

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen
from tornado.options import define, options
import sockjs.tornado

define("port", default=8888, help="Port to run the server on", type=int)
define("debug_mode", default=True)
define("cdn_enabled", default=False)
define("cdn_endpoint")

class Application(tornado.web.Application):
    def __init__(self):
        #SockRouter = sockjs.tornado.SockJSRouter(ServerStatusHandler, '/status')
        handlers = [
            (r'/', IndexHandler),
		]# + SockRouter.urls
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            debug=options.debug_mode,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def get_cdn_host_name(self):
        return options.cdn_endpoint
 
    def is_cdn_enabled(self):
    	enabled = options.cdn_enabled
    	if not options.cdn_endpoint:
    		enabled = False
		return enabled
 
    def static_url(self, path, include_host=None, **kwargs):
        if self.is_cdn_enabled():      
            relative_url = super(BaseHandler, self).static_url(path, include_host=False, **kwargs)
            return '//' + self.get_cdn_host_name() + relative_url
        else:
            return super(BaseHandler, self).static_url(path, include_host=include_host, **kwargs)

    @property
    def iphone_data(self):
        return self.application.iphone_data

#class PhoneStatusHandler(sockjs.tornado.SockJSConnection):

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.write(json.dumps(self.iphone_data))

def scraper(page_url = "http://store.apple.com/sg/buy-iphone/iphone6"):
	print "Scraper is running."
	page = urllib2.urlopen(page_url)
	soup = BeautifulSoup(page)
	script = soup.find('script', text=re.compile('window\.productSelectionController\.addData'))
	json_text = re.search(r'^\s*window\.productSelectionController\.addData\(({.*?})\s*\);\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
	data = json.loads(json_text)
	app.iphone_data = []

	for d in data["products"]:
		model = "iDiot"
		if d["dimensionScreensize"] == "4_7inch":
			model = "iPhone 6" 
		elif d["dimensionScreensize"] == "5_5inch":
			model =  "iPhone 6 Plus"

		colour = d["dimensionColor"].replace("_", " ").title()
		capacity = d["dimensionCapacity"].title()
		price = d["price"].replace("_", ".")
		shipping_quote = d["displayShippingQuote"].title()
		availablility = "No" if shipping_quote == "Currently Unavailable" else "Yes"

		info = {
			'model': model,
			'colour': colour,
			'capacity': capacity,
			'price': price,
			'shippingQuote': shipping_quote,
			'availability': availablility
		}

		app.iphone_data.append(info)

def main():
    tornado.options.parse_config_file(os.path.join(os.path.dirname(__file__), "config.py"))
    tornado.options.parse_command_line()
    global app
    app = Application()
    app.iphone_data = []

    scheduler = TornadoScheduler()
    scheduler.add_job(scraper, 'interval', seconds=60)
    scheduler.start()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()