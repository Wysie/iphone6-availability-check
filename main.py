# -*- coding: utf-8 -*-

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
        SockRouter = sockjs.tornado.SockJSRouter(ServerDataHandler, '/data')
        handlers = [
            (r'/', IndexHandler),
		] + SockRouter.urls
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

class BaseSocketHandler(sockjs.tornado.SockJSConnection):
    @property
    def server_variables(self):
        return app.server_variables

allsockets = [] # Hackish method to access the methods within the ServerDataHandler

class ServerDataHandler(BaseSocketHandler):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)
        if self not in allsockets:
            allsockets.append(self)

    def on_message(self, msg):
        self.broadcast(self.clients, msg)

    def on_close(self):
        self.clients.remove(self)
        if self in allsockets:
            allsockets.remove(self)

# Hackish method. Logically we can loop through each of the object in allsockets and send a message,
# but since there is a broadcast function, we only need to make use of any one object. For simplicity,
# we are using the first object in the list.
def update_data():
    if len(allsockets) > 0:
        allsockets[0].broadcast(allsockets[0].clients, json.dumps(app.iphone_data))

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.render('index.html', data=json.dumps(app.iphone_data))

def scraper(page_url = "http://store.apple.com/sg/buy-iphone/iphone6", country = "sg"):
    page = urllib2.urlopen(page_url)
    soup = BeautifulSoup(page)
    script = soup.find('script', text=re.compile('window\.productSelectionController\.addData'))
    json_text = re.search(r'^\s*window\.productSelectionController\.addData\(({.*?})\s*\);\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    data = json.loads(json_text)
    app.iphone_data[country] = []

    for d in data["products"]:
        model = "iDiot"
        if d["dimensionScreensize"] == "4_7inch":
        	model = "iPhone 6" 
        elif d["dimensionScreensize"] == "5_5inch":
        	model =  "iPhone 6 Plus"

        colour = d["dimensionColor"].replace("_", " ").title()
        capacity = d["dimensionCapacity"].title()
        price = "{:,.2f}".format(float(d["price"].replace("_", ".")))

        shipping_quote = d["displayShippingQuote"].title() if country != "tw" else d["displayShippingQuote"]
        availablility = "Yes"

        if shipping_quote == "Currently Unavailable" or shipping_quote == "暫無供應".decode('UTF-8'):
            availablility = "No"

        info = {
        	'model': model,
        	'colour': colour,
        	'capacity': capacity,
        	'price': price,
        	'shippingQuote': shipping_quote,
        	'availability': availablility
        }

        app.iphone_data[country].append(info)

def scraper_sg():
    scraper("http://store.apple.com/sg/buy-iphone/iphone6", "sg")

def scraper_hk():
    scraper("http://store.apple.com/hk/buy-iphone/iphone6", "hk")

def scraper_tw():
    scraper("http://store.apple.com/tw/buy-iphone/iphone6", "tw")

def scraper_au():
    scraper("http://store.apple.com/au/buy-iphone/iphone6", "au")

def main():
    tornado.options.parse_config_file(os.path.join(os.path.dirname(__file__), "config.py"))
    tornado.options.parse_command_line()
    global app
    app = Application()
    app.iphone_data = {}

    scraper_sg()
    scraper_hk()
    scraper_tw()
    scraper_au()
    scheduler = TornadoScheduler()
    time_interval = 60
    scheduler.add_job(scraper_sg, 'interval', seconds=time_interval)
    scheduler.add_job(scraper_hk, 'interval', seconds=time_interval)
    scheduler.add_job(scraper_tw, 'interval', seconds=time_interval)
    scheduler.add_job(scraper_au, 'interval', seconds=time_interval)
    scheduler.add_job(update_data, 'interval', seconds=time_interval)
    scheduler.start()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()