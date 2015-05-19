#!/usr/bin/python
import urllib2, urllib

import argparse

parser = argparse.ArgumentParser(description='Home Appliance Control System (HACS) client.')
#parser.add_argument('integers', metavar='N', type=int, nargs='+',
#				   help='an integer for the accumulator')
parser.add_argument('-v', dest='verbose', action='store_const',
				   const=True, default=False,
				   help='verbose (default: find the max)')

args = parser.parse_args()
#print(args)
if(args.verbose):
	print 'Wow!'
else:
	print 'Boo!'
#print args.accumulate(args.integers)

#baseList = ['http://router.local/~bigeeyor/','http://nomoreass.hol.es/','http://bigeeyor.0fees.us/','http://bigeeyor.bugs3.com/','http://bigeeyor.host-ed.me/home/','http://148.251.123.45/~bigeeyor/']
#base = baseList[0]
#
#payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('job','keep-alive')]
#payload=urllib.urlencode(payload)
#url	= base+ 'homeAndServer.php'
#req=urllib2.Request(url, payload)
#req.add_header("Content-type", "application/x-www-form-urlencoded")
#
#limitTry = 5;
#for i in range(limitTry):
#	try: urllib2.urlopen(req, timeout=0.1).read()
#	except urllib2.URLError:
#		print 'Timed out for keep-alive process.'
#		if(i<limitTry-1):
#			print 'Trying again...('+str(i+2)+')'
#		else:
#			print 'Limit reached ('+str(i+1)+'), moving on to next process.'
#	except:
#		print 'Error from other cause, moving on to next process.'
#		break
#	else:
#		print 'Passed'
#		break