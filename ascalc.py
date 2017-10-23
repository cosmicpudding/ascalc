#!/usr/bin/env python2.7
# APERTIF SOURCE CALCULATOR (ascalc.py)
# Will calculate start/end times for sources given a time period
# Input: source text file, start date/time, duration in hours
# V.A. Moss 23/10/2017 (vmoss.astro@gmail.com)

import os
import sys
from astropy.io import ascii
import datetime
import ephem

# Specific format required: name, ra, dec (sexagesimal)
d = ascii.read('sources.txt')

# Note: all calculations take place in Universal Time
date = '2017-10-20'
UT = '15:00:00'
duration = 63 # hours


print """           _____  ______ _____ _______ _____ ______                     
     /\   |  __ \|  ____|  __ \__   __|_   _|  ____|                    
    /  \  | |__) | |__  | |__) | | |    | | | |__                       
   / /\ \ |  ___/|  __| |  _  /  | |    | | |  __|                      
  / ____ \| |    | |____| | \ \  | |   _| |_| |                         
 /_/____\_\_|_  _|______|_|_ \_\_|_| _|_____|_|                         
  / ____|/ __ \| |  | |  __ \ / ____|  ____|                            
 | (___ | |  | | |  | | |__) | |    | |__                               
  \___ \| |  | | |  | |  _  /| |    |  __|                              
  ____) | |__| | |__| | | \ \| |____| |____                             
 |_____/ \____/ \____/|_|__\_\\_____|______|       _______ ____  _____  
  / ____|   /\   | |    / ____| |  | | |        /\|__   __/ __ \|  __ \ 
 | |       /  \  | |   | |    | |  | | |       /  \  | | | |  | | |__) |
 | |      / /\ \ | |   | |    | |  | | |      / /\ \ | | | |  | |  _  / 
 | |____ / ____ \| |___| |____| |__| | |____ / ____ \| | | |__| | | \ \ 
  \_____/_/    \_\______\_____|\____/|______/_/    \_\_|  \____/|_|  \_\ \n"""

def dec2str(dec):
    if not dec:
        return None
    neg = 0
    if dec < 0:
        dec *= -1
        neg = 1
    dd = int(dec)
    diff = dec - dd
    mm = int(diff*60)
    diff = diff - (mm/60.0)
    ss = diff*3600
    if ss >= 59.995:
        ss = 00.0
        mm += 1

    if neg:
        str = '-%02d:%02d:%05.2f' % (dd, mm, abs(ss))
    else:
        str = '%02d:%02d:%05.2f' % (dd, mm, abs(ss))
    return str

# Define the location of APERTIF
loc = ephem.Observer()
loc.lon = dec2str(6.60334)
loc.lat = dec2str(52.91474)
loc.elevation = 17
loc.date = '%s %s' % ('/'.join(date.split('-')),UT)
loc.horizon = '10:00:00' # degrees

# Start by calculating end time/date
print 
sdate = datetime.datetime.strptime(date+UT,'%Y-%m-%d%H:%M:%S')
print 'Start time of observations:', sdate
edate = sdate + datetime.timedelta(hours=duration)
print 'End time of observations:',edate
print

currdate = datetime.datetime.strptime(date+UT,'%Y-%m-%d%H:%M:%S')

# Loop through, in 24 hour jumps to calculate each rise time
while currdate < edate:
	print
	print '##############################################'
	print

	# Check the location date, which will be fed to pyephem
	loc.date = '%s %s' % ('/'.join(date.split('-')),UT)
	print 'Current date/time:',loc.date
	print

	for i in range(0,len(d)):

		# Get the source name
		src = d['src'][i]
		brd = '*'*20
		print brd
		print src
		print brd

		# Get the source position
		ra,dec = d['ra'][i],d['dec'][i]
		print ra,dec

		# Define the source (labelled as star though obviously it's most likely not a star)
		star = ephem.FixedBody()
		star._ra = ra
		star._dec = dec
		star.compute(loc)

		# Check its properties
		print 'Circumpolar? ',star.circumpolar
		print 'Never rises? ',star.neverup
		print 'Transit time: %s' % (loc.next_transit(star))
		if star.circumpolar == False:
			print 'Rise time: %s' % loc.previous_rising(star,start=loc.date)
			print 'Set time: %s' % loc.next_setting(star,start=loc.date)

		# Transit time, get the hour angle and then figure out what time the +/- 6 hours are?
		transit = datetime.datetime.strptime(str(loc.next_transit(star)),'%Y/%m/%d %H:%M:%S')
		src_start = transit-datetime.timedelta(hours=6)
		src_end = transit+datetime.timedelta(hours=6)
		src_diff = (src_start-sdate).seconds

		# Add an asterisk in the case that the end time is longer than possible to schedule
		if src_end > edate:
			add = '*'
		else:
			add = ''

		# Print the suggested start time, based on +/-6 hr of the transit time
		print
		print 'Start time (UTC): %s' % src_start
		print 'End time (UTC): %s' % src_end+add
		print
	
	# Move forward +1 day, to calculat the next rise/set times
	newdate = datetime.datetime.strptime(date+' '+UT,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(days=1)
	print 'Updating new start time...'
	date = datetime.datetime.strftime(newdate,'%Y-%m-%d')
	UT = datetime.datetime.strftime(newdate,'%H:%M:%S')
	currdate = datetime.datetime.strptime(date+UT,'%Y-%m-%d%H:%M:%S')

# Finish
print
print '##############################################'
print
print 'Endtime reached!'

