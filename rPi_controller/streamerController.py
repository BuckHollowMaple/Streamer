import speech_recognition
from time import sleep
import redis
import os
import RPi.GPIO as GPIO
import subprocess
from datetime import datetime
from datetime import timedelta
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)

memory = redis.StrictRedis(host='localhost', port=6379, db=0)

last_time = datetime.now()
formats = ['movie','show','song','book','youtube','episode','year','radio']

r = speech_recognition.Recognizer()
m = speech_recognition.Microphone(sample_rate = 48000)
with m as source:
   r.adjust_for_ambient_noise(source)

volume = 80
last_position = 0
visible = False
os.popen('amixer set PCM 80% >/dev/null')
os.popen('amixer -c 1 set Mic 30% >/dev/null')

while True:
        i=GPIO.input(11)
        if (i==1) or (last_time > datetime.now()):
		print "\nMotion detected"
		if i == 1: last_time = datetime.now() + timedelta(seconds = 5)
		with m as source:
		    audio = r.listen(source)
		    print "New Audio"
		try:
		    text = r.recognize_google(audio).lower().replace('dream','stream').replace('scream','stream')
		    if text:
			    print "Said: " + text
			    if ('turn on' in text) or ('tv on' in text):
				os.system('echo "on 0" | cec-client -s -d 1')
				visible = True
				sleep(7)
				memory.set('ttsOverride','Hello')
			    elif ('turn off' in text) or ('tv off' in text):
				memory.set('ttsOverride','Sure thing')
				sleep(3)
				os.system('echo "standby 0" | cec-client -s -d 1')
				visible = False
			    elif ('volume to' in text):
				try: num = int(text.split('volume to')[1].split()[0])
				except: num = 0
				if num != 0:
					volume = num
					os.popen('amixer set PCM %s% >/dev/null' % str(volume))
				memory.set('ttsOverride','Done')
			    elif ('volume up' in text):
				os.popen('amixer set PCM %s% >/dev/null' % str(volume+10))
				volume += 10
				memory.set('ttsOverride','Done')
			    elif ('volume down' in text):
				os.popen('amixer set PCM %s% >/dev/null' % str(volume-10))
				volume += 11
				memory.set('ttsOverride','Done')
			    elif ('pause' in text) and ('stream' in text):
				test = os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh status').read().split('Paused: ')[1].split('\n')[0]
				if test == 'false': 
					os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh pause')
					memory.set('ttsOverride','Your media is now paused')
				elif test == 'true': memory.set('ttsOverride','Your media is already paused')
			    elif ('play' in text) and ('stream' in text):
				test = os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh status').read().split('Paused: ')[1].split('\n')[0]
				if test == 'true': 
					os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh pause')
					memory.set('ttsOverride','Playing now')
				elif test == 'false':
					memory.set('ttsOverride','Your media is already playing')
			    elif ('stop' in text) and ('stream' in text):
				memory.set('ttsOverride',"Stopping now")
				memory.set('last_show_position',os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh status').read().split('Position: ')[1].split('\n')[0])
				os.system('killall omxplayer')
				os.system('killall omxplayer.bin')
				os.system('killall stream')
				os.system('killall mpsyt')
			    elif ('resume' in text) and ('stream' in text):
				memory.set('ttsOverride',"I'm trying to resume now")
				subprocess.Popen(memory.get('last_show_command'), shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
				sleep(15)
				os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh setposition '+memory.get('last_show_position'))
		            elif ('stream' in text) and (not 'help' in text):
				if not visible:
				        os.system('echo "on 0" | cec-client -s -d 1')
					visible = True
				if [word for word in text.split() if word.lower() in formats]:
					os.system('killall stream')
				        memory.set('ttsOverride','Okay')
					subprocess.Popen('stream '+text.split('stream')[1].strip(), shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					memory.set('ttsOverride',"Please specify what type of media you're asking for")
		            elif ('stream' in text) and ('help' in text):
				if not visible:
		                	os.system('echo "on 0" | cec-client -s -d 1')
					visible = True
		                memory.set('ttsOverride',"I can do movies, television shows, radio stations and books to your devices. Start by saying s t r e a m such and such movie, episode or what have you. Try to be concise.")
		                sleep(10)
		                os.system('echo "standby 0" | cec-client -s -d 1')
				visible = False
		            else:
		                pass
		except speech_recognition.UnknownValueError:
		    #if visible: memory.set('ttsOverride',"Please repeat that")
		    #else: pass
		    pass
		except speech_recognition.RequestError as e:
		    reload(speech_recognition)
		    r = speech_recognition.Recognizer()
		    m = speech_recognition.Microphone(sample_rate = 48000)
		    with m as source:
		       r.adjust_for_ambient_noise(source)
		    pass
		except:
			pass

	# Test and save for variables
	if len(os.popen('ps -aux | grep omxplayer.bin').read().split('\n')) > 3:
		last_position = int(os.popen('/root/Scripts/Alicia/HAL/dbuscontrol.sh status').read().split('Position: ')[1].split('\n')[0])
	elif last_position != 0:
		memory.set('last_show_position',last_position)
		last_position = 0

	sleep(1)
