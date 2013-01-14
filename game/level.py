from collections import OrderedDict
from random import randint, choice, shuffle, gammavariate

import pygame as pg

from conf import conf
from util import ir, weighted_rand


def method_speed (method, fps, dist):
    """Get a method's speed in fraction of total distance per frame."""
    method = conf.METHODS[method]
    if method['dist']:
        return float(method['speed']) / (fps * dist)
    else:
        return 1. / (fps * method['time'])


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
dist: length of the connection line, in pixels.
methods: {method: {'allowed': allowed, 'speed': speed}} OrderedDict for each
         available method, fastest first.
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
        self.dist = dist = people[0].dist(people[1]) - \
                           2 * conf.PERSON_ICON_RADIUS
        fps = conf.FPS[None]
        methods = reversed(sorted((method_speed(m, fps, dist), m)
                                  for m in methods))
        self.methods = OrderedDict((m, {'allowed': True, 'speed': s})
                                   for s, m in methods)
        self.sending = False
        self.sent = False

    def other (self, person = None):
        """Get the person on the other end."""
        if person is None:
            person = self.sending
        return self.people[self.people[0] is person]

    def disable_method (self, method):
        self.methods[method]['allowed'] = False
        if self.sending and method == self.current_method:
            # was using this method: switch to another
            self.send()

    def enable_method (self, method):
        method = self.methods[method]
        method['allowed'] = True
        if self.sending:
            dist = self.dist
            dist_left = (1 - self.progress) * dist
            t_left = dist_left / self.methods[self.current_method]['speed']
            if dist / method['speed'] < t_left:
                # switching to this method will be quicker
                self.send()

    def send (self, sender = None):
        """Send a message from the given person.


Returns whether any methods are available, or None if already sent.

"""
        resend = sender is None
        if resend:
            # re-send in same direction
            sender = self.sending
        if not self.sent:
            self.sending = sender
            self.progress = 0
            # use fastest available method
            for m, data in self.methods.iteritems():
                if data['allowed']:
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
            self.progress += self.methods[self.current_method]['speed']
            if self.progress >= 1:
                # finished sending
                self.sending.finished(self)
                self.other().recieve(self)
                self.sent = True
                self.cancel()

    def draw_base (self, screen):
        if self.sent:
            colour = (255, 100, 100)
        else:
            colour = (100, 255, 100)
        pg.draw.aaline(screen, colour, self.people[0].pos, self.people[1].pos)

    def draw_pos (self, screen):
        if self.sending:
            x0, y0 = start = self.sending.pos
            x1, y1 = end = self.other().pos
            r = self.progress
            pos = (ir(x0 + r * (x1 - x0)), ir(y0 + r * (y1 - y0)))
            pg.draw.circle(screen, (255, 100, 100), pos, 3)


class Person (object):
    def __init__ (self, level, pos):
        self.level = level
        self.ident = None
        self.pos = pos
        self.cons = []
        self.knows = False
        self._know = []
        self.sending = False

    def __str__ (self):
        return str(self.level.people.index(self))

    __repr__ = __str__

    def dist (self, other):
        """Get the distance to another person."""
        return self.level.dists[frozenset((self, other))]

    def recieve (self, con = None):
        """Recieve the message."""
        if not self.knows:
            #print self, 'knows'
            if con is not None:
                self._know.append(con.other(self))
            self.knows = True
            self.level.n_know += 1
        elif self.sending is con:
            # recieving from the person we're sending to: cancel sending
            self.sending = False

    def send (self):
        """Send the message."""
        # find people we're connected to who don't know
        targets = []
        know = self._know
        for c in self.cons:
            if c.other(self) not in know:
                targets.append(c)
        had_any = False
        if targets:
            shuffle(targets)
            for c in targets:
                # try to send
                success = c.send(self)
                if success:
                    #print self, '->', c.other(self)
                    self.sending = c
                    return
                elif success is False:
                    had_any = True
            # no connections remain
            self.sending = False
        if not had_any:
            # everyone knows: we have nothing to do, ever
            self.sending = None

    def disabled (self, con):
        """Tell the person sending cannot continue."""
        con.cancel()
        self.send()

    def finished (self, con):
        """Tell the person sending has finished."""
        self._know.append(con.other(self))
        self.sending = False

    def update (self):
        if self.knows and self.sending is False:
            self.send()

    def draw (self, screen):
        if self.knows:
            c = (255, 100, 100)
        else:
            c = (100, 255, 100)
        pg.draw.circle(screen, c, self.pos, conf.PERSON_ICON_RADIUS)


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        self.init()

    def init (self):
        # generate people
        self.people = ps = []
        dists = {}
        self.dists = used_dists = {}
        b = conf.MAP_BORDER
        x0, y0, w, h = conf.MAP_RECT
        x1 = x0 + w - b
        y1 = y0 + h - b
        x0 += b
        y0 += b
        nearest = 2 * conf.PERSON_ICON_RADIUS + conf.PERSON_NEAREST
        for i in range(conf.NUM_PEOPLE):
            while True:
                x, y = randint(x0, x1), randint(y0, y1)
                for p in ps:
                    ox, oy = p.pos
                    dist = ((ox - x) * (ox - x) + (oy - y) * (oy - y)) ** .5
                    if dist < nearest:
                        break
                else:
                    new_p = Person(self, (x, y))
                    if ps:
                        dists[frozenset((new_p, p))] = dist
                    ps.append(new_p)
                    break
        # compute all remaining distances
        for p1 in ps:
            for p2 in ps:
                if p1 is not p2:
                    key = frozenset((p1, p2))
                    if key not in dists:
                        x1, y1 = p1.pos
                        x2, y2 = p2.pos
                        dists[key] = ((x2 - x1) * (x2 - x1) + \
                                      (y2 - y1) * (y2 - y1)) ** .5

        def add_con (p1, p2):
            # need to add dist to self.dists before creating Connection
            key = frozenset((p1, p2))
            used_dists[key] = dists[key]
            c = Connection(self, (p1, p2), ('in person',))
            self.cons.append(c)
            p1.cons.append(c)
            p2.cons.append(c)
            g1 = groups[p1]
            g2 = groups[p2]
            g1.update(g2)
            for p, g in groups.iteritems():
                if g is g2:
                    groups[p] = g1

        # generate connections
        self.cons = []
        # and group by whether connected
        groups = dict((p, set((p,))) for p in ps)
        n_cons = conf.CONS_PER_PERSON
        max_cons = conf.MAX_CONS_PER_PERSON
        # give everyone connections biased towards people near them
        for p in ps:
            # distances have a non-zero minimum
            others = dict((other, 1. / dists[frozenset((p, other))] ** \
                                       conf.SHORT_CONNECTION_BIAS)
                          for other in ps if other is not p)
            for c in p.cons:
                del others[c.other(p)]
            targets = []
            this_n_cons = ir(max(1, min(max_cons, min(len(others),
                                                      gammavariate(*n_cons)))))
            for i in xrange(this_n_cons - len(p.cons)):
                other = weighted_rand(others)
                targets.append(other)
                del others[other]
            for other in targets:
                add_con(p, other)
        # reduce to one group by adding extra connections
        frozen_groups = set(frozenset(g) for g in groups.itervalues())
        while len(frozen_groups) > 1:
            i = iter(frozen_groups)
            g1 = next(i)
            g2 = next(i)
            dist, p1, p2 = min(min((dists[frozenset((p1, p2))], p1, p2)
                                   for p2 in g2 if p2 is not p1) for p1 in g1)
            add_con(p1, p2)
            frozen_groups = set(frozenset(g) for g in groups.itervalues())

        # let someone know
        self.n_know = 0
        p = choice(ps)
        p.recieve()
        p.ident = 'initial' # mother, brother, etc.
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
        #if self.dirty:
            #self.dirty = False
        #else:
            #return False
        screen.blit(self.game.img('bg.png'), (0, 0))
        for c in self.cons:
            c.draw_base(screen)
        for p in self.people:
            p.draw(screen)
        for c in self.cons:
            c.draw_pos(screen)
        return True
