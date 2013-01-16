import pygame as pg
from pygame import Rect

from conf import conf
from util import position_sfc, combine_drawn, blank_sfc


# widgets have:
#   .size (tuple)
#   .click(pos, evt)
#       returns widget to register for button release
#   .draw(screen, pos = (0, 0), draw_bg = True)


class Widget (object):
    def __init__ (self, size):
        self.size = size
        self.pos = None
        self.dirty = True

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        if self.dirty:
            self.pos = pos
            if draw_bg:
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
            if hasattr(w, 'click') and Rect((x, y), w.size).collidepoint(pos):
                return w.click((pos[0] - x, pos[1] - y), evt)

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        Widget.draw(self, screen, pos, False)
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
        self.text = blank_sfc(size)
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
    def __init__ (self, width, text, cb, *args, **kwargs):
        data = conf.BUTTON
        bw = data['border width']
        bc = data['border colour']
        ListItem.__init__(self, width - 2 * bw, text)
        w, h = self.size
        w += 2 * bw
        h += 2 * bw
        self.size = (w, h)
        sfcs = []
        for bc in (bc, tuple(reversed(bc))):
            sfc = blank_sfc(self.size)
            sfc.blit(self.sfc, (bw, bw))
            sfc.fill(bc[0], (0, bw, bw, h))
            sfc.fill(bc[0], (0, 0, w, bw))
            sfc.fill(bc[1], (w - bw, bw, bw, h - 2 * bw))
            sfc.fill(bc[1], (bw, h - bw, w - bw, bw))
            sfcs.append(sfc)
        self._sfc, self._click_sfc = sfcs
        self.sfc = self._sfc
        self.cb = lambda: cb(*args, **kwargs)
        self._down = []

    def click (self, pos, evt):
        if evt.type == pg.MOUSEBUTTONDOWN and evt.button in conf.CLICK_BTNS \
           and self.pos is not None:
            self._down.append(evt.button)
            if self.sfc != self._click_sfc:
                self.sfc = self._click_sfc
                self.dirty = True
            return self
        elif evt.type == pg.MOUSEBUTTONUP and self.sfc != self._sfc:
            self._down.remove(evt.button)
            if not self._down:
                self.sfc = self._sfc
                self.dirty = True
                if Rect(self.pos, self.size).collidepoint(pos):
                    self.cb()
