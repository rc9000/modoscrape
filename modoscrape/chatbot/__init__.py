"""
mostly copy/pasted from TestBot in the irc package
"""

import irc.bot
import irc.strings
import re
import pprint


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):

        self.vote_time = 10

        password = 'xxxxxx'
        with open("e:/twitch-token.txt", "r") as f:
            data = f.readlines()
            password = data[0]

        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname)
        self.channel = channel
        self.votes = {}

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.c = c

    def end(self):
        print "end", self
        self.disconnect()
        print "disco", self
        self.die()
        print "die", self

    def on_pubmsg(self, c, e):
        print "e", e
        text = e.arguments[0]
        nick = e.source.nick

        if re.match("^MrDestructiod", text):
            # never respond to bot messages to prevent loops
            # ignore nick for that even
            return

        if re.match("^echo", text):
            self.write(c, nick + ": screw you Kappa (for saying " + text + ")")

        if re.match("^(click|go|F)", text):
            self.votes[nick] = text


    def write(self, c, msg):
        print msg
        c.privmsg(self.channel, 'MrDestructoid ' +  msg)

    def start_vote(self):
        self.votes = {}
        self.write(self.c, "vote now for next action")

    def end_vote(self):
        self.write(self.c, "results:")
        self.write(self.c, pprint.pformat(self.votes))
        return self.votes








#
# def main():
#
#     channel = '#zeroxtwoa'
#     nickname = 'zeroxtwoa'
#     server = 'irc.chat.twitch.tv'
#     port = 6667
#     bot = TestBot(channel, nickname, server, port)
#     bot.start()
#
# if __name__ == "__main__":
#     main()
#
