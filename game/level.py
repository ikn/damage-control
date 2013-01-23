import pygame as pg

from conf import conf
from util import combine_drawn, sum_pos
import ui
from wmap import Map
import action
from ext import evthandler as eh


def _setup_widgets (bg, *ws):
    for w in ws:
        w.bg = bg
        if isinstance(w, ui.Container):
            _setup_widgets(bg, *(child for pos, child in w.widgets))
        if isinstance(w, InfluenceWidget):
            w.text.bg = w.bg


def mk_ui (level):
    bg = level.game.img('bg.png')
    news_r = conf.NEWS_LIST_RECT
    actions_r = conf.ACTIONS_LIST_RECT
    sel = action.Selected(bg)
    influence = InfluenceWidget(level.influence)
    wmap = Map(level, conf.WMAP_RECT[2:], sel)
    sel.wmap = wmap
    news = ui.List(news_r[2:])
    c = ui.Container(
        (conf.WMAP_RECT[:2], wmap),
        ((news_r[0], 0),
         ui.Text((news_r[2], conf.HEAD_HEIGHT), 'NEWS', 'head')),
        (news_r[:2], news),
        ((actions_r[0], 0),
         ui.Text((actions_r[2], conf.HEAD_HEIGHT), 'ACTIONS', 'head')),
        (conf.INFLUENCE_RECT[:2], influence),
        (conf.SELECTED_RECT[:2], sel),
        (actions_r[:2], ui.List(actions_r[2:], *[
            action.mk_button(wmap, a) for a in conf.ACTIONS
        ]))
    )
    _setup_widgets(bg, c)
    return (c, wmap, news, influence)


class InfluenceWidget (ui.Widget):
    def __init__ (self, n):
        ui.Widget.__init__(self, conf.INFLUENCE_RECT[2:])
        self._n = None
        self.set_val(n)

    def set_val (self, n):
        n = int(n)
        if n != self._n:
            text = 'Influence points: {0}'.format(n)
            self.text = ui.Text(self.size, text, 'normal', 0)
            if self._n is not None:
                self.text.bg = self.bg
            self._n = n

    def draw (self, screen, pos, draw_bg = True):
        rtn = False
        if ui.Widget.draw(self, screen, pos, draw_bg):
            draw_bg = False
        if self.dirty:
            rtn = True
            self.dirty = False
        return combine_drawn(rtn, self.text.draw(screen, pos, draw_bg))


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        event_handler.add_event_handlers({
            pg.MOUSEBUTTONDOWN: self._mbdown,
            pg.MOUSEBUTTONUP: self._mbup
        })
        event_handler.add_key_handlers([
            (conf.KEYS_BACK, self._cancel, eh.MODE_ONDOWN)
        ])
        for k, v in conf.REQUIRED_FONTS['level'].iteritems():
            game.fonts[k] = v
        action.game = game
        ui.game = game
        self.init()

    def init (self):
        # reset variables
        self.influence = conf.INITIAL_INFLUENCE
        self._clicked = {}
        self.dirty = True
        self.paused = False
        # create UI
        self.ui, self.wmap, self.news, self.influence_w = mk_ui(self)
        # TODO: add initial text (as news)

    def _mbdown (self, evt):
        w = self.ui.click(evt.pos, evt)
        if w:
            self._clicked[evt.button] = w

    def _mbup (self, evt):
        b = evt.button
        if b in self._clicked:
            self._clicked[b].click(evt.pos, evt)
            del self._clicked[b]

    def _cancel (self, *args):
        if self.wmap.selected.showing_type:
            self.wmap.selected.show(None, self.wmap.selecting)
        elif self.wmap.selecting:
            self.wmap.cancel_selecting()
        #else:
            #self.pause()

    def add_news (self, *items):
        w = conf.NEWS_LIST_RECT[2]
        for item in items:
            self.news.insert(0, ui.ListItem(w, item))

    def spend (self, cost):
        self.influence -= cost
        self.influence_w.set_val(self.influence)

    def update (self):
        if self.paused:
            return
        # update influence
        wmap = self.wmap
        self.spend(-conf.INFLUENCE_GROWTH_RATE * \
                   (1 - float(wmap.n_know) / len(wmap.people)))
        news = wmap.update()
        if news:
            self.add_news(*news)

    def draw (self, screen):
        rtn = False
        draw_bg = True
        if self.dirty:
            self.ui.dirty = True
            screen.blit(self.game.img('bg.png'), (0, 0))
            rtn = True
            draw_bg = False
            self.dirty = False
        return combine_drawn(rtn, self.ui.draw(screen, draw_bg = draw_bg))
