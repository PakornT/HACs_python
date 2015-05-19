#!/usr/bin/python

import re

data = '1:2:312<--test text'
print data
if __name__ == '__main__':
	found = re.search("(\\d+)", data.split(':')[2]).group()
	print found
#	times = float(re.search("(\\d+)", data.split(':')[2]))