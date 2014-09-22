import json
import re
import urllib2
from bs4 import BeautifulSoup

page = urllib2.urlopen("http://store.apple.com/sg/buy-iphone/iphone6")
soup = BeautifulSoup(page)
script = soup.find('script', text=re.compile('window\.productSelectionController\.addData'))
json_text = re.search(r'^\s*window\.productSelectionController\.addData\(({.*?})\s*\);\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
data = json.loads(json_text)

data_extract = []

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
		
	print "Model: {0}".format(model)
	print "Colour: {0}".format(colour)
	print "Capacity: {0}".format(capacity)
	print "Price: ${0}".format(price)
	print "Shipping Quote: {0}".format(shipping_quote)
	print "Availability: {0}\n".format(availablility)

	info = {
		'model': model,
		'colour': colour,
		'capacity': capacity,
		'price': price,
		'shippingQuote': shipping_quote,
		'availability': availablility
	}

	data_extract.append(info)

print data_extract