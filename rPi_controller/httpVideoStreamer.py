import redis, os
from time import sleep
import subprocess
import requests
import string
from bs4 import BeautifulSoup
from unidecode import unidecode

memory = redis.StrictRedis(host='localhost', port=6379, db=0)

template = '<!DOCTYPE HTML>\n<html>\n<head>\n<title>Streamer</title>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<link href="./../css/bootstrap.css" rel="stylesheet" type="text/css" />\n<link href="./../css/style.css" rel="stylesheet" type="text/css" />\n<script src="./../js/jquery-1.11.1.min.js"></script>\n<script src="./../js/videojs.js"></script>\n<link href="http://fonts.googleapis.com/css?family=Maven+Pro:400,500,700" rel="stylesheet" type="text/css">\n<body>\n<section id="wrapper">\n<div class="videoContainer">\n<video id="myVideo" controls preload="auto" poster="./../images/theater.jpg" width="380" >\n<source src="TEXTTESTDATA" type="video/mp4" />\n<p>Your browser does not support the video tag.</p>\n</video>\n<div class="control">\n<div class="btmControl">\n<div class="btnPlay btn" title="Play/Pause video"><span class="icon-play"></span></div>\n<!--<div class="volume" title="Set volume">\n<span class="volumeBar"></span>\n</div>-->\n<div class="sound sound2 btn" title="Mute/Unmute sound"><span class="icon-sound"></span></div>\n<div class="btnFS btn" title="Switch to full screen"><span class="icon-fullscreen"></span></div>\n</div>\n</div>\n</div>\n</section></body>\n</html>'

n_template = '<!DOCTYPE HTML>\n<html>\n<head>\n<title>Streamer</title>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<link href="./../css/bootstrap.css" rel="stylesheet" type="text/css" />\n<link href="./../css/style.css" rel="stylesheet" type="text/css" />\n<script src="./../js/jquery-1.11.1.min.js"></script>\n<script>\nsetTimeout(function(){window.location.href = "http://stream.now";}, 2500);\n</script>\n<link href="http://fonts.googleapis.com/css?family=Maven+Pro:400,500,700" rel="stylesheet" type="text/css">\n<body onload="setTimeout()">\n<div class="banner" id="home">\n<div class="container">\n<div class="header-top">\n<h2>Nothing found. Sorry.</h2>\n<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />\n</div>\n</div>\n</div></body></html>'

last_command = ''

def getThumb(name):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',}
	URL = 'https://www.bing.com/images/search?q='+'+'.join(name.split())+'+wide+jpeg+poster&go=Search&qs=ds&form=QBIR'
	resp = requests.get(URL,headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	t = soup.findAll("img", {"class": "mimg"},)
	if t:
		for each in t:
			element = unidecode(each)
			height = int(element.split('height="')[1].split('"')[0])
			width = int(element.split('width="')[1].split('"')[0])
			if (width > height) and (not 'data:' in unidecode(each)):
				try: return each['src']
				except: pass
		else: return t[0]['src']
	else: return ''

while True:
	with open('/var/log/apache2/access.log', 'r') as myfile:
		data=myfile.read().replace('\n', '')
	last_command = data.split('?media=')[-1].split()[0].replace('"','').replace("'","").replace('+',' ')
	if memory.get('http_command') != last_command:
		u_template = template
		memory.set('http_command',last_command)
		subprocess.Popen('stream '+last_command+' NETWORK'+" >/dev/null 2>&1", shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		memory.set('network_stream_link','')
		timeout = 0
		while (not memory.get('network_stream_link')) and (timeout < 30):
			sleep(0.5)
			timeout += 1
		os.system('rm /var/www/html/media/* >/dev/null 2>&1')
		if not timeout == 30:
			test_thumb = getThumb(last_command)
			if test_thumb: u_template = u_template.replace('./../images/theater.jpg',test_thumb)
			u_template = u_template.replace('TEXTTESTDATA',memory.get('network_stream_link'))
			with open('/var/www/html/media/'+last_command.replace(' ','-')+'.html', 'w') as myfile:
				myfile.write(u_template)
		else:
			u_template = n_template
			with open('/var/www/html/media/'+last_command.replace(' ','-')+'.html', 'w') as myfile:
				myfile.write(u_template)
	sleep(2)
		



