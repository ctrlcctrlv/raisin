 # -*- coding: utf8 -*-

import json
import urllib2
import re

from utils import fetch_url

### === Linkrace === ###

# Checks if end_article is in the link list at url and returns a result
def find_article(url, end_article):
    json_file = fetch_url(url)
    link_dictionary = json.load(json_file)
    
    # Handle the varying pageid key in the JSON file provided by MediaWiki
    pageid = list(link_dictionary['query']['pages'])[0]
    # Page does not exist
    if pageid == '-1':
        return False

    article_entry = {'ns': 0, 'title': end_article}
    if article_entry in link_dictionary['query']['pages'][pageid]['links']:
        return True

    # Continue if link list is not complete yet
    if 'query-continue' in list(link_dictionary):
        continue_string = urllib2.quote(link_dictionary['query-continue']['links']['plcontinue'])
        ''' Endless appending of plcontinues, can be improved '''
        new_url = url + '&plcontinue=' + continue_string
        return find_article(new_url, end_article)
    else:
        return False

# Check if end_article can be reached from start_article only by clicking links
def reachable(start_article, end_article):
    # JSON file with 500 links at most, namespace 0
    host = 'http://es.wikipedia.org/w/api.php'
    parameters = '?format=json&action=query&prop=links&pllimit=500&plnamespace=0&titles=' 
    initial_url = host + parameters + urllib2.quote(start_article)
    return find_article(initial_url, end_article)

# Check if link chain is valid and show wrong paths
def check_chain(chain):
    chain = [article_name.strip() for article_name in chain.split('>')]

    # Check link chain
    broken = []
    for i in range(0, len(chain) - 1):
        if not reachable(chain[i], chain[i + 1]):
            broken.append('%s /> %s' % (chain[i], chain[i + 1]))
    return broken



### === Fetch === ###

# Show first three sentences of an article
def fetch(article_name):
    host = 'http://es.wikipedia.org/w/api.php?'
    parameters = 'format=json&action=query&prop=extracts&exsentences=3&explaintext=true&titles='
    url = host + parameters + urllib2.quote(article_name)

    json_file = fetch_url(url)
    page_dictionary = json.load(json_file)
    
    # Handle the varying pageid key in the JSON file provided by MediaWiki
    pageid = list(page_dictionary['query']['pages'])[0]
    # Page does not exist
    if pageid == '-1':
        return "The article %s doesn't exist." % (article_name)

    extract = page_dictionary['query']['pages'][pageid]['extract']
    return extract.encode('utf-8')

# Returns title of random article
def random_pair():
    host = 'http://es.wikipedia.org/w/api.php?'
    parameters = 'format=json&action=query&list=random&rnnamespace=0&rnlimit=2'
    url = host + parameters

    json_file = fetch_url(url)
    page_dictionary = json.load(json_file)
    
    return page_dictionary['query']['random'][0]['title'].encode('utf-8'), page_dictionary['query']['random'][1]['title'].encode('utf-8') 


### === Misc === ###
# Handle wiki style links
article_regex = re.compile('\[\[(.*)\]\]')

def extract_article(message):
    list = message.split()
    for word in list:
        match = article_regex.findall(word) # why
        if match:
            return match[0] # double why

# Check if article is a valid link
# TODO: Broken interwikis
def get_link(article):
    host = 'http://es.wikipedia.org/w/api.php?'
    parameters = 'format=json&action=query&prop=info&titles='
    url = host + parameters + article
    json_file = fetch_url(url)
    link_dictionary = json.load(json_file)
    

    # Get page ID
    pageid = list(link_dictionary['query']['pages'])[0]
    # Page doesn't exist if ID is -1
    if pageid == '-1':
        return
    
    return 'http://es.wikipedia.org/wiki/%s' % article
