# coding: utf-8

#
# Holy mother of African American individuals
#

import socket
import sys
import re
import htmlentitydefs

from urlparse import urlparse

# Match URL
match_url = re.compile(
	r'^https?://'  # http:// or https://
	r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # Domain
	r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # IP
	r'(?::\d+)?'  # Port
	r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	
# Get title with regex
title_regex = re.compile('<title>(.*?)</title>', re.IGNORECASE)

# Check for location headers in HTTP response
redirection_regex = re.compile('Location:\s(.*)', re.IGNORECASE)

# Get valid URL from string
def extract_url(message):
	list = message.split()
	for word in list:
		result = match_url.search(word)
		if result:
			return result.group(0)

# Unescape HTML entities from text
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text.encode('utf-8') # leave as is
    return re.sub("&#?\w+;", fixup, text)

# Validates URL, stolen from Django
def is_valid_url(url):
    return url is not None and match_url.search(url)

# Return decimal value of ip
def decimal(ip):
	strings = ip.split('.')
	list = [int(string) for string in strings]
	return (list[0] * 256**3) + (list[1] * 256**2) + (list[2] * 256) + list[3]

# Returns True if IP is private or loopback
def is_not_public(ip):
	# Precomputed values for optimiliazations, equivalent to decimal(precomputed)
	# 10.0.0.0 - 10.255.255.255
	class_a = 167772160 < decimal(ip) < 184549375
	# 172.16.0.0 - 172.31.255.255
	class_b = 2886729728 < decimal(ip) < 2887778303
	# 192.168.0.0 - 192.168.255.255
	class_c = 3232235520 < decimal(ip) < 3232301055
	# 127.0.0.0 - 127.255.255.255 
	loopback = 2130706432 < decimal(ip) < 2147483647
	return class_a or class_b or class_c or loopback

# Get title of page at url
def get_title(url):
	if not is_valid_url(url):
		return

	parsed_url = urlparse(url)
	host = parsed_url.netloc
	path = parsed_url.path
	if path == '':
		path = '/'
	port = 80

	ip = ''
	web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		ip = socket.gethostbyname(host)
		web.connect((host, port))
	except Exception:
		return
	
	if is_not_public(ip):
		return
	
	web.send('GET %s HTTP/1.1\n' % path)
	web.send('Host: %s\n' % host)
	web.send('User-Agent: raisin IRC bot/0.1\n')
	web.send('\n')
	
	title = ''	
	done = False
	while not done:
		data = web.recv(2048)
		for line in data.split('\r\n'):
			if len(line) > 0:
				redirection_match = redirection_regex.search(line)
				if redirection_match:
					new_url = redirection_match.group(1)
					return get_title(new_url)

				title_match = title_regex.search(line)
				if title_match:
					web.shutdown(socket.SHUT_RDWR)
					web.close()
					title = title_match.group(1)
					done = True
	
	return unescape(title)
