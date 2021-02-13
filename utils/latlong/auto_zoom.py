from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import re
import argparse


# TODO - INSTALLATION AND SETTING PATHS

def get_zoom_level(latitude, longitude):
	with open('utils/latlong/latlong.html', 'r') as f:
		
		file = f.read()
		file = re.sub("(lat: )(\d+\.\d+)", "lat: {}".format(latitude), file) 
		file = re.sub("(lng: )(\d+\.\d+)", "lng: {}".format(longitude), file)
		with open('utils/latlong/newlatlong.html', 'w') as tempf:
			tempf.write(file)

	# file_path = "/home/master/Documents/COE/latlong/newlatlong.html"
	file_path = os.path.abspath("utils/latlong/newlatlong.html")
	file_loc = ''.join(["file://", file_path])
	# chromedriver_path = "/home/master/Documents/COE/latlong/chromedriver"
	chromedriver_path = "utils/latlong/chromedriver"
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	browser = webdriver.Chrome(executable_path=chromedriver_path, options=options)
	browser.get(file_loc)
	div = browser.find_element_by_id('mydiv')
	print("Zoom level:", div.text)
	return int(div.text)

if __name__ == '__main__':
	latitude = 19.107436
	longitude = 72.903875
	get_zoom_level(latitude, longitude)