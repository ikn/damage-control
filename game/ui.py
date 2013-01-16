import pygame as pg
from pygame import Rect

from conf import conf
from util import combine_drawn, position_sfc


# widgets have:
#   .size (tuple)
#   .click(pos, evt)
#   .draw(screen, pos = (0, 0), draw_bg = True)


class Widget (object):
    def __init__ (self, size):
        self.size = size
        self.dirty = True

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        if self.dirty and draw_bg:
            screen.blit(self.bg, pos, (pos, self.size))
            return True
        return False


class Container (Widget):
    """Widget containing other widgets.

Takes any number of (pos, widget) tuples.  Widgets mustn't overlap.

"""

    def __init__ (self, *widgets):
        x0 = min(p[0] for p, w in widgets)
        x1 = max(p[0] + w.size[0] for p, w in widgets)
        y0 = min(p[1] for p, w in widgets)
        y1 = max(p[1] + w.size[1] for p, w in widgets)
        size = (x1 - x0, y1 - y0)
        Widget.__init__(self, size)
        self.widgets = widgets

    def click (self, pos, evt):
        for (x, y), w in self.widgets:
            if Rect(p, w.size).collidepoint:
                w.click((pos[0] - x, pos[1] - y), evt)
                break

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        if self.dirty:
            for p, w in self.widgets:
                w.dirty = True
            self.dirty = False
        ox, oy = pos
        rtn = []
        for (x, y), w in self.widgets:
            pos = (ox + x, oy + y)
            this_rtn = w.draw(screen, pos, draw_bg)
            if this_rtn is True:
                this_rtn = [Rect(pos, w.size)]
            rtn.append(this_rtn)
        return combine_drawn(*rtn)


class Head (Widget):
    def __init__ (self, size, text):
        Widget.__init__(self, size)
        data = conf.UI_HEAD
        text = render_text('ui head', text, data['font colour'],
                           width = size[0], just = 1)[0]
        self.text = pg.Surface(size).convert_alpha()
        self.text.fill((0, 0, 0, 0))
        position_sfc(text, self.text)

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        Widget.draw(self, screen, pos, draw_bg)
        if self.dirty:
            screen.blit(self.text, pos)
            self.dirty = False
            return True
        return False

class List (Container):
    """Widget containing a scrollable column of widgets."""

    def __init__ (self, size, *widgets):
        self._widgets_before = []
        ws = []
        h = size[1]
        g = conf.UI_LIST_GAP
        y = 0
        for i, w in enumerate(widgets):
            wh = w.size[1]
            if y + wh > h:
                self._widgets_after = list(widgets[i + 1:])
                break
            ws.append([(0, y), w])
            y += wh + g
        Container.__init__(self, *ws)
        self.size = size

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        rtn = False
        if Widget.draw(self, screen, pos, draw_bg):
            rtn = True
            draw_bg = False
        return combine_drawn(rtn, Container.draw(self, screen, pos, draw_bg))


class ListItem (Widget):
    def __init__ (self, width, text):
        # text is string or surface
        data = conf.UI_LIST_ITEM
        if isinstance(text, basestring):
            sfc = render_text('ui list item', text, data['font colour'],
                              width = width, bg = data['bg colour'],
                              pad = data['padding'])[0]
        else:
            sfc = pg.Surface(width, text.get_height() + 2 * data['padding'][1])
            sfc = sfc.convert_alpha()
            sfc.fill(data['bg colour'])
            position_sfc(text, sfc)
        size = (width, sfc.get_height())
        self.sfc = sfc
        Widget.__init__(self, size)

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        Widget.draw(self, screen, pos, draw_bg)
        if self.dirty:
            screen.blit(self.sfc, pos)
            self.dirty = False
            return True
        return False


class Button (ListItem):
    # TODO: clicking, change on hover
    def __init__ (self, width, text, cb = None):
        ListItem.__init__ (self, width, text)
        data = conf.BUTTON
        t = data['top width']
        b = data['bottom width']
        w, h = self.size
        h += t + b
        self.size = (w, h)
        sfc = pg.Surface(self.size).convert_alpha()
        sfc.fill((0, 0, 0, 0))
        sfc.blit(self.sfc, (0, t))
        sfc.fill(data['top colour'], (0, 0, w, t))
        sfc.fill(data['bottom colour'], (0, h - b, w, b))
        self.sfc = sfc
        self.cb = cb
