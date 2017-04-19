import irc.bot
import irc.strings
import re
import pprint
import operator
import random


class BleepBloop(irc.bot.SingleServerIRCBot):
    def __init__(self):

        self.vote_time = 10

        password = ''
        with open("e:/twitch-token.txt", "r") as f:
            data = f.readlines()
            password = data[0]

        channel = '#phyrexianviewbot'
        nickname = 'phyrexianviewbot'
        server = 'irc.chat.twitch.tv'
        port = 6667

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

        if re.match("^(click|go|F)", text, re.IGNORECASE):
            self.votes[nick] = BleepBloop.normalize_vote(text)


    def write(self, c, msg):
        print msg
        c.privmsg(self.channel, 'MrDestructoid ' +  msg)

    def start_vote(self):
        self.votes = {}
        self.write(self.c, "Vote now for next action now!")

    def end_vote(self):
        self.write(self.c, "results:")
        self.write(self.c, pprint.pformat(self.votes))
        return self.votes

    @staticmethod
    def normalize_vote(str):
        str = str.lower()
        str = re.sub("\s+", " ", str)
        str = re.sub("\s+$", "", str)
        return str

    @staticmethod
    def winning_vote(votes):
        tally = {}

        for k in votes:
            vote = votes[k]
            if tally.has_key(vote):
                tally[vote] += 1
            else:
                tally[vote] = 1

        sorted_tally = sorted(tally.items(), key=operator.itemgetter(1), reverse=True)

        max_votes = sorted_tally[0][1]
        tied_votes = [k for k, v in tally.items() if v == max_votes]
        winner = random.choice(tied_votes)
        pprint.pprint(["votecount", sorted_tally, "ties ?", tied_votes, "winner (random pick)", winner])

        return winner






