from conf import conf
from util import combine_drawn
import ui
from wmap import Map


def _setup_widgets (bg, *ws):
    for w in ws:
        w.bg = bg
        if isinstance(w, ui.Container):
            _setup_widgets(bg, *(child for pos, child in w.widgets))


def mk_ui (bg):
    wmap = Map(conf.WMAP_RECT[2:])
    c = ui.Container(
        (conf.WMAP_RECT[:2], wmap),
        ((conf.NEWS_LIST_RECT[:2]), ui.List(conf.NEWS_LIST_RECT[2:],
            ui.ListItem(conf.UI_WIDTH, 'Aoeu netoahun saothuntseoha tnshoeu.'),
            ui.Button(conf.UI_WIDTH, 'C anoethu aotnsehuaoet hunst aohs.'),
            ui.ListItem(conf.UI_WIDTH, 'Ft taoes oaetuheoa uthtonsu heontuhenot hth otn.'),
            ui.ListItem(conf.UI_WIDTH, 'Ihen otheo th.')
        ))
    )
    _setup_widgets(bg, c)
    return (c, wmap)


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        for k, v in conf.REQUIRED_FONTS['level'].iteritems():
            game.fonts[k] = v
        ui.render_text = game.render_text
        self.init()

    def init (self):
        self.ui, self.wmap = mk_ui(self.game.img('bg.png'))
        # reset flags
        self.dirty = True
        self.paused = False

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
