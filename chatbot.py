
import modoscrape
import modoscrape.chatbot
import threading
import time

channel = '#phyrexianviewbot'
nickname = 'phyrexianviewbot'
server = 'irc.chat.twitch.tv'
port = 6667
bot = modoscrape.chatbot.TestBot(channel, nickname, server, port)
t1 = threading.Thread(target=bot.start)
t1.start()
print "thread", t1


while True:
    time.sleep(5)
    bot.start_vote()
    time.sleep(10)
    votes = bot.end_vote()
    time.sleep(1)

#bot.end()

