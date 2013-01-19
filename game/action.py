from random import choice, triangular

from conf import conf
from util import ir, weighted_rand
import ui

def mk_button (wmap, action):
    def cb (evt, last_up, inside):
        if last_up and inside:
            Action(wmap, action)

    return ui.Button(conf.ACTIONS_LIST_RECT[2], action['desc'], cb)


class Action (object):
    def __init__ (self, wmap, data):
        self._wmap = wmap
        self._data = data
        wmap.ask_select_target(self, data['type'])

    def _mk_news (self, items):
        if not isinstance(items, dict):
            items = dict((n, 1) for n in items)
        s = weighted_rand(items)
        if s is None:
            return None
        # substitute some values
        for c, sub in self._news_data.iteritems():
            s = s.replace('%' + c, sub)
        return s

    def start (self, target):
        self.target = target
        data = self._data
        del self._data
        self._news_end = data['news end']
        # generate news substitution text
        t = triangular(*data['time'])
        self._news_data = n_data = {
            't': '{0} days'.format(ir(t)),
            'r': '{0}-{1} days'.format(data['time'][0], data['time'][2])
        }
        if data['type'] == 'p':
            p = target.ident
            n_data['p'] = p
            n_data['P'] = p.capitalize()
            t_pos = target.pos
        elif data['type'] == 'c':
            p1, p2 = target.people
            t_pos = (.5 * (p1.pos[0] + p2.pos[0]), .5 * (p1.pos[1], p2.pos[1]))
        else: # data['type'] == 'a'
            t_pos = target
        n_data['a'] = self._wmap.area(t_pos)
        # generate initial news and register with map
        news = data['news start']
        return (ir(t * conf.DAY_FRAMES), self._mk_news(news))

    def end (self):
        return self._mk_news(self._news_end)
