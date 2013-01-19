import pygame as pg

from conf import conf
from util import combine_drawn
import ui
from wmap import Map
from action import mk_button, Selected
from ext import evthandler as eh


def _setup_widgets (bg, *ws):
    for w in ws:
        w.bg = bg
        if isinstance(w, ui.Container):
            _setup_widgets(bg, *(child for pos, child in w.widgets))


def mk_ui (bg):
    news_r = conf.NEWS_LIST_RECT
    actions_r = conf.ACTIONS_LIST_RECT
    sel = Selected(bg)
    wmap = Map(conf.WMAP_RECT[2:], sel)
    news = ui.List(news_r[2:])
    c = ui.Container(
        (conf.WMAP_RECT[:2], wmap),
        ((news_r[0], 0),
         ui.Text((news_r[2], conf.HEAD_HEIGHT), 'NEWS', 'head')),
        (news_r[:2], news),
        ((actions_r[0], 0),
         ui.Text((actions_r[2], conf.HEAD_HEIGHT), 'ACTIONS', 'head')),
        (conf.SELECTED_RECT[:2], sel),
        (actions_r[:2], ui.List(actions_r[2:], *[
            mk_button(wmap, action) for action in conf.ACTIONS
        ]))
    )
    _setup_widgets(bg, c)
    return (c, wmap, news)


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
        ui.render_text = game.render_text
        self.init()

    def init (self):
        self.ui, self.wmap, self.news = mk_ui(self.game.img('bg.png'))
        # TODO: add initial text (as news)
        # reset variables
        self._clicked = {}
        self.dirty = True
        self.paused = False

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
        if self.wmap.selecting:
            self.wmap.cancel_selecting()
        else:
            self.game.quit_backend()

    def add_news (self, *items):
        w = conf.NEWS_LIST_RECT[2]
        for item in items:
            self.news.insert(0, ui.ListItem(w, item))

    def update (self):
        if self.paused:
            return
        news = self.wmap.update()
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
