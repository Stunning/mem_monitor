#!/usr/bin/env python

import sys
import re
import smtplib
from email.mime.text import MIMEText
from socket import gethostname

warn_ratio = float(sys.argv[1])
email_to = sys.argv[2:]

once_filename = "/tmp/mem_monitor-once.json"

def check():
	pattern = re.compile("""privvmpages""" + 
		"""\s+(?P<held>\d+)""" +
		"""\s+(?P<maxheld>\d+)""" +
		"""\s+(?P<barrier>\d+)""" +
		"""\s+(?P<limit>\d+)""" +
		"""\s+(?P<failcnt>\d+)""")
	with open("/proc/user_beancounters", "rb") as data:
		match = pattern.search(data.read())
		p = dict((k, int(v)) for k, v in match.groupdict().items())
		ratio = p["maxheld"] / float(p["limit"])
		if p["failcnt"]:
			alert("fail", "Memory limit breached")
		elif ratio >= warn_ratio:
			alert("warn", "Memory %.0f%% full" % (ratio*100))
		elif p["maxheld"] >= p["barrier"]:
			alert("warn", "memory barier brached")
		else:
			alert("ok")
	
def alert(type, message=None):
	try:
		with open(once_filename, "rb") as once_file:
			once = once_file.read()
	except:
		once = "ok"
	if type == once:
		return
	
	if type in ["fail", "warn"]:
		email(message)
		
	with open(once_filename, "wb") as once_file:
		once_file.write(type)
	
def email(message):
	msg = MIMEText("\n".join([
		message,
		"",
		"Host: " + gethostname()]))
	email_from = "root@" + gethostname()
	msg['Subject'] = "STUNNIMP: " + message
	msg['From'] = email_from
	msg['To'] = ', '.join(email_to)
	
	s = smtplib.SMTP('localhost')
	s.sendmail(email_from, email_to, msg.as_string())
	s.quit()


check()
