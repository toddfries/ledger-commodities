#!/usr/bin/env python

import os
import json
import urllib2
import datetime
import sys

filepath = os.path.expanduser("~/prices.dat")

# bitcoincharts currency url explanations
# i = 1-min, 5-min, 15-min, 30-min, Hourly, 2-hour, 6-hour, 12-hour, Daily, Weekly
# r = days, empty = all data
# i1 = (large indicators), empty = none
# i2 = empty = none
# i3 = empty = none
# i4 = empty = none
# v = (show volume bars)
# cv = (volume in currency)
# ps = (parabolic sar)
# l = (log scale)
# p = (percent scale)
# example timeframes that work (too much data requested results in ENODATA)
# i=Weekly&r=
# i=Daily&r=90
# i=Hourly&r=7
# i=15-min&r=30
# i=5-min&r=10

metalsdataurl = "http://services.packetizer.com/spotprices/?f=json"

existingprices = file(filepath).readlines()
existingprices = dict( [ " ".join(l.split()[1:4]), l.strip() ] for l in existingprices )

currencies = [
	[ "mtgoxCAD", "CAD"],
	[ "mtgoxJPY", "JPY"],
	[ "justLTC", "LTC"],
	[ "mtgoxEUR", "EUR"],
	[ "mtgoxUSD", "USD"],
	#[ "cryptoxUSD", "xUSD"],
	[ "bitstampUSD", "bUSD"],
	#[ "globalUSD", "gUSD"],
	[ "rockUSD", "oUSD"],
	[ "mtgoxAUD", "AUD"],
	[ "mtgoxCHF", "CHF"],
	[ "mtgoxSEK", "SEK"],
	[ "mtgoxCNY", "CNY"],
	[ "mtgoxGBP", "GBP"],
	[ "mtgoxRUB", "RUB"],
]

btcprices = dict()

for cur in currencies:
  btcurl = "http://bitcoincharts.com/charts/chart.json?m=" + cur[0] + "&SubmitButton=Draw&i=Hourly&r=3&c=0&t=S&m1=10&m2=25&x=0&i1=&i2=&i3=&i4=&v=1&cv=0&ps=0&l=0&p=0&"
  #print "Starting " + cur[0] + "," + cur[1], ": ", btcurl

  bcd = urllib2.urlopen(btcurl).read()
 
  cprices = [ [datetime.datetime.utcfromtimestamp(row[0])] + [row[4]] for row in json.loads(bcd) ]
  sprices = [ ]
  for x,y in cprices:
    #print "cprices: x = "+str(x)+", y = "+str(y)
    sprices.append(("P", x.strftime("%Y/%m/%d %H:%M:%S"), "BTC", cur[1], "%0.2f"%float(y)))
    sprices.append(("P", x.strftime("%Y/%m/%d %H:%M:%S"), cur[1], "BTC", "%0.8f"%(1/float(y))))

  cprices = dict ( [ d[1] + " " + d[2] + " " + d[3], " ".join(d) ] for d in sprices )
  btcprices.update( cprices )
  #print "len(btcprices) = " + str(len(btcprices))


### METALS

metalscd = urllib2.urlopen(metalsdataurl).read()
metalscd = json.loads(metalscd)
date = metalscd["date"].replace("-","/") + " 17:00:00"
metalprices = [
  [ "P", date, "XAU",      "USD", metalscd["gold"]                     ],
  [ "P", date, "XAG",      "USD", metalscd["silver"]                   ],
  [ "P", date, "XPL",      "USD", metalscd["platinum"]                 ],
  [ "P", date, "PAMPAU",   "USD", str(float(metalscd["gold"])   +  40) ],
  [ "P", date, "RCMPAU",   "USD", str(float(metalscd["gold"])   +  50) ],
  [ "P", date, "ROUNDSAG", "USD", str(float(metalscd["silver"]) + 1.5) ],
]
metalprices = dict( [ d[1] + " " + d[2] + " " + d[3], " ".join(d) ] for d in metalprices )

concatdict = dict(existingprices)
concatdict.update(btcprices)
concatdict.update(metalprices)

values = sorted(concatdict.values())
string = "\n".join(values)
datafile = file(filepath,"w")
datafile.write(string)
datafile.flush()
