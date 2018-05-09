#!/usr/bin/python

# this started with code borrowed from
# https://www.hackster.io/carmelito/home-monitoring-system-for-elderly-using-hologram-986d09
# and heavily modifed to send an ifttt alert to the ifttt app itself
# This version does *not* use the hologram data router function
# from the author on hackster.io:
#Created to demo the Home Monitoring system for the elderly - using Hologram Nova
#This code is based on -
# Hologram sample code -https://hologram.io/docs/reference/cloud/python-sdk/
# and sample code for the Grove sensors - https://github.com/DexterInd/GrovePi/tree/master/Software/Python

# note Grove not used

# Actual working curl example that works on the command line
# curl -H "Content-Type: application/json" -X POST -d '{"value1":"75.5"}' https://maker.ifttt.com/trigger/deleted-trigger-name/with/key/deleted-key

import time
import math
import sys
import requests
from Hologram.HologramCloud import HologramCloud
import Adafruit_DHT as dht

ALARMTEMP=85

# deleted my key for public github version
IFTTTPostSite="https://maker.ifttt.com/trigger/trigger-name/with/key/XXXXXXXXXXXX"
# FAIL test value
# IFTTTPostSite="https://maker.ifttt.com/trigger/trigger-name/with/key/XXXXXXXXXX"

# hologram = HologramCloud(credentials, network='cellular')
# Connect the Grove Temperature & Humidity Sensor Pro to digital port D4
# sensorDHT22 = 4

# primitive for now: create a loop with a sleep timer--maybe use cron later

def get_temp():
	h,t=dht.read_retry(dht.DHT22, 4)
	fahrenheit = (t * 1.8 ) + 32 # convert to fahrenheit
	return fahrenheit,h

def send_alarm(fahr,h):
	hologram = HologramCloud(dict(), network='cellular') # connect to cellular

	result = hologram.network.connect()
	if result == False:
		print 'Failed to connect to cell network'
		sys.exit(1) # later will call textMessage function
	print "Attempting to send to Hologram cloud..."
	print "String to send is " + message
	print "attempting to send to holo cloud"
	# postData={"value1":fahr,"value2":h}
	postData={"value1":'{0:0.1f}'.format(fahr),"value2":'{0:0.1f}'.format(h)}
	r=requests.post(url=IFTTTPostSite, data=postData)
	# r is the returned status code from the curl request
	print(r.status_code, r.reason)
	hologram.network.disconnect() 

	if (r.status_code != "200"):
		return 1  # error condition
	else:
		return 0  # got a "200 OK"

while True:
	# get the current temp from sensor
	fahr,h = get_temp()
	# message = 'Temp is {0:0.1f}*F Humidity is {1:0.1f}%'.format(fahr,h)
	message = '{{ "Value1":"{0:0.1f}", "Value2": "{1:0.1f}" }}'.format(fahr,h)

	# responseCode = hologram.sendMessage(message)
	# print hologram.getResultString(responseCode) # print the response code 
	print ("Current Temp and humidity is "+ message)
	print ("Current Alarm Temp is {0:0.1f} ".format(ALARMTEMP))

	result = 0 # should get overridden in send_alarm() if there's a failure
	if (fahr >= ALARMTEMP):
		result = send_alarm(fahr,h)

	if (result != 0):  # curl failed, send text
		# later will call textMessage function
		print("data message failed. Trying text message")
	time.sleep(300)  # sleep for 30s

