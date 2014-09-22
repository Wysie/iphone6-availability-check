import json
import re
import urllib2
from bs4 import BeautifulSoup

page = urllib2.urlopen("http://store.apple.com/sg/buy-iphone/iphone6")
soup = BeautifulSoup(page)

script = soup.find('script', text=re.compile('window\.productSelectionController\.addData'))
json_text = re.search(r'^\s*window\.productSelectionController\.addData\(({.*?})\s*\);\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
data = json.loads(json_text)

for d in data["products"]:
	if d["dimensionScreensize"] == "4_7inch":
		print "Model: iPhone 6"
	elif d["dimensionScreensize"] == "5_5inch":
		print "Model: iPhone 6 Plus"
	else:
		print "Model: iDiot"

	print "Colour: {0}".format(d["dimensionColor"].capitalize())
	print "Capacity: {0}".format(d["dimensionCapacity"].capitalize())
	print "Price: ${0}".format(d["price"].replace("_", "."))
	print "Availability: {0}\n".format(d["displayShippingQuote"].capitalize())