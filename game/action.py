from random import choice, triangular

from conf import conf
from util import ir, weighted_rand
import ui


class Action (object):
    def __init__ (self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)
        if not isinstance(self.news, dict):
            self.news = dict((n, 1) for n in self.news)
        self.button = ui.Button(conf.ACTIONS_LIST_RECT[2], self.desc, self.do)

    def do (self):
        tr = self.time
        t = triangular(*tr)
        news = weighted_rand(self.news).replace('%t', str(ir(t)) + ' days')
        news = news.replace('%r', '{0}-{1} days'.format(tr[0], tr[2]))
        t = ir(t * conf.DAY_FRAMES)
        print news
