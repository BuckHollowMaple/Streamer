#!/usr/bin/python
import redis
import os
import sys
import re
import numpy as np
import pandas as pd
import requests
import string
import subprocess
from text2math import text2math
from bs4 import BeautifulSoup
from time import sleep
from unidecode import unidecode
from random import randint
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display

# Trend vars
trendSize = []
i = 0
while True:
    trendSize.append(i)
    if len(trendSize) == 15:
	break
trendList = list(range(15))

# Cleanup past processes
os.system('killall Xvfb >/dev/null 2>&1')
os.system('killall geckodriver >/dev/null 2>&1')
os.system('killall node >/dev/null 2>&1')
if (not 'NETWORK' in sys.argv[1:]):
	os.system('killall peerflix >/dev/null 2>&1')
	os.system('killall vlc >/dev/null 2>&1')

# Local vars
command = ''
DEBUG = False
formats = ['movie','show','song','book','youtube']
ex_cmds = ['next','weather','previous','last','latest','newest','what','who','when','where','last','episode','suggest','suggestion','play','played','star','year','radio','news']
removewords = ['for','the','from','an','a']
stopwords = ['old','new','original','newest']
start_stream = ["I'm starting the stream now","The stream is starting now","The stream will play shortly","Starting the stream soon"]
season_s = ['season','series','s.']
episode_s = ['episode','ep.','ep']
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',}

# Redis local memory
memory = redis.StrictRedis(host='192.168.1.130', port=6379, db=0)
if not memory.get('mpsyt_count'): memory.set('mpsyt_count','1')
if not memory.get('ims_percentage'): memory.set('ims_percentage','0')

# For pandas in trend determination
def trendline(data, order=1):
    coeffs = np.polyfit(data.index.values, list(data), order)
    slope = coeffs[-2]
    return float(slope)

# Gets the weather forecast and displays the radar as long as there is text
def weather():
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',}
	resp = requests.get('http://www.wcax.com/weather',headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')	
	t = soup.findAll("div", {"class": "media-body"})
	weather_desc = t[2].text.replace('Gary','Alicia').replace('Sharon','Alicia').replace('\n','')
	weather_desc = '. '.join(weather_desc.split('. ')[:2])
	memory.set('ttsOverride',weather_desc)
	os.system('rm /root/Downloads/NatLoop.gif >/dev/null 2>&1')
	os.system('cd /root/Downloads/ && wget https://radar.weather.gov/Conus/Loop/NatLoop.gif >/dev/null 2>&1')
	os.popen('eog /root/Downloads/NatLoop.gif -f 2>/dev/null')
	# Wait for silence to be broken by ttsoverride
	if ('closed' in os.popen('head -1 /proc/asound/card0/pcm3p/sub0/status').read()):
		while ('closed' in os.popen('head -1 /proc/asound/card0/pcm3p/sub0/status').read()):
			sleep(1)
	# Wait until the weather report is finished
	while (not 'closed' in os.popen('head -1 /proc/asound/card0/pcm3p/sub0/status').read()):
		sleep(1)
	os.system('killall oeg >/dev/null 2>&1')

# Checks to see if the movie name is right
def check_mname(name):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',}
	URL = 'https://www.google.com/search?q='+'+'.join(name.split())+'+movie+wikipedia'
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	a = soup.findAll("a")
	for each in a:
		text = unidecode(each.text)
		if text and ('Wikipedia' == text.split()[-1]):
			f_text = text.split(' - Wikipedia')[0].replace('-',' ').translate(None, string.punctuation).upper()
			split_test = [word for word in f_text.split() if word.isdigit() and (len(word) != 1)]
			if split_test:
				f_text = f_text.split(split_test[0])[0]
			return ' '.join([word for word in f_text.split() if (word[0].isupper()) or ((word[0].isdigit() and (len(word) == 1)))]).lower().replace('tv','').replace('movie','').strip()
	else:
		return ''

# Searches any page for a mp4
def defaultSearch(buildup):
	resp = requests.get(buildup,headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	s = soup.findAll('script')
	t = soup.findAll("video")
	test = ''
	for each in s:
		text = unidecode(each.text)
		if 'mp4' in text:
			test = ('http'+text.split('mp4')[0].split('http')[-1]+'mp4').replace('https','http')
	if test: return test
	test = ''
	for each in t:
		text = unidecode(each)
		if ('mp4' in text) and ('src' in text):
			test = (text.split('mp4')[0].split('src="')[-1]+'mp4')
	if test: return test
	else: return ''

# Tries primewire to find show/movie
def primewire(name,type):
	# Parses the search parameters into separate variables
	if ('s0' in name):
		build_URL = 's0'+name.split('s0')[1]
		name = name.split('s0')[0].strip()
	elif ('s1' in name):
		build_URL = 's1'+name.split('s1')[1]
		name = name.split('s1')[0].strip()
	else: build_URL = ''
	orig_build = build_URL
	year = ''
	# Removes year from movie
	if ('movie' in type):
		year = ''.join(name.split()[-1]).strip()
		name = ' '.join(name.split()[:-1]).strip()
	# Init local vars
	addon_URL,final_URL,load_type = '','',''
	addons,addons_b,addons_c,addons_d,addons_e,addons_f,addons_g = [],[],[],[],[],[],[]
	addons_alt = []
	# Bring up primewire search on the search keywords
	if 'movie' in type: URL = 'https://www.primewire.life/?search_keywords='+'+'.join(name.split())
	else: URL = 'https://www.primewire.life/index.php?tv&search_keywords='+'+'.join(name.split())
	
	resp = requests.get(URL,headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("a")
	# Finds and selects first title in search menu (later can be semantic/syntax related)
	for each in t:
		#print unidecode(each.text)
		if '(' in unidecode(each.text).lower():
			if ('show' in type) or (('movie' in type) and year and (unidecode(each.text).split('(')[1].split(')')[0] == year)):
				addon_URL = unidecode(each['href'])
				break
	else:
		memory.set('ttsOverride',"There weren't any titles under that name. Sorry")
		sys.exit()
	# Finds the season and episode, if the type is a show
	if 'show' in type:
		memory.set('imsAfterShow',name+" "+build_URL[:-6]+'season '+str(int(build_URL[-5:][:2]))+' episode '+str(int(build_URL[-5:][3:])+1))
		memory.set('imsBeforeShow',name+" "+build_URL[:-6]+'season '+str(int(build_URL[-5:][:2]))+' episode '+str(int(build_URL[-5:][3:])-1))
		try:
			build_URL = ('season-'+build_URL[1:].replace('e','-episode-')).replace('-0','-')
			URL = 'https://www.primewire.life'+addon_URL
			resp = requests.get(URL)
			soup = BeautifulSoup(resp.text, 'html.parser')
			t = soup.findAll("a")
			for each in t:
				if build_URL in unidecode(each['href']):
					addon_URL = unidecode(each['href'])
					break
		except:
			# End of the season, go to the next
			next_season = str(int(parse_media(memory.get('imsAfterShow'))[-5:][:2])+1)
			if 's0' in orig_build: build_URL = 's0'+(parse_media(memory.get('imsAfterShow'))[:-6]+'s0'+next_season+'e01').split('s0')[1]
			elif 's1' in orig_build: build_URL = 's1'+(parse_media(memory.get('imsAfterShow'))[:-6]+'s1'+next_season+'e01').split('s1')[1]
			build_URL = ('season-'+build_URL[1:].replace('e','-episode-')).replace('-0','-')
			URL = 'https://www.primewire.life'+addon_URL
			resp = requests.get(URL)
			soup = BeautifulSoup(resp.text, 'html.parser')
			t = soup.findAll("a")
			for each in t:
				try:
					if build_URL in unidecode(each['href']):
						addon_URL = unidecode(each['href'])
						break
				except:
					pass
	# Gathers information on the show/movie page to parse from
	URL = 'https://www.primewire.life'+addon_URL
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("a",title=True)
	s = soup.findAll("span", {"class": "version_host"})
	# Build up the site list for selection
	sitename_list = []
	siteurl_list = []

	for each in s:
		sitename_list.append(each.text.replace('\n',''))
	for each in t:
		if 'Version' in each.text: siteurl_list.append(each['href'])
	# Finds the best version selection from the title's page
	for x in xrange(0, len(siteurl_list)):
		try:
			if 'openload.' in sitename_list[x]: addons.append(siteurl_list[x])
			elif 'vidto.' in sitename_list[x]: addons_b.append(siteurl_list[x])
			elif 'rapidvideo.' in sitename_list[x]: addons_c.append(siteurl_list[x])
			elif 'vidup.' in sitename_list[x]: addons_d.append(siteurl_list[x])
			elif 'vidlox.' in sitename_list[x]: addons_e.append(siteurl_list[x])
			elif 'speedvid.' in sitename_list[x]: addons_f.append(siteurl_list[x])
			elif 'gorillavid.' in sitename_list[x]: addons_g.append(siteurl_list[x])
		except: pass
	print str(addons)
	print str(addons_b)
	print str(addons_c)
	print str(addons_d)
	print str(addons_e)
	print str(addons_f)
	print str(addons_g)
	# Between these 5 types of magnets, any show/movie should be accessable 
	if addons or addons_b or addons_c or addons_d or addons_e or addons_f or addons_g:
		# Processes openload magnets (quickest)
		for x in xrange(0, len(addons)):
			'''
			URL = 'https://www.primewire.life'+addons[x]
			resp = requests.get(URL)
			soup = BeautifulSoup(resp.text, 'html.parser')
			u = soup.findAll("meta")
			for each in u:
				try: 
					if 'https://openload' in unidecode(each['content']):
						final_URL = unidecode(each['content'])
						break
				except:
					pass
			if final_URL:
				print final_URL
				test = max(os.popen("cd /root/Scripts/Alicia/casperjs/primewire && phantomjs --ssl-protocol=any getShowURL.js %s 2>/dev/null" % final_URL).read().split('\n'),key=len)
				if test and (not 'undefined is not an object' in test) and (not '|' in test): return test
			'''
			pass
		else:
			# Processes vidloz magnets (2nd quickest)
			for q in xrange(0,len(addons_e)):
				buildup = 'https://www.primewire.life'+addons_e[q]
				test = defaultSearch(buildup)
				if ('http' in test) and (not '|' in test):
					return test
			else:
				# Processes rapidvideo magnets (2nd quickest)
				for y in xrange(0, len(addons_c)):
					buildup = 'https://www.primewire.life'+addons_c[y]
					test = defaultSearch(buildup)
					if ('http' in test) and (not '|' in test):
						return test
				else:
					# Process speedvid magnets (2nd quickest)
					for n in xrange(0, len(addons_f)):
						buildup = 'https://www.primewire.life'+addons_f[n]
						resp = requests.get(buildup,headers=headers)
						soup = BeautifulSoup(resp.text, 'html.parser')
						try: test = 'http'+(soup.text).split('mp4')[1].split('http')[-1]+'mp4'
						except: test = ''
						if ('http' in test) and (not '|' in test):
							return test
					else:
						# Processes vidto magnets (takes 15+ sec)
						for z in xrange(0, len(addons_b)):
							buildup = 'https://www.primewire.life'+addons_b[z]
							test = os.popen("cd /root/Scripts/Alicia/casperjs/primewire && casperjs vidtoURL.js --url='%s' 2>/dev/null" % buildup).read()
							if test and (not 'undefined is not an object' in test) and (not '|' in test): return test
						else:
							for r in xrange(0, len(addons_g)):
								full = 'https://www.primewire.life'+addons_g[r]
								test_url = os.popen('casperjs /root/Scripts/Alicia/casperjs/getURL.js --url="%s"' % full).read()
								buildup = 'https://www.tubeoffline.com/downloadFrom.php?host=Gorillavid&video='+test_url
								resp = requests.get(buildup,headers=headers)
								soup = BeautifulSoup(resp.text, 'html.parser')
								a = soup.findAll("a")
								for each in a:
									if each.text == 'DOWNLOAD':
										return each['href']
	elif addons_alt:
		for x in xrange(0, len(addons_alt)):
			URL = 'https://www.primewire.life'+addons_alt[x]
			test = defaultSearch(URL)
			if ('http' in test) and (not '|' in test):
				return test
	return ''

# Finds a stream for a radio station
def radioMagnet(station,type):
	headers = {
	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
	}
	# Build the call sign
	if (len([word for word in station.split() if len(word) == 1]) >= 4) and (type == 'radio'):
		raw = [word.upper() for word in station.split() if len(word) == 1]
		if len(raw) != 4:
			try: raw[raw.index('W'):][:4]
			except: raw[raw.index('K'):][:4]
		station = ''.join(raw)
	# Description of the radio station to find call sign
	if (len(station) != 4) and (type == 'radio'):
		try:
			callnum = [call for call in station.split() if (len(call)<=5) and ('.' in call)]
			URL = 'https://www.google.com/search?q=radio+station+'+'+'.join(station.split())
			if callnum: URL = URL.replace(callnum[0],'"'+callnum[0]+'"')
			resp = requests.get(URL,headers=headers)
			soup = BeautifulSoup(resp.text, 'html.parser')	
			t = soup.findAll('a')
			collect = ''
			for each in t:
				collect += unidecode(each.text).replace('.',' ').replace(',',' ').replace('-',' ')+" "
			words = [word for word in re.findall(r'\w+',collect) if (len(word) == 4) and (word.isupper()) and ((word[0] == 'W') or (word[0] == 'K'))]
			station = Counter(words).most_common()[0][0]
		except Exception as e:
			print e
			return "Error: Google wants a captcha"
	# Check if the stream is already known
	if memory.get('radiostream_'+'_'.join(station.split())):
		return memory.get('radiostream_'+'_'.join(station.split()))+"|||"+station
	else:
		memory.set('ttsOverride',"The first time will take a bit")
	# Called with 4 letter call sign
	try:
		if type == 'radio':
			URL = 'https://www.google.com/search?q=inurl%3Aradio-locator.com+'+station
			resp = requests.get(URL,headers=headers)
			soup = BeautifulSoup(resp.text, 'html.parser')
			t = soup.findAll("cite", {"class": "_Rm"})
			for each in t:
				if station in unidecode(each.text):
					URL = unidecode(each.text)
					resp = requests.get(URL,headers=headers)
					soup = BeautifulSoup(resp.text, 'html.parser')
					t = soup.findAll('a')
					if not ('http' in t[13].text) and (len(soup.text) < 500):
						URL = 'https://radio-locator.com'+unidecode(t[13]['href']).replace('call','bc=y&call')+'&rd=421801'
						resp = requests.get(URL,headers=headers)
						soup = BeautifulSoup(resp.text, 'html.parser')
						if 'File1' in soup.text: return unidecode(soup.text).split('File1=')[1].split('\r\n')[0]+"|||"+station
						elif len(soup.text) < 300: return unidecode(soup.text).replace('\r\n','')+"|||"+station
						else:
							return "Error: Nothing found"
		if type == 'radio': URL = 'https://www.google.com/search?q=inurl%3Atunein.com%2Fradio+stream++"'+station+'"'
		else: URL = 'https://www.google.com/search?q=inurl%3Atunein.com+stream+'+'+'.join(station.split())
		resp = requests.get(URL,headers=headers)
		soup = BeautifulSoup(resp.text, 'html.parser')
		t = soup.findAll("cite", {"class": "_Rm"})
		tune_URL = unidecode(t[0].text)
		# Use selenium on tunein radio link
		# Selenium profile vars
		# --- Full screen ---
		driver.get('http://localhost')
		driver.find_element_by_xpath('/html/body').send_keys(Keys.F11)
		# -------------------
		opts = Options()
		opts.binary = "/opt/firefox/firefox"
		profile = webdriver.FirefoxProfile()
		profile.set_preference("permissions.default.image", 2)
		display = Display(visible=0, size=(800, 600))
		display.start()
		driver = webdriver.Firefox(firefox_profile=profile,firefox_options=opts)
		try:
			driver.set_page_load_timeout(15)
			driver.get(tune_URL)
		except:
			timer = 0
			while True:
				test = str(driver.find_element_by_tag_name('audio').get_attribute("src")).split('?')[0]
				if ('streamthe' in test) or (timer > 15): break
				sleep(0.2)
				timer += 1
		driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w') 
		driver.close()
		display.stop()
		if test: return test+"|||"+station
		else: return 'Error: Could not get tunein link'
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print e
		# Reset the router to change the IP
		# Google and/or Radio-locator is sick of catering to you
		return "Error: General"

# Returns the season and episode of the description of a show
def search_show(show):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',}
	URL = 'https://www.google.com/search?q=episode'+'+'.join(show.split())
	show = show.split('of')[1].split('where')[0].split('when')[0].strip()
	resp = requests.get(URL,headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')	
	t = soup.findAll('a')
	u = soup.findAll("span", {"class": "st"})
	v = soup.findAll("div", {"class": "_qgd"})
	w = soup.findAll("cite", {"class": "_Rm"})
	season = 0
	episode = 0
	marker = []
	search = ''	
	imdb_test = [link for link in w if 'imdb' in unidecode(link.text)]
	wiki_test = [link for link in w if 'wikipedia' in unidecode(link.text)]

	if imdb_test: search = 'imdb'
	elif wiki_test: search = 'wikipedia'

	# Searches through imdb and wikipedia for data
	if search:
		if search == 'imdb': l_URL = imdb_test[0].text.split('/review')[0]
		else: l_URL = wiki_test[0].text
		if not 'http' in l_URL:
			l_URL = 'http://'+l_URL
		resp = requests.get(l_URL,headers=headers)
		soup = BeautifulSoup(resp.text, 'html.parser')
		i = soup.findAll("i")
		a = soup.findAll("a",title=True)
		if search == 'imdb': marker = soup.findAll("div", {"class": "bp_heading"})
		else: marker = soup.findAll(['th','td'])
		# We're in wiki and we'll change the show name if it's specific
		if i and ('wiki' in l_URL): 
			for each in i:
				text = unidecode(each.text).lower()
				if text.startswith(show): show = text.translate(None, string.punctuation)
		# We're in imdb
		elif a and ('imdb' in l_URL):
			for each in a:
				text = unidecode(each.text).lower()
				if text.startswith(show): show = text.translate(None, string.punctuation)
		# Get the rest of the miserable data
		for y in xrange(0, len(marker)):
			try:
				text = unidecode(marker[y].text).lower()
				season_test = [key for key in text.split() if key in season_s]
				episode_test = [key for key in text.split() if key in episode_s]
				season = int(text.split(season_test[0])[1].split()[0].translate(None, string.punctuation))
				episode = int(text.split(episode_test[0])[1].split()[0].translate(None, string.punctuation))
				if (season != 0) and (season <= 15) and (episode != 0) and (episode <= 35): break
			except: pass
	# Searches through the google data if nothing important was found
	if (season == 0) or (season >= 15) or (episode == 0) or (episode >= 35): 
		for y in xrange(0,3):
			listing = []
			if y == 0: listing = t
			elif y == 1: listing = u
			elif y == 2: listing = v
			for x in xrange(0,len(listing)):
				try:
					test = unidecode(listing[x].text).lower()
					season_test = [key for key in test.split() if key in season_s]
					episode_test = [key for key in test.split() if key in episode_s]
					if season_test and episode_test:
						season = int(test.split(season_test[0])[1].split()[0].translate(None, string.punctuation))
						if '0' in str(season): season = int(season.split('0')[1])
						episode = int(test.split(episode_test[0])[1].split()[0].translate(None, string.punctuation))
						if '0' in str(episode): episode = int(episode.split('0'
)[1])
						if (season != 0) and (season <= 15) and (episode != 0) and (episode <= 35): break
						else: season,episode = 0,0
				except:
					pass
				if (season != 0) and (season <= 15) and (episode != 0) and (episode <= 35): break
	if (season != 0) and (episode != 0): return 'season '+str(season)+' episode '+str(episode)
	else: return ''	

# Get movie year
def movie_year(show):
	URL = 'https://www.google.com/search?q='+'+'.join(show.split())+" movie"
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("a")
	for each in t:
		text = repr(each.text).lower()
		if (show in text) and ('(' in text) and (text.split('(')[1].split(')')[0].isdigit()): return text.split('(')[1].split(')')[0]
		else:
			text = text.translate(None, string.punctuation)[1:]
			for x in xrange(0, len(show.split())):
				section = ' '.join(show.split()[x:])
				if (section in text):
					try:
						test = text.split(section)[1].strip().split()[0]
						if (test.isdigit()) and (len(test) == 4): return test
					except:
						pass

# Find actors from a show
def find_actors(show):
	URL = 'https://www.google.com/search?q='+'+'.join(show.split())+'+actors'
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("a", {"class": "fl"},title=True)
	listing = []
	for each in t:
		if '(' in each['title']:
			test = repr(each['title']).split('(')[1].split(')')[0]
			if not test.isdigit(): listing.append(repr(each['title']).split('(')[0].strip().replace("u'","").replace('u"',''))
	if [s for s in listing if len(s.split()) != 2]:
		listing = []
		for each in t:
			if '(' in each['title']:
				test = repr(each['title']).split('(')[1].split(')')[0]
				if not test.isdigit(): listing.append(repr(each['title']).split('(')[1].strip().replace("u'","").replace('u"','').split(',')[0].split(')')[0].replace('"','').replace("'",""))
	return listing[:4]

# Get actor's shows
def suggest_actor_content(actor):
	URL = 'https://www.google.com/search?q='+'+'.join(actor.split())
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("a", {"class": "fl"},title=True)
	listing = []
	for each in t:
		if '(' in each['title']:
			test = repr(each['title']).replace('\u','').split('(')[1].split(')')[0]
			if test.isdigit(): listing.append(str(each['title']).split('(')[0].strip())
	return listing

# Suggests media from genre for the type
def suggest_media(genre,type):
	if ('show' in type):
		ttype = 'tv_series'
	elif 'movie' in type:
		ttype = 'movies'
	URL = 'http://www.imdb.com/search/title?genres=%s&title_type=%s&sort=num_votes,desc' % (genre,ttype)
	resp = requests.get(URL)
	soup = BeautifulSoup(resp.text, 'html.parser')
	u = soup.findAll("p", {"class": "text-muted"})
	t = soup.findAll("a")
	listing = []
	desc = []
	for each in t:
		if ('/title/' in each.get('href')) and ('?ref' in each.get('href')) and (not 'See full summary' in unidecode(each.text)) and (not '\n' in unidecode(each.text)): listing.append(unidecode(each.text))
	for each in u:
		if len(unidecode(each.text)) > 60: desc.append(unidecode(each.text).replace('\n','').split('...')[0])
	listing = listing[:10]
	randnum = randint(0, len(listing)-1)
	return listing[randnum]+"|"+desc[randnum]

# Returns the latest shows season and episode
def latest_show(show):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',}
	URL = 'https://www.google.com/search?q='+'+'.join(show.split())+'+last+episode'
	resp = requests.get(URL,headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("span", {"class": "_Xbe kno-fv"})
	if len(t) >= 3:
		return show+'season '+t[1].text+' episode '+t[2].text

# Parses show details into sXXeXX format
def parse_media(media_name):
	show_name = ''
	if ('season' in media_name.lower()):
	    number = int(media_name.lower().split('season')[1].split()[0])
	    if number < 10: show_name += " s0"+str(number)
	    else: show_name += " s"+str(number)
	else:
	    show_name += " s01"
	if ('episode' in media_name.lower()):
	    number = int(media_name.lower().split('episode')[1].split()[0])
	    if number < 10: show_name += "e0"+str(number)
	    else: show_name += "e"+str(number)
	else:
	    show_name += "e01"
	media_name = media_name.split('season')[0].split('episode')[0].strip() + show_name
	last_ep = int(media_name[-1])
	return media_name

# Returns the magnet link to a torrent
def get_magnet_link(media_name = 'harry potter', type = 'movie', lastResort = False):
    try:
	    original = media_name

	    # Parses show details into a proper format
	    if ('show' in type) and (not 's0' in media_name) and (not 's1' in media_name) and (lastResort == False): media_name = parse_media(media_name)
	    elif ('show' in type): media_name = media_name.split('episode')[0]

	    # Parse the appropriate URL
	    URL = 'https://thepiratebay.org/search/'+media_name+'/0/99/'
	    if (lastResort == True): URL += '0'
	    elif 'movie' in type: URL += '207'
	    elif 'show' in type: URL += '205'
	    elif 'song' in type: URL += '101'
	    elif 'book' in type: URL += '601'

	    # Receive the response
	    resp = requests.get(URL)
	    soup = BeautifulSoup(resp.text, 'html.parser')

	    media_page = soup.find_all("a")
	    media_page_size = soup.find_all("font")
	    media_page_seeders = soup.findAll("td", {"align": "right"})

	    # File sizes for all torrents
	    file_size = []
	    for x in xrange(0,len(media_page_size)):
		size = float(str(media_page_size[x]).split('Size ')[1].split(',')[0].split('\xc2')[0])
		if (size < 20) and (('show' in type) or ('movie' in type)): size = size*1024
		file_size.append(size)	

	    # Seeders for all torrents
	    file_seeders = []
	    for x in xrange(0, len(media_page_seeders)):
		if x % 2 == 0: file_seeders.append(int(str(media_page_seeders[x]).split('>')[1].split('<')[0]))

	    # Magnets for all torrents
	    file_magnet = [s.get('href') for s in media_page if 'magnet' in s.get('href')]

	    # Titles for all torrents
	    file_titles = [s.get('title') for s in media_page if 'torrent' in s.get('href')]
	    # Returns the ideal magnet
	    y = len(file_magnet)-1
	    ideal_magnet = ''
	    if ('show' in type):
		if (file_seeders[0] > 10) and (file_size[0] < 600) and (not 'sub' in file_titles[0].lower()):
			if (media_name.split()[-2] == 'season'):
				if ' '.join(media_name.split()[-2:]) in file_titles[0]: ideal_magnet = file_magnet[0]
	    elif ('movie' in type):
		if (file_seeders[0] > 100) and (file_size[0] < 3000) and (not 'sub' in file_titles[0].lower()): ideal_magnet = file_magnet[0]
	    if not ideal_magnet:
		    for x in xrange(0, y): 
			if ('show' in type):
				if (file_seeders[y-x] > 10) and (file_size[y-x] < 600) and (not 'sub' in file_titles[y-x].lower()):
					if (media_name.split()[-2] == 'season'):
						if ' '.join(media_name.split()[-2:]) in file_titles[y-x]: ideal_magnet = file_magnet[y-x]
					else: ideal_magnet = file_magnet[y-x]
			elif ('book' in type):
				if (file_seeders[y-x] > 3): ideal_magnet = file_magnet[y-x]
			elif ('song' in type):
				if (file_seeders[y-x] > 3) and (file_size[y-x] < 50): ideal_magnet = file_magnet[y-x]
			elif ('movie' in type):
				if (file_seeders[y-x] > 15) and (file_size[y-x] < 1500) and (not 'sub' in file_titles[y-x].lower()): 
					ideal_magnet = file_magnet[y-x]

	    # Sets the next show in memory
	    if ('show' in type):
		    if ('s0' in original) or ('s1' in original): 
			memory.set('imsAfterShow',original[:-6]+'season '+str(int(original[-5:][:2]))+' episode '+str(int(original[-5:][3:])+1))
			memory.set('imsBeforeShow',original[:-6]+'season '+str(int(original[-5:][:2]))+' episode '+str(int(original[-5:][3:])-1))
		    elif 'episode' in original: 
			memory.set('imsAfterShow',original.split('episode')[0]+'episode '+str(int(original.lower().split('episode')[1].split()[0])+1))
			memory.set('imsBeforeShow',original.split('episode')[0]+'episode '+str(int(original.lower().split('episode')[1].split()[0])-1))
		    elif (media_name[-6] == 's'): 
			memory.set('imsAfterShow',media_name[:-6]+'season '+str(int(media_name[-5:][:2]))+' episode '+str(int(media_name[-5:][3:])+1))
			memory.set('imsBeforeShow',media_name[:-6]+'season '+str(int(media_name[-5:][:2]))+' episode '+str(int(media_name[-5:][3:])-1))

	    memory.set('torrent_size',str(file_size[file_magnet.index(ideal_magnet)]))
	    memory.set('search_title',original)

	    # Not a lot of seeders on the chosen magnet
	    if file_seeders[file_magnet.index(ideal_magnet)] <= 3: memory.set('ttsOverride','Not enough support. Try again at a different time')

	    if ideal_magnet: return ideal_magnet
	    else: return ''
    except:
	return ''

# Init call
def main(request):
    # Local vars
    query = request
    type = query.split()
    cmd_test = [word for word in query.split() if word.lower() in ex_cmds]
    type_test = [word for word in type if word.lower() in formats]
    if cmd_test and type_test:
	    if query.index(cmd_test[0]) > query.index(type_test[0]): type = ' '.join(type_test)
	    else: type = ' '.join(cmd_test)
    elif cmd_test: type = ' '.join(cmd_test)
    elif type_test: type = ' '.join(type_test)
    source = ' '.join(query.split()[1:])
    source = source.split(type.split()[0])[1]
    #source = ' '.join([word for word in source.split() if not word in type.split()])
    command = ''
    if 'NETWORK' in source:
	source = source.replace('NETWORK','').strip().lower()
	type += ' network'
    else: source = source.lower()

    # Removes words not needed
    if source:
	   final = source
	   for x in xrange(0, len(source.split())):
		if source.split()[x] in removewords: final = final.replace(source.split()[x],'',1)
		else: break
	   source = final.strip()
    # Command 'stream the next show'
    if ('next' in type) and ('episode' in source): 
	source = memory.get('imsAfterShow')
	type = 'show'
    elif ('previous' in type) and ('episode' in source): 
	source = memory.get('imsBeforeShow')
	type = 'show'
    # Command latest episode
    # stream the tv show big bang theory latest episode'
    elif ('show' in source) and (('latest' in type) or ('newest' in type) or ('last' in type)):
	source = latest_show(source.split('show')[0])
	type = 'show'
	if not source:
		memory.set('ttsOverride',"I'm sorry, but I don't know what the last episode was")
		sys.exit()
    # Command to show the weather
    elif ('weather' in type):
	weather()
	sys.exit()
    # Command to play description of a show
    elif ('episode' in type) and (('when' in type) or ('where' in type)):
	if 'when' in type: r_type = 'when'
	else: r_type = 'where'
	show = source.split('of')[1].split(r_type)[0].strip()
	test = search_show(source) 
	if test: 
		source = show + " " + test
		type = 'show'
	else:
		memory.set('ttsOverride',"I couldn't find any episode like that")
		sys.exit()
    # Suggest media content
    elif ('suggest' in type):
	genre = re.split(r"(movie|tv show|show)\s*",source)[0].split()[-1]
	type = re.split(r"(movie|tv show|show)\s*",source)[1]
	memory.set('ttsOverride',' - '.join(str(suggest_media(genre,type)).split('|')))
	sys.exit()
    # Command about who played in a movie/show
    # stream who played in rocky horror
    elif (('who' in type) or ('what' in type)) and (('played' in type) or ('starred' in type)) and (not 'movie' in source) and (not 'show' in source):
	test = ', '.join(find_actors(re.split(r"(played in|starred in| movie | show )\s*", source)[-1]))
	sub = test.split(',')[-1]
	memory.set('ttsOverride',test.replace(sub,' and'+sub))
	sys.exit()
    # Commands about movies/shows from actors
    # stream what movies halle barry played in
    elif (('who' in type) or ('what' in type)) and (('play' in type) or ('star' in type)) and (('movie' in source) or ('show' in source)):
	test = ', '.join(suggest_actor_content(' '.join(re.split(r"(showed|show|played|play|starred|star)\s*", source)[0].split()[-2:])))
	sub = test.split(',')[-1]
	memory.set('ttsOverride',test.replace(sub,' and'+sub))
	sys.exit()
    # Command about year of movie/show
    elif ('year' in type):
	test = movie_year(re.split(r"(come out|released)\s*", (re.split(r"(did|was it|was)\s*", source)[2]))[0]).strip()
	test = re.split(r"( movie | show )\s*",test)[-1]
	memory.set('ttsOverride',test)
	sys.exit()
    # Command for the radio
    elif ('radio' in type) or ('news' in type):
	if ('radio' in type): r_type = 'radio'
	else: r_type = 'news'
	test = radioMagnet(source.replace('station',''),r_type)
	if '|||' in test:
		command = 'vlc "%s" --qt-start-minimized' % test.split('|||')[0]
		# Save for later
		memory.set('radiostream_'+'_'.join(test.split('|||')[1].split()),test.split('|||')[0])
	else:
		memory.set('ttsOverride',test)
		sys.exit()

    # Adds the year the movie was made for better accuracy
    if 'movie' in type:
	test_name = check_mname(source)
	test_year = movie_year(source)
	if test_name:
		source = test_name
	if test_year:
		source = ''.join([i for i in source if not i.isdigit()]).strip()
		source += " "+test_year
		source = ' '.join([word for word in source.split() if word.lower() not in stopwords])
    #elif 'show' in type:
	#name = ' '.join(source.split('season')[0].split())
	#test_name = check_mname(name)
	#if test_name: source = source.replace(name,test_name)

    # Builds a command from magnets
    if (not 'youtube' in type) and source:
	    # Resets vars
	    test_magnet = ''
	    '''
	    # Recursive check via requests to get the torrent magnet
	    for x in xrange(0,3):
		if (not 'show' in type) and (not 'network' in type):
			if x == 0: test_magnet = get_magnet_link(source,type,False)
			elif x == 1: test_magnet = get_magnet_link(source,type,True)
			elif x == 2:
				if ('show' in type):
					next_season = str(int(parse_media(source)[-5:][:2])+1)
					test_magnet = get_magnet_link(parse_media(source)[:-6]+'s0'+next_season+'e01',type,False)
			if test_magnet:
				break
	    # Recursive check for the primewire framework stream link
	    else:
	    '''
		
	    if ('movie' in type) or ('show' in type):
			if (not 's0' in source) and (not 's1' in source) and ('show' in type): test = primewire(parse_media(source),type)
			else: test = primewire(source,type)
			if test: command = "vlc %s --fullscreen --no-sub-autodetect-file --sub-track 100  --audio-filter equalizer --no-video-title --sout-all --play-and-exit --aspect-ratio 16:9" % test
			else:
				memory.set('ttsOverride',"I didn't find any results. Too bad for you")
				sys.exit()

	    # Build the command from test_magnet
	    if test_magnet:
		    if ('movie' in type) or ('song' in type) or ('show' in type): command = 'peerflix "'+test_magnet+'" --vlc -- --fullscreen --no-sub-autodetect-file --sub-track 100 --audio-filter equalizer --no-video-title'
		    elif ('book' in type): command = 'cd /root/Scripts/Alicia/misc/books/ && aria2c "'+test_magnet+'" --seed-time=0'
    # Youtube
    else:
	memory.set('ttsOverride','This may take a bit')
	if source.split()[0] == 'next':
		memory.set('mpsyt_count',str(int(memory.get('mpsyt_count'))+1))
		command = "mpsyt set search_music false, set show_video true, set fullscreen 1,/'%s',%s,q" % (source, memory.get('mpsyt_count'))
	else:
		memory.set('mpsyt_count','0')
		command = "mpsyt set search_music false, set show_video true, set fullscreen 1,/'%s',1,q" % source

    # Executes the prebuilt command
    try:
	if command: memory.set('stream_command',command.replace('\n',''))
	else: memory.set('stream_command','nothing')

	'''
	# VLC processing
	if (('movie' in type) or ('show' in type)) and (not 'vlc' in command.split()[0]):
		memory.set('ttsOverride',start_stream[randint(0,3)]+". Please wait")
		# Wait for peerflix starts downloading the file
		timer = 0
		while (os.popen('ps -aux | grep peerflix').read().count('\n') > 1) and (memory.get('ims_percentage') == '0') and (timer < 30):
			timer += 1
			sleep(1)
		if timer == 30:
			os.system('killall vlc >/dev/null 2>&1')
			if (not 's0' in source) and (not 's1' in source): test = primewire(parse_media(source),type)
			else: test = primewire(source,type)
			if test: 
				command = "vlc %s --fullscreen --no-sub-autodetect-file --sub-track 100  --audio-filter equalizer --no-video-title --sout-all --play-and-exit --aspect-ratio 16:9" % test
				subprocess.Popen(command+" >/dev/null 2>&1", shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			else:
				memory.set('ttsOverride',"I didn't find any results. Too bad for you")
				sys.exit()
		elif (os.popen('ps -aux | grep peerflix').read().count('\n') == 1):
			memory.set('ttsOverride','Something went wrong inside me')
			sys.exit()
		elif float(memory.get('torrent_size')) > 6000: memory.set('ttsOverride','It may take a bit to start, but it will be constant after that')
		# Trend analysis to determine how long it will take to download
		timer = 0
		tSize = float(memory.get('torrent_size'))
		tPerc = float(memory.get('ims_percentage'))
		while (timer < 15) and (int(os.popen('ps -aux | grep vlc').read().split('\n')[1].split()[5]) < 100000):
			trendSize[0] = float(memory.get('ims_percentage'))
			for count in xrange(1,len(trendSize)):
				trendSize[15 - count] = trendSize[14 - count]
			timer += 1
			sleep(1)
		if timer == 10:
			df = pd.DataFrame({'time': trendList, 'size': trendSize})
			slope = trendline(df['size'])
			if (tSize * (tPerc * 0.01)) >= 20: estimate_sec = 0
			else:
				try: estimate_sec = (10/(tSize * (slope * 0.01)))*-1
				except: estimate_sec = 0
			if estimate_sec > 180:
				if (not 's0' in source) and (not 's1' in source): test = primewire(parse_media(source),type)
				else: test = primewire(source,type)
				if test: 
					command = "vlc %s --fullscreen --no-sub-autodetect-file --sub-track 100  --audio-filter equalizer --no-video-title --sout-all --play-and-exit --aspect-ratio 16:9" % test
					os.system('killall vlc >/dev/null 2>&1')
					subprocess.Popen(command+" >/dev/null 2>&1", shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					memory.set('ttsOverride',"I didn't find any results. Too bad for you")
					sys.exit()
			else:
				if estimate_sec > 60:
					minutes = round(estimate_sec/60)
					if minutes == 1:
						memory.set('ttsOverride','Your stream will be ready in 1 minute')
					else:
						memory.set('ttsOverride','Your stream will be ready to play, in %s minutes' % minutes)
				elif estimate_sec > 20: memory.set('ttsOverride','Your stream will be ready in less than 1 minute')
				elif estimate_sec > 10: memory.set('ttsOverride','Your stream will play in a few seconds')
	'''
	# Ebook processing
	if 'book' in type:
		# Reset peerflix, since, it doesn't play on vlc to reset
		memory.set('ims_percentage','0')
		# Say book confirmation to tts
		memory.set('ttsOverride',"I've found your book online. Please wait")
		# Wait for the command to stop
		while os.popen('ps -aux | grep aria2c').read().count('\n') > 2: sleep(1)

		# Builds a list of books downloaded, format them & upload them
		test = []
		for x in xrange(0,len(source.split())):
			#if x != len(source.split())-1:
			t_source = ' '.join(source.split()[:len(source.split())-x])
			t_1 = os.popen('find /root/Scripts/Alicia/misc/books/ -iname "*%s*" -type f' % t_source.strip()).read().split('\n')
			t_2 = os.popen('find /root/Scripts/Alicia/misc/books/ -iname "*%s*" -type f' % t_source.strip().replace(' ','_')).read().split('\n')
			if t_1[0] or t_2[0]: break
		if t_1[0]: test = t_1
		elif t_2[0]: test = t_2
		if test:
			books = [s for s in test if ('epub' in s) or ('pdf' in s) or ('mobi' in s)]
			book_title = books[0].split('.')[0].split('/')[-1]
			# Multiple formats for the same book
			if [s for s in books if book_title in s]:
				# Looks for mobi first
				if [s for s in books if 'mobi' in s]: books = [s for s in books if 'mobi' in s]
				# Looks for pdf second
				elif [s for s in books if 'pdf' in s]: books = [s for s in books if 'pdf' in s]
				# Settles for epub
				else: books = [s for s in books if 'epub' in s]
			# Verbose
			if len(books) > 1: memory.set('ttsOverride',"There are a bunch of books in this collection it seems. This process might take a while")
			else: memory.set('ttsOverride',"I'm processing the book now. It shouldn't take long")
			# Process every book in list 'books'
			for x in xrange(0, len(books)):
				os.system('rm /root/Scripts/Alicia/misc/book.mobi >/dev/null 2>&1')
				os.system('ebook-convert "%s" /root/Scripts/Alicia/misc/book.mobi >/dev/null 2>&1' % books[x])
				if os.path.isfile('/root/Scripts/Alicia/misc/book.mobi'):
					os.system('node /root/Scripts/Alicia/casperjs/streamer/sendBookEmail.js >/dev/null 2>&1')
					memory.set('ttsOverride',"%s is now uploaded to your kindle" % books[x].split('.')[0].split('/')[-1])	
					break				
				else: memory.set('ttsOverride',"There seems to be an issue with this particular book. I'm sorry" % str(type))
			else:
				memory.set('ttsOverride',"That's weird. Some kind of error occured.")
			pass
		else:
			memory.set('ttsOverride',"Formatting the book titles failed. Sorry")
	'''
	# Command to monitor for increased lag and disable after x amount of sec
	if ('movie' in type) or ('show' in type) or ('song' in type):
		timer = 0
		# Waits until vlc opens a show from the memory buffer
		while (int(os.popen('ps -aux | grep vlc').read().split('\n')[1].split()[5]) < 100000) and (timer < 45):
			timer += 1
			sleep(1)
		g_cnt = 0
		# While vlc is playing
		while len(os.popen('ps -aux | grep vlc').read().split('\n')) > 3:
			q_cnt = 0
			memory.set('soundOff','False')
			# Wait until the stream stops in vlc 
			while (not 'closed' in os.popen('head -1 /proc/asound/card0/pcm3p/sub0/status').read()):
				sleep(1)
				q_cnt += 1
				# Two minutes without a lag - detach from vlc and quit
				if q_cnt == 120:
					sys.exit()
			l_cnt = 0
			memory.set('soundOff','True')
			# Wait until the stream comes back and adds l_cnt to the global
			while ('closed' in os.popen('head -1 /proc/asound/card0/pcm3p/sub0/status').read()):
				l_cnt += 1
				sleep(1)
			g_cnt += l_cnt
			# Explain and exit
			if g_cnt > 45:
				memory.set('ttsOverride',"I've detected an anomaly in the streaming process. Please try another show, for now. Sorry")
				os.system('killall vlc >/dev/null 2>&1')
				sys.exit()
	'''
    except Exception as e:
	memory.set('ttsOverride',"There seems to be an issue with the %s I found" % str(type))
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno)
        print e
	#print "Error"
        exit()

if __name__ == '__main__':
        while True:
                if memory.get('stream_request'):
                        request = memory.get('stream_request')
                        memory.set('stream_request','')
                        main(request)
                sleep(0.2)

