import pygame as pg

from conf import conf
from util import combine_drawn
import ui
from wmap import Map
from action import Action


def _setup_widgets (bg, *ws):
    for w in ws:
        w.bg = bg
        if isinstance(w, ui.Container):
            _setup_widgets(bg, *(child for pos, child in w.widgets))


def mk_ui (bg):
    news_r = conf.NEWS_LIST_RECT
    actions_r = conf.ACTIONS_LIST_RECT
    wmap = Map(conf.WMAP_RECT[2:])
    c = ui.Container(
        (conf.WMAP_RECT[:2], wmap),
        ((news_r[0], 0), ui.Head((news_r[2], conf.UI_HEAD_HEIGHT), 'NEWS')),
        (news_r[:2], ui.List(news_r[2:],
            ui.ListItem(news_r[2], 'Aoeu netoahun saothuntseoha tnshoeu.'),
            ui.ListItem(news_r[2], 'Ft taoes oaetuheoa uthtonsu heontuhenot hth otn.'),
            ui.ListItem(news_r[2], 'Ihen otheo th.')
        )),
        ((actions_r[0], 0),
         ui.Head((actions_r[2], conf.UI_HEAD_HEIGHT), 'ACTIONS')),
        (actions_r[:2], ui.List(actions_r[2:], *[
            Action(action).button for action in conf.ACTIONS
        ]))
    )
    _setup_widgets(bg, c)
    return (c, wmap)


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        event_handler.add_event_handlers({
            pg.MOUSEBUTTONDOWN: self._mbdown,
            pg.MOUSEBUTTONUP: self._mbup
        })
        for k, v in conf.REQUIRED_FONTS['level'].iteritems():
            game.fonts[k] = v
        ui.render_text = game.render_text
        self.init()

    def init (self):
        self.ui, self.wmap = mk_ui(self.game.img('bg.png'))
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

    def update (self):
        if self.paused:
            return
        news = self.wmap.update()
        #if news:
        #   self.news.add(*news)

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
