### Common IRC functions and internal data
import socket
import ssl

from config import *

# Connect using SSL
port = 6697
irc_unencrypted = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc = ssl.wrap_socket(irc_unencrypted)
irc.connect((network, port))
logged_in = False

# Users and channels
# users['channel'] = [users]
users = {}

# Game scores
# wallet['user'] = coins
wallet = {}

# Linkrace scores
# race['user'] = score
races = {}

# Game deposit
deposit = 50


# Send command to irc socket
def execute(command):
    irc.send(command + '\r\n')

# Send message to channel
def say(channel, message):
    execute('PRIVMSG %s :%s' % (channel, message))

# Add user to user dictionary
def add_user(channel, name):
    global wallet, races

    # Check if username has leading symbols (@, +, etc) and remove them
    if not name[0].isalnum():
        name = name[1:]
    if channel in users:
        users[channel].add(name)
    # If it doesn't exist, create a new entry with the list [channel]
    else:
        users[channel] = set([name])

    # Add user to scores
    if name not in wallet:
        wallet[name] = 5

    if name not in races:
        races[name] = 0

# Remove user from users dictionary
def remove_user(channel, name):
    if channel in users:
        users[channel].remove(name)

# Kick user from channel
def bot_kick(channel, user, reason):
    execute('KICK %s %s :%s' % (channel, user, reason))
    remove_user(channel, user)
    deposit += 10

# Load previous scores from file
def load_scores():
    global deposit

    scores_file = ''
    try: 
        scores_file = open('.scores', 'r')
    except IOError:
        print 'Could not load scores file.'
        sys.exit()

    deposit = int(scores_file.readline())
    
    line = ' '
    while 1:
        line = scores_file.readline()
        if line == '':
            break

        user = line.split()[0]
        coins = int(line.split()[1])
        linkrace_score = int(line.split()[2])

        wallet[user] = coins
        races[user] = linkrace_score

    scores_file.close()

# Save current scores to file
def save_scores():
    global deposit, scores
    
    scores_file = ''

    try: 
        scores_file = open('.scores', 'w')
    except IOError:
        print 'Could not write scores file. Current scores were:'
        print 'Deposit: %s' % deposit
        for user, score_list in scores.items():
            print "%s: %s coins, %s" % (user, score_list[0], score_list[1])
        sys.exit()

    scores_file.write(str(deposit) + '\n')

    # interleaved_list = ('user', coins, linkrace_score)
    for leaf in zip(wallet.keys(), wallet.values(), races.values()):
        line = "%s %s %s\n" % (leaf[0], leaf[1], leaf[2])
        scores_file.write(line)

    scores_file.close()
