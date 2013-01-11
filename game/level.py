from collections import OrderedDict

import pygame as pg

from conf import conf
from random import randint, choice, gammavariate


class Connection (object):
    """A connection between two people.

    CONSTRUCTOR

Connection(level, people, methods)

level: the current Level.
people: list of people to connect.
methods: list of methods (identifiers) this connection can use.

    METHODS

other
send
cancel
update
draw

    ATTRIBUTES

level, people: as given.
methods: {method: allowed} OrderedDict for each available method, fastest
         first.
dist: distance between the people, in pixels.
sending: the target person if currently sending a message, else None.
sent: whether the message has finished sending.
    [if sending:]
progress: sending progress, from 0 to 1.
current_method: the method currently being used to send a message (None if
                none available).

"""

    def __init__ (self, level, people, methods):
        self.level = level
        self.people = people
        speed = conf.METHOD_SPEED
        methods = reversed(sorted((speed[m], m) for m in methods))
        self.methods = OrderedDict((m, True) for s, m in methods)
        self.dist = people[0].dist(people[1]) - 2 * conf.PERSON_ICON_RADIUS
        self.sending = False
        self.sent = False

    def other (self, person = None):
        """Get the person on the other end."""
        if person is None:
            person = self.sending
        return self.people[self.people[0] is person]

    def disable_method (self, method):
        self.methods[method] = False
        if self.sending and method == self.current_method:
            # was using this method: switch to another
            self.send()

    def enable_method (self, method):
        self.methods[method] = True
        if self.sending:
            speed = conf.METHOD_SPEED
            dist_left = (1 - self.progress) * self.dist
            t_left = dist_left / speed[self.current_method]
            if self.dist / speed[method] < dist_left:
                # switching to this method will be quicker
                self.send()

    def send (self, sender = None):
        """Send a message from the given person.


Returns whether any methods are available.

"""
        resend = sender is None
        if resend:
            # re-send in same direction
            sender = self.sending
        if not self.sent:
            self.sending = sender
            self.progress = 0
            # use fastest available method
            for m, allowed in self.methods.iteritems():
                if allowed:
                    self.current_method = m
                    return True
            # no available methods
            self.current_method = None
            # if resending, this is an internal call, so let person know we've
            # stopped sending
            if resend:
                sender.disabled(self)
            return False

    def cancel (self):
        """Cancel sending."""
        self.sending = False
        del self.current_method, self.progress

    def update (self):
        if self.sending:
            self.progress += conf.METHOD_SPEED[self.current_method] * \
                             conf.METHOD_SPEED_MULTIPLIER
            if self.progress >= 1:
                # finished sending
                self.sending.finished()
                self.other().recieve()
                self.sent = True
                self.cancel()

    def draw (self, screen):
        return


class Person (object):
    def __init__ (self, level, pos):
        self.level = level
        self.pos = pos
        self.cons = []
        self.knows = False
        self.sending = False

    def __str__ (self):
        return str(self.level.people.index(self))

    __repr__ = __str__

    def dist (self, *args):
        """Get the distance to another person.

dist(x, y) -> distance
dist(person) -> distance

"""
        x, y = self.pos
        if len(args) == 2:
            ox, oy = args
        else:
            ox, oy = args[0].pos
        return ((ox - x) * (ox - x) + (oy - y) * (oy - y)) ** .5

    def recieve (self):
        """Recieve the message."""
        if not self.knows:
            print self, 'knows'
            self.knows = True

    def send (self):
        """Send the message."""
        # find people we're connected to who don't know
        targets = []
        for c in self.cons:
            if not c.other(self).knows:
                targets.append(c)
        if targets:
            for c in targets:
                # try to send
                if c.send(self):
                    print self, '->', c.other()
                    self.sending = True
                    return
            # no connections remain
            self.sending = False
        else:
            # everyone knows: we have nothing to do, ever
            self.sending = None

    def disabled (self, con):
        """Tell the person sending cannot continue."""
        con.cancel()
        self.send()

    def finished (self):
        """Tell the person sending has finished."""
        self.sending = False

    def update (self):
        if self.knows and self.sending is False:
            self.send()

    def draw (self, screen):
        pg.draw.circle(screen, (200, 200, 200), self.pos,
                       conf.PERSON_ICON_RADIUS)


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        self.init()

    def init (self):
        # generate people
        self.people = ps = []
        b = conf.MAP_BORDER
        x0, y0, w, h = conf.MAP_RECT
        x1 = x0 + w - b
        y1 = y0 + h - b
        x0 += b
        y0 += b
        nearest = 2 * conf.PERSON_ICON_RADIUS + conf.PERSON_NEAREST
        n = conf.NUM_PEOPLE
        for i in range(n):
            while True:
                x, y = randint(x0, x1), randint(y0, y1)
                for p in ps:
                    if p.dist(x, y) < nearest:
                        break
                else:
                    ps.append(Person(self, (x, y)))
                    break
        # generate connections
        self.cons = []
        # TODO
        # give everyone a random number of connections biased towards people near them (use util.weighted_rand) to start with
        # then group everyone who's connected into sets
        # and while there's more than one set, take two sets and join them by connecting the two nearest people in either
        #n_cons = conf.CONS_PER_PERSON
        #this_cons = max(1, min(n, gammavariate(*n_cons)))
        for i1, i2 in ((0, 1), (0, 2), (1, 3)):
            c = Connection(self, (ps[i1], ps[i2]), ('in-person',)) ##
            ps[i1].cons.append(c) ##
            ps[i2].cons.append(c)
            self.cons.append(c) ##
        ps[0].recieve() ##
        # let someone know
        #choice(ps).recieve()
        # reset flags
        self.dirty = True
        self.paused = False

    def update (self):
        if self.paused:
            return
        for p in self.people:
            p.update()
        for c in self.cons:
            c.update()

    def draw (self, screen):
        if self.dirty:
            screen.blit(self.game.img('bg.png'), (0, 0))
            for p in self.people:
                p.draw(screen)
            self.dirty = False
            return True
        else:
            return False
