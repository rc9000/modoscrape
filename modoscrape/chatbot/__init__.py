import irc.bot
import irc.strings
import re
import pprint
import operator
import random
import time
import math


class BleepBloop(irc.bot.SingleServerIRCBot):
    def __init__(self):

        self.STATE_AWAIT_STREAM_DELAY = 1
        self.STATE_VOTING_ACTIVE = 2
        self.STATE_RESULT_READY = 3

        self.voting_active_time = 5
        self.voting_await_stream_delay_time = 2
        self.viewer_count = 1
        self.votes_needed_to_progress = 1

        #self.bot_emote = 'tsmtgTKS'
        self.bot_emote = 'MrDestructoid'


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

        self.state = self.STATE_AWAIT_STREAM_DELAY
        self.state_entered = int(time.time())

    def state_check(self, viewer_count):
        now = int(time.time())

        votes_needed_to_progress = max(int(math.ceil(viewer_count / 3)), 1)
        self.votes_needed_to_progress = votes_needed_to_progress

        #print "vntp =", votes_needed_to_progress

        if self.state == self.STATE_AWAIT_STREAM_DELAY:
            if now > self.state_entered + self.voting_await_stream_delay_time:
                print "transition STATE_AWAIT_STREAM_DELAY > STATE_VOTING_ACTIVE";
                self.state_entered = now
                self.state = self.STATE_VOTING_ACTIVE
                self.start_vote()
            else:
                print "state STATE_AWAIT_STREAM_DELAY"

        elif self.state == self.STATE_VOTING_ACTIVE:
            if (now > self.state_entered + self.voting_active_time) and len(self.votes) >= 1:
                print "transition STATE_VOTING_ACTIVE > STATE_RESULT_READY (vote time elapsed)"
                self.state_entered = now
                self.state = self.STATE_RESULT_READY
            elif len(self.votes) >= votes_needed_to_progress:
                print "transition STATE_VOTING_ACTIVE > STATE_RESULT_READY (enough votes)"
                self.state_entered = now
                self.state = self.STATE_RESULT_READY
            elif (now > self.state_entered + self.voting_active_time) and len(self.votes) == 0:
                print "state STATE_VOTING_ACTIVE elapsed but no votes yet, await more"
            else:
                print "state STATE_VOTING_ACTIVE still in progress"

        elif self.state == self.STATE_RESULT_READY:
            print "state STATE_RESULT_READY, need to call end_vote to collect input"

        return self.state


    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.c = c
        c.cap('LS')
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('END')

    def on_join(self, c, e):
       pprint.pprint(["join", c, e])

    def on_names(self, c, e):
       pprint.pprint(["names", c, e])

    def on_part(self, c, e):
       pprint.pprint(["part", c, e])

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

        #viewers = c.names()
        #pprint.pprint(['v_on_this_pub', viewers])

        if re.match("^" + self.bot_emote, text):
            # never respond to bot messages to prevent loops
            return

        if re.match("^echo", text):
            self.write(c, nick + ": screw you Kappa (for saying " + text + ")")

        if re.match("^(click |go |f\d+|pass)", text, re.IGNORECASE):
            self.votes[nick] = BleepBloop.normalize_vote(text)


    def write(self, c, msg):
        print msg
        c.privmsg(self.channel, self.bot_emote + ' ' +  msg)

    def start_vote(self):
        # FIXME: update timestamp with start of vote
        self.votes = {}
        self.write(self.c, "Vote for next action now! "
                           "Progressing after {} seconds or {} votes."
                   .format(self.voting_active_time, self.votes_needed_to_progress))

    def end_vote(self):
        winner, sorted_tally = BleepBloop.winning_vote(self.votes)
        self.write(self.c, "results:")
        self.write(self.c, pprint.pformat(sorted_tally))
        self.write(self.c, "winner chosen: " + winner)
        self.state_entered = int(time.time())
        self.state = self.STATE_AWAIT_STREAM_DELAY
        print "transition STATE_RESULT_READY > STATE_AWAIT_STREAM_DELAY"
        return winner, sorted_tally

    @staticmethod
    def normalize_vote(str):
        str = str.lower()
        str = re.sub("\s+", " ", str)
        str = re.sub("\s+$", "", str)

        # capitalize cursor directions
        for ch in ['u', 'r', 'd', 'l']:
            m = re.search("(.*) (" + ch + ")(\d+)", str)
            if m:
                cmd = m.group(1)
                direction = m.group(2)
                index = m.group(3)
                direction = direction.upper()
                str = cmd + " " + direction + "" + index

        mx = re.search("(.*) x$", str)
        if mx:
            str = mx.group(1) + " X"

        fm = re.search("^f(\d)$", str)
        if fm:
            fnumber = fm.group(1)
            return 'F'+fnumber

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

        return winner, sorted_tally






