#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib2

from irc_common import *

# Keeping track of imported functions in a stupidly verbose way
from calc import calculate
from wikipedia import fetch, random_pair, check_chain, extract_article, get_link
from title import extract_url, get_title
from utils import fetch_url
from game import roll_dice, last_roll

# Read line and execute commands
def read_line(line):
    # Variables inside curly braces are optional
    
    # Dirty but better than having "self" all over the damn code
    global logged_in, deposit, scores

    # PING messages don't start with ':'
    if line.startswith(':'):
        ### Parsing ###
        # Complete command (:name!username@host command {args} :args)
        full_command = line.split() # [:name!username@host, command{, args}, :args]

        if len(full_command) < 2:
            return

        # Sender info (:name!username@host)
        sender_info = full_command[0]
        sender_info = sender_info.lstrip(':').split('!') # [name, username@host]
        sender = sender_info[0] # name

        # Message and parameters (command {args} :args)
        message = full_command[1:]
        command = message[0] # command

        ### Numeric replies ###
        # Initial connection
        if not logged_in and (command == '439' or 'NOTICE' in command):
            execute('NICK %s' % nickname)
            execute('USER %s %s %s :%s' % (nickname, nickname, nickname, nickname))
            execute('NS IDENTIFY %s' % password)
            # execute('NS GHOST %s %s' % (nickname, password))
            logged_in = True

        # Start of MOTD
        elif command == '375':
            for channel in channels:
                execute('JOIN %s' % channel)

        # NAMES list
        elif command == '353':
            # message = ['353', bot_nickname, '=', #chan, :nick1, nick2, nick3]
            channel = message[3] # #chan
            message[4] = message[4].lstrip(':') # nick1
            names_list = message[4:] # [nick1, nick2, nick3]

            for name in names_list:
                add_user(channel, name)

        ### Handle common messages ###
        elif command == 'KICK':
            current_channel = full_command[2]
            user = full_command[3]
            # Autojoin
            if user == nickname:
                execute('JOIN %s' % current_channel)
            # User KICKs
            else:
                remove_user(user, current_channel)
            deposit += 10

        # User JOINs
        elif command == 'JOIN' and sender != nickname:
            # message = ['JOIN', {':' + }#chan]
            current_channel = message[1].lstrip(':')
            add_user(current_channel, sender)

        # User PARTs
        elif command == 'PART':
            # message = ['PART', #chan, ':' + reason]
            current_channel = message[1]
            remove_user(current_channel, sender)

        # User QUITs
        elif command == 'QUIT':
            for channel in channels:
                remove_user(channel, sender)

        # User commands
        elif command == 'PRIVMSG':
            # message = ['PRIVMSG', #chan, ':' + word word word]
            message[2] = message[2].lstrip(':')
            
            current_channel = message[1]
            said = ' '.join(message[2:])
            params = message[3:] # List of parameters (split by spaces)
            search_term = '+'.join(params)   
                
            # Get title from web pages
            if 'http://' in said:
                url = extract_url(said)
                title = get_title(url)
                if title:
                    say(current_channel, 'Title: %s' % title)

            # Get link to Wikipedia article
            if '[[' in said:
                article = extract_article(said)
                link = get_link(article)
                if link:
                    say(current_channel, link)
                
            ## IRC commands ##
            # Commands with parameters
            if len(params) > 0:
                # Google
                if said.find('@g') == 0:
                    say(current_channel, 'https://www.google.com/search?q=%s' % search_term) 

                # Wolfram Alpha
                elif said.find('@wa') == 0:
                    say(current_channel, 'http://www.wolframalpha.com/input/?i=%s' % search_term) 

                # DuckDuckGo
                elif said.find('@ddg') == 0:
                    say(current_channel, 'http://duckduckgo.com/?q=%s' % search_term) 

                # DRAE
                elif said.find('@drae') == 0:
                    say(current_channel, 'http://lema.rae.es/drae/?val=%s' % search_term) 

                # DPD
                elif said.find('@dpd') == 0:
                    say(current_channel, 'http://lema.rae.es/dpd/?key=%s' % search_term)

                # Jisho kanji lookup
                elif said.find('@kan') == 0:
                    escaped_term = urllib2.quote(search_term)
                    say(current_channel, 'http://jisho.org/kanji/details/%s' % escaped_term)

                # EN > JP
                elif said.find('@ei') == 0:
                    say(current_channel, 'http://jisho.org/words?jap=&eng=%s&dict=edict' % search_term)

                # JP > EN
                elif said.find('@ni') == 0:
                    escaped_term = urllib2.quote(search_term)
                    say(current_channel, 'http://jisho.org/words?jap=%s&eng=&dict=edict' % escaped_term)

                # EN > ES
                elif said.find('@en') == 0:
                    say(current_channel, 'http://www.wordreference.com/es/translation.asp?tranword=%s' % search_term)
                
                # ES > EN
                elif said.find('@es') == 0:
                    say(current_channel, 'http://www.wordreference.com/es/en/translation.asp?spen=%s' % search_term)
                
                # Unit converter
                elif said.find('@conv') == 0:
                    if 'to' not in params:
                        return
                    index = params.index('to')
                    amount = params[0]
                    unit_from = params[1:index]
                    unit_from = urllib2.quote(' '.join(unit_from))
                    # 'to' == params[index]
                    unit_to = params[index + 1:]
                    unit_to = urllib2.quote(' '.join(unit_to))
                                        
                    conversion_url = 'http://www.google.com/ig/calculator?hl=en&q=' 

                    conversion = fetch_url(conversion_url + amount + unit_from + '=?' + unit_to).read()
                    parsed_conversion = conversion.split('"')

                    # Check for errors
                    if len(parsed_conversion[5]) == 0:
                        unit_result = urllib2.unquote(unit_to)
                        say(current_channel, '%s %s' % (parsed_conversion[3].split()[0], unit_result))
                
                # Linkrace module
                elif said.find('@link') == 0:
                    linkcommand = params[0]
                    
                    # Get race links
                    if linkcommand == 'get':
                        url = 'http://es.wikipedia.org/wiki/%s'
                        start, end = random_pair()
                        starturl = url % urllib2.quote(start)
                        endurl = url % urllib2.quote(end)
                        say(current_channel, 'Start article is %s' % starturl)
                        say(current_channel, 'Goal article is %s' % endurl)
                    
                    # Check if chain is valid
                    if linkcommand == 'check':
                        chain = ' '.join(params[1:])
                        broken_links = check_chain(chain)
                        if not broken_links:
                            say(current_channel, 'The chain is valid.')
                        else:
                            error_list = ' | '.join(broken_links)
                            say(current_channel, error_list)
                            say(current_channel, 'The chain is not valid.')

                # Calculator           
                elif said.find('@calc') == 0:
                    expression = ''.join(params)
                    result = str(calculate(expression))
                    say(current_channel, result)

                # Wikipedia fetch
                elif said.find('@fetch') == 0:
                    article_name = ' '.join(params)
                    extract = fetch(article_name)
                    say(current_channel, extract)

                # Bet 
                elif said.find('@bet') == 0:
                    wager = int(params[0])
                    if wager > deposit:
                        say(current_channel, 'Deposit is %s, cannot bet %s' % (deposit, wager))
                        return

                    roll = roll_dice(sender)
                    if roll == 1 or roll == 6:
                        say(current_channel, 'Last roll was' % last)
                        return

                    if win:
                        say(current_channel, '%s: %s, +%sC' % (sender, roll, wager))
                        scores[sender][0] += wager
                        deposit -= wager
                    else:
                        say(current_channel, '%s: %s, -%sC' % (sender, roll, wager))
                        scores[sender][0] -= wager
                        deposit += wager

            # Commands without parameters
            else:
                # Roll
                if said.find('@roll') == 0:
                    roll = roll_dice(sender)
                    if roll == 1:
                        deposit += 1
                        scores[sender][0] -= 1
                        balance = scores[sender][0]
                        say(current_channel, '%s: rolled %s, -1C, balance: %sC' % (sender, roll, balance))
                    elif roll == 6 and deposit > 0:
                        deposit -= 1
                        scores[sender][0] += 1
                        balance = scores[sender][0]
                        say(current_channel, '%s: rolled %s, +1C, balance: %sC' % (sender, roll, balance))
                    else:
                        say(current_channel, '%s: rolled %s' % (sender, roll))
                            
                # Check deposit
                elif said.find('@deposit') == 0:
                    say(current_channel, 'Deposit: %s' % deposit)

                elif said.find('@last') == 0:
                    say(current_channel, '%s: Last roll: %s' % (sender, last_roll(sender)))

            ## Owner commands ##
            if sender == owner:
                # Disconnect
                if said == '.quit':
                    execute('QUIT')
                    save_scores()
                    sys.exit()

                # Print userlist
                elif said.find('.users') == 0:
                    say(current_channel, str(users))
                
                # Print scores
                elif said.find('.scores') == 0:
                    say(current_channel, str(scores))

                # Bot joins
                elif said.find('.join') == 0:
                    channel = said.split()[1]
                    execute('JOIN %s' % channel)

                # Bot parts
                elif said.find('.part') == 0:
                    execute('PART %s' % current_channel)
                    del users[current_channel]

                # Bot kicks
                elif said.find('.kick') == 0:
                    user = said.split()[1]
                    bot_kick(current_channel, user)

    # PING messages don't start with ':'
    else:
        # Pong
        if 'PING' in line:
            execute('PONG %s' % line.split()[1])

# Main loop
while 1:
    data = irc.recv(8192)
    for line in data.split('\r\n'):
        if len(line) > 0:
            print line
            try:
                read_line(line)
            except Exception as derp: 
                print derp
