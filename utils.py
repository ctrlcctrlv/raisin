# -*- coding: utf-8 -*-

import urllib2

def fetch_url(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Raisin IRC bot/0.1')
    socket = urllib2.urlopen(request, None, 5)
    return socket
