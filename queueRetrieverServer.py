#! /usr/bin/env python
# This code will retreive and store session locally.
import os
import subprocess
import math
import re
import time
import urllib2, urllib
from datetime import datetime
from datetime import timedelta
import shelve
import argparse

parser = argparse.ArgumentParser(description='Home Appliance Control System (HACS) client.')
#parser.add_argument('integers', metavar='N', type=int, nargs='+',
#				   help='an integer for the accumulator')
parser.add_argument('-v', dest='verbose', action='store_const',
				   const=True, default=False,
				   help='Verbose mode (display only important details)')
parser.add_argument('-vv', dest='superverbose', action='store_const',
				   const=True, default=False,
				   help='Super verbose mode (display every details)')				
parser.add_argument('-s', dest='selectBase', action='store_const',
				   const=True, default=False,
				   help='Manually select server from the list.')	
args = parser.parse_args()
verbose = args.verbose
sVerbose = args.superverbose
selectBase = args.selectBase
baseList = ['http://router.local/~bigeeyor/','http://nomoreass.hol.es/','http://bigeeyor.0fees.us/','http://bigeeyor.bugs3.com/','http://bigeeyor.host-ed.me/home/','http://148.251.123.45/~bigeeyor/home/','http://hacs.dx.am/','http://teto.ueuo.com/']
if(selectBase):
	for i in range(baseList.__len__()):
		print str(i) + ': ' + baseList[i]
	print 'Which server is intended to use?'
	base	= baseList[int(raw_input('Select option : '))]
else:
	base = baseList[5]
print base + ' is selected.'
#timing_appliance = []
timed_appliance = []
timedListNumber = 0
timeout = 3 # Time out for connecting (default 3 seconds)
wait_time = 30
timeoutForDisplay = 5
sessionFile = '/tmp/shelve.out'
displayFlag = True
nextDisplayTime = 0
pingStatTime = 0
connectionHealth = 0
limitTry = 5
sleepWaitTime = 5;# in Minutes unit
if(verbose):
	print "Verbose Mode"
elif(sVerbose):
	print "Super Verbose Mode"
else:
	print "Normal Mode"
def tryQueryServer(req, prevData):
	if(verbose|sVerbose):
		print 'Fetching data from server: '+base
	for i in range(limitTry):
		try: data = urllib2.urlopen(req, timeout=timeout).read()
		except urllib2.URLError:
			if(verbose|sVerbose):
				print 'Cannot reach server.'
			if(i<limitTry-1):
				if(verbose|sVerbose):
					print 'Trying again...('+str(i+2)+')'
			else:
				if(verbose|sVerbose):
					print 'Limit reached ('+str(i+1)+'), moving on to next process.'
				data = prevData
		except:
			if(verbose|sVerbose):
				print 'Error from other cause, moving on to next process.'
			data = prevData
			break
		else:
			break
	if(sVerbose):
		print data
	return data

def queryServer(payload):
#	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('job','ping')]
	payload=urllib.urlencode(payload)
	url	= base+ 'homeAndServer.php'
	req=urllib2.Request(url, payload)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	for i in range(limitTry):
		if(sVerbose):
			print "Pinging server to check the latency."
		try: data = urllib2.urlopen(req, timeout=timeout).read()
		except urllib2.URLError:
			if(verbose|sVerbose):
				print 'Cannot reach server. Ping has been skipped.'
			if(i<limitTry-1):
				if(verbose|sVerbose):
					print 'Trying again...('+str(i+2)+')'
			else:
				if(verbose|sVerbose):
					print 'Limit reached ('+str(i+1)+'), moving on to next process.'
				data = float(0)
		except:
			if(verbose|sVerbose):
				print 'Error from other cause, moving on to next process.'
			data = float(0)
			break
		else:
			break
	return float(data)

def statServer():
	averagePingTime = 0;
	if(verbose|sVerbose):
		print "Accumulating server stat for client latency."
	for i in range(3):
		pingTime = time.time()
		payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('job','ping')]
		queryServer(payload)
		averagePingTime = averagePingTime + ((time.time() - pingTime)/2)
	averagePingTime = averagePingTime/3*1000
	if(sVerbose):
		print "Ping time = "+str(averagePingTime)+" ms."
	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('job','ping'),('value',averagePingTime)]
	queryServer(payload)
	return

def printTimedList(timedData):
	if timedListNumber != timedData.__len__():
		print 'Queue has been changed on server side.'
	for timed in timedData:
		appliance = str(timed.split(':')[0])
		command = str(timed.split(':')[1])
		terminal_times = float(timed.split(':')[2])
		print 'Program is going to ' + command + ' on ' + appliance + ' in ' + str(int(math.ceil((terminal_times-currentTime)/60))) + ' minutes.'
	return timedData.__len__()

def timedDelete():
	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('type','timed'),('action','timeup')]
	payload=urllib.urlencode(payload)
	url	= base+ 'readData.php'
	req=urllib2.Request(url, payload)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
#	data = urllib2.urlopen(req).read()
	for i in range(limitTry):
		try: urllib2.urlopen(req, timeout=timeout).read()
		except urllib2.URLError:
			if(verbose|sVerbose):
				print 'Timed out for deleting timed process.'
			if(i<limitTry-1):
				if(verbose|sVerbose):
					print 'Trying again...('+str(i+2)+')'
			else:
				if(verbose|sVerbose):
					print 'Limit reached ('+str(i+1)+'), moving on to next process.'
		except:
			if(verbose|sVerbose):
				print 'Error from other cause, moving on to next process.'
			break
		else:
			break
	return

def serverCheck(connectionHealth):
	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('job','keep-alive')]
	payload=urllib.urlencode(payload)
	url	= base+ 'homeAndServer.php'
	req=urllib2.Request(url, payload)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
#	urllib2.urlopen(req, timeout=3).read()
	for i in range(limitTry):
		try: urllib2.urlopen(req, timeout=timeout).read()
		except urllib2.URLError:
			if(verbose|sVerbose):
				print 'Timed out for keep-alive process.'
			if(i<limitTry-1):
				if(verbose|sVerbose):
					print 'Trying again...('+str(i+2)+')'
			else:
				if(verbose|sVerbose):
					print 'Limit reached ('+str(i+1)+'), moving on to next process.'
				connectionHealth=connectionHealth+1
				if(connectionHealth>=5):
					print time.asctime(time.localtime(time.time()))
					print base + ' cannot be reached at this moment.'
#					print 'Server cannot be reached at this moment.'
					print 'Wait '+str(sleepWaitTime)+' minutes before continuing...'
					if(verbose|sVerbose):
						for i in range(sleepWaitTime):
							print str(sleepWaitTime-i) + ' minute(s) left...'
							time.sleep(60)
							print time.asctime(time.localtime(time.time()))
					else:
						time.sleep(sleepWaitTime*60)
						print time.asctime(time.localtime(time.time()))
					connectionHealth=0
		except:
			if(verbose|sVerbose):
				print 'Error from other cause, moving on to next process.'
			break
		else:
			break
	return connectionHealth

#if os.path.isfile(sessionFile):
#	print 'Previous session exists.'
#	choice = raw_input('Do you want to continue(Y/N)?: ')
#	if (choice.lower()=='n') | (choice==''):
#		os.remove(sessionFile)
#		print 'Previous session is cleared.'
#	else:
#		my_shelf = shelve.open(sessionFile)
#		for key in my_shelf:
#			globals()[key]=my_shelf[key]
#		my_shelf.close()
#		print 'Continue session after reboot/failed...'
#		print time.asctime(time.localtime(time.time()))

while(True):
#	my_shelf = shelve.open(sessionFile,'n') # 'n' for new
#	for key in dir():
#		try:
#			my_shelf[key] = globals()[key]
##		except TypeError:
#			#
#			# __builtins__, my_shelf, and imported modules can not be shelved.
#			#
##			print('ERROR shelving: {0}'.format(key))
#		except:
#			pass
#	my_shelf.close()
	
	connectionHealth = serverCheck(connectionHealth)
	
	currentTime = time.time()
	if pingStatTime < currentTime:
		pingStatTime = currentTime+60;
		statServer()
	
#	print time.strftime('%l:%M:%S%p %Z on %b %d, %Y',time.localtime(currentTime))
	if(wait_time < 1) & displayFlag:
		print time.asctime(time.localtime(currentTime))
	elif(wait_time > 0):
		print time.asctime(time.localtime(currentTime))

#	for i in reversed(range(timing_appliance.__len__())):
#		if(timing_appliance[i][2]<currentTime):
#			if(timing_appliance[i][1]=='arrive'):
#				print 'User is supposed to be home.'
#				wait_time = 0
#			elif(timing_appliance[i][1]=='depart'):
#				print 'User left home.'
#				wait_time = 30
#			else:
#				print 'SIMULATE AS IF RASPI GPIO HAD BEEN EXECUTED.'
#				print time.asctime(time.localtime(currentTime))
#				print 'Program has ' + timing_appliance[i][1] + ' ' + timing_appliance[i][0]
#			timing_appliance.remove(timing_appliance[i])
#			timedDelete()
	if timed_appliance:
		if(timed_appliance[2]<currentTime):
			if(timed_appliance[1]=='arrive'):
				print 'User is supposed to be home.'
				wait_time = 0
			elif(timed_appliance[1]=='depart'):
				print 'User left home.'
				wait_time = 30
			else:
				print 'SIMULATE AS IF RASPI GPIO HAD BEEN EXECUTED.'
				print timed_appliance[0].split('_')[1]
				vendorName = timed_appliance[0].split('_')[1]
				applianceType = timed_appliance[0].split('_')[0]
				print timed_appliance[1].split('_')[1]
				commandType = timed_appliance[1].split('_')[0]
				commandName = timed_appliance[1]
				print timed_appliance[2]
				if commandType == "KEY":
					# INFRARED-TYPE COMMANDS
					print 'subprocess.call(exec irsend SEND_ONCE '+vendorName+' '+commandName+' &,shell=True)'
				else:
					# MECHANICAL SWITCHES
					print 'Mechanical switches command has been executed.'
					
				print time.asctime(time.localtime(currentTime))
				print 'Program has ' + timed_appliance[1] + ' ' + timed_appliance[0]
			timed_appliance=[]
			timedDelete()

		
	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('type','timed')]
	payload=urllib.urlencode(payload)
	url	= base+ 'readData.php'
	req=urllib2.Request(url, payload)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
#	timedData = urllib2.urlopen(req, timeout=timeout).read()
	timedData = tryQueryServer(req, "Unreachable\n")
	timedData = timedData.decode('utf-8').split('\n')
#	print timedData
#	print timedData[0]
	if((timedData[0][0:5]=='Empty') & (timed_appliance!=[])):
		print 'Timed command has been cleared, according to server data.'
		timed_appliance=[]
	if((timedData[0][0:5]!='Empty')&(timedData[0][0:11]!='Unreachable')):
		data = timedData[0]
		appliance = str(data.split(':')[0])
		command = str(data.split(':')[1])
		terminal_times = float(data.split(':')[2])
#		times = float(re.search("(\\d+)", data.split(':')[2]).group())
#		times = float(data.split(':')[2])
		if(wait_time < 1) & displayFlag:
			timedListNumber = printTimedList(timedData)
		elif(wait_time > 0):
			timedListNumber = printTimedList(timedData)
#		print 'Program is going to ' + command + ' on ' + appliance + ' in ' + str((terminal_times-currentTime)/60) + ' minutes.'
#		print time.strftime('%l:%M%p %Z on %b %d, %Y',time.localtime(time.time()))
#		print time.asctime(time.localtime(time.time()))
#		print time.asctime(time.localtime(c+600))
#		print time.strftime('%l:%M:%S%p %Z on %b %d, %Y')
#		terminal_times = (times*60)+currentTime
#		print 'Which is going to be: ' + time.asctime(time.localtime(terminal_times))
#		timing_appliance.append([appliance,command,terminal_times])
		timed_appliance = [appliance,command,terminal_times];
#		payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('type','timed')]
#		#The first is the var name the second is the value
#		payload=urllib.urlencode(payload)
#		url	= base+ 'readData.php'
#		req=urllib2.Request(url, payload)
#		req.add_header("Content-type", "application/x-www-form-urlencoded")
#		data = urllib2.urlopen(req).read()
#		data = data.decode('utf-8').split('\n')[0]
		if wait_time > 0:
			time.sleep(0.1)
	if(timedData[0][0:5]=='Empty'):
		if(wait_time < 1) & displayFlag:
			print 'There is no queue currently for timing process.'
		elif(wait_time > 0):
			print 'There is no queue currently for timing process.'
	elif(timedData[0][0:11]=='Unreachable'):
#		print 'Timed Error'
		print 'Server is currently unreachable.'
	
	payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('type','instance')]
	payload=urllib.urlencode(payload)
	url	= base+ 'readData.php'
	req=urllib2.Request(url, payload)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
#	data = urllib2.urlopen(req).read()
	data = tryQueryServer(req, "Unreachable\n")
	data = data.decode('utf-8').split('\n')[0]
#	print data
	while((data[0:5]!='Empty')&(data[0:11]!='Unreachable')):
#		print data
		appliance = data.split(':')[0]
		command = data.split(':')[1]
		times = int(re.search("(\\d+)", data.split(':')[2]).group())
		#		times = float(data.split(':')[2])
		for i in range(times):
			print 'SIMULATE AS IF RASPI GPIO HAD BEEN EXECUTED.'
			print appliance.split('_')[1]
			vendorName = appliance.split('_')[1]
			applianceType = appliance.split('_')[0]
			print command.split('_')[1]
			commandType = command.split('_')[0]
			commandName = command
			print command
			if commandType == "KEY":
				# INFRARED-TYPE COMMANDS
				print 'subprocess.call(exec irsend SEND_ONCE '+vendorName+' '+commandName+' &,shell=True)'
			else:
				# MECHANICAL SWITCHES
				print 'Mechanical switches command has been executed.'
			time.sleep(0.1)
			
		print 'Program is going to ' + command + ' ' + appliance + ' for ' + str(times) + ' times.'
		payload=[('hashedPassword','e4d3d3f0fce651d09aee5480ec5e58268ccc2409'),('type','instance')]
		#The first is the var name the second is the value
		payload=urllib.urlencode(payload)
		url	= base+ 'readData.php'
		req=urllib2.Request(url, payload)
		req.add_header("Content-type", "application/x-www-form-urlencoded")
#		data = urllib2.urlopen(req).read()
		data = tryQueryServer(req, "Unreachable\n")
		data = data.decode('utf-8').split('\n')[0]
		if wait_time > 0:
			time.sleep(0.1)
		
	if(data[0:5]=='Empty'):
		if(wait_time < 1) & displayFlag:
			print 'There is no queue currently for instance process.'
		elif(wait_time > 0):
			print 'There is no queue currently for instance process.'
	elif(data[0:11]=='Unreachable'):
		print 'Server is currently unreachable.'
			
	if wait_time > 0:
		if not timed_appliance:
			if(verbose|sVerbose):
				print "Sleep for " + str(wait_time) + " seconds."
			time.sleep(wait_time)
		else:
			if (time.time()+wait_time>timed_appliance[2]):
				if(verbose|sVerbose):
					print "Sleep for " + str(time.time()+wait_time-timed_appliance[2]) + " seconds."
				time.sleep(time.time()+wait_time-timed_appliance[2])
			else:
				if(verbose|sVerbose):
					print "Sleep for " + str(wait_time) + " seconds."
				time.sleep(wait_time)

	if (wait_time < 1) & displayFlag:
		displayFlag = False
		nextDisplayTime = currentTime + timeoutForDisplay
#		print time.asctime(time.localtime(currentTime))
#		time.sleep(5)
	elif(wait_time < 1) & (nextDisplayTime < currentTime):
		displayFlag = True
#		time.sleep(5)
