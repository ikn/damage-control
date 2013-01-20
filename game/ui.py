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
        self.size = tuple(size)
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
        if widgets:
            x0 = min(p[0] for p, w in widgets)
            x1 = max(p[0] + w.size[0] for p, w in widgets)
            y0 = min(p[1] for p, w in widgets)
            y1 = max(p[1] + w.size[1] for p, w in widgets)
            size = (x1 - x0, y1 - y0)
        else:
            size = (0, 0)
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


class List (Container):
    """Widget containing a scrollable column of widgets.

    METHODS

append
insert
pop
scroll_by
scroll_to

    ATTRIBUTES

top: index of top visible widget.
bottom: index of bottom visible widget + 1.

"""

    def __init__ (self, size, *widgets):
        Widget.__init__(self, size)
        self._widgets_before = []
        self.widgets = []
        self._widgets_after = []
        self.top = 0
        self.bottom = 0
        self.append(*widgets)
        start = len(self._widgets_before)

    def __len__ (self):
        return len(self._widgets_before) + len(self.widgets) + \
               len(self._widgets_after)

    def append (self, *ws):
        after = self._widgets_after
        if after:
            after.extend(ws)
        else:
            # start below last widget
            visible = self.widgets
            g = conf.LIST_GAP
            if visible:
                (x, y), last = visible[-1]
                y += last.size[1] + g
            else:
                y = 0
            h = self.size[1]
            for i, w in enumerate(ws):
                wh = w.size[1]
                if y + wh > h:
                    # doesn't fit
                    after.extend(ws[i + 1:])
                    break
                visible.append([(0, y), w])
                y += wh + g
            self.dirty = True
            self.bottom = self.top + len(visible)

    def insert (self, i, widget):
        if i < self.top:
            self._widgets_before.insert(i, widget)
            self.top += 1
            self.bottom += 1
        elif i >= self.bottom and self._widgets_after:
            self._widgets_after.insert(i - self.bottom, widget)
        else:
            # will (want to) be visible: need to reallocate positions
            ws = self.widgets
            readd = [widget] + [w for p, w in ws[i - self.top:]]
            self.widgets = ws[:i - self.top]
            readd += self._widgets_after
            self._widgets_after = []
            self.append(*readd)
            self.dirty = True

    def pop (self, i):
        if i < self.top:
            self._widgets_before.pop(i)
        elif i >= self.bottom:
            self._widgets_after.pop(i - self.bottom)
        else:
            ws = self.widgets
            i -= self.top
            ws.pop(i)
            self.widgets = ws[:i]
            self.append(*(w for p, w in ws[i:]))
            self.dirty = True

    def scroll_by (self, n):
        if n == 0:
            return
        if n < 0:
            before = self._widgets_before
            if not before:
                # nothing to show
                return
            readd = before[n:] + [w for p, w in self.widgets] + \
                    self._widgets_after
            self._widgets_before = before[:n]
            self.widgets = []
            self._widgets_after = []
            self.append(*readd)
        else: # n > 0
            if not self._widgets_after:
                # nothing to show
                return
            ws = [w for p, w in self.widgets]
            self._widgets_before.extend(ws[:n])
            self.widgets = []
            readd = ws[n:] + self._widgets_after
            self._widgets_after = []
            self.append(*readd)
        self.dirty = True

    def scroll_to (self, n):
        if n < self.top:
            self.scroll_by(n - self.top)
        elif n >= self.bottom:
            self.scroll_by(self.bottom + 1 - n)
        # else already visible

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        rtn = False
        if Widget.draw(self, screen, pos, draw_bg):
            rtn = True
            draw_bg = False
        return combine_drawn(rtn, Container.draw(self, screen, pos, draw_bg))


class Img (Widget):
    def __init__ (self, sfc):
        self.sfc = sfc
        Widget.__init__(self, sfc.get_size())

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        Widget.draw(self, screen, pos, draw_bg)
        if self.dirty:
            screen.blit(self.sfc, pos)
            self.dirty = False
            return True
        return False


class Text (Img):
    def __init__ (self, size, text, font):
        text = render_text(font, text, conf.TEXT_COLOUR, width = size[0],
                           just = 1)[0]
        ts = text.get_size()
        size = [ts[i] if size[i] is None else size[i] for i in (0, 1)]
        sfc = blank_sfc(size)
        position_sfc(text, sfc)
        Img.__init__(self, sfc)


class ListItem (Img):
    def __init__ (self, width, text):
        # text is string or surface
        data = conf.LIST_ITEM
        if isinstance(text, basestring):
            sfc = render_text('normal', text, conf.TEXT_COLOUR,
                              width = width, bg = data['bg colour'],
                              pad = data['padding'])[0]
        else:
            sfc = pg.Surface(width, text.get_height() + 2 * data['padding'][1])
            sfc = sfc.convert_alpha()
            sfc.fill(data['bg colour'])
            position_sfc(text, sfc)
        Img.__init__(self, sfc)

    def draw (self, screen, pos = (0, 0), draw_bg = True):
        Widget.draw(self, screen, pos, draw_bg)
        if self.dirty:
            screen.blit(self.sfc, pos)
            self.dirty = False
            return True
        return False


class Button (ListItem):
    """A button.

    CONSTRUCTOR

Button(width, text, cb, *args, **kwargs)

width: width in pixels.
text: text to display, or a surface to blit centred.
cb, args, kwargs: cb(evt, last_up, inside, *args, **kwargs) is called on mouse
                  clicks, where:
    evt: the Pygame mouse event (button down or up).
    last_up: this is a button up event and is the last mouse button that was
             holding this button widget down.
    inside: this event occurred within the button widget (always true for
            button down events).

"""

    def __init__ (self, width, text, cb, *args, **kwargs):
        b_data = conf.BUTTON_BORDER
        bw = b_data['width']
        bc = b_data['colour']
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
        self.cb = lambda *pre_args: cb(*(pre_args + args), **kwargs)
        self._down = []

    def click (self, pos, evt):
        if evt.type == pg.MOUSEBUTTONDOWN and evt.button in conf.CLICK_BTNS \
           and self.pos is not None:
            self.cb(evt, False, True)
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
            self.cb(evt, not self._down,
                    bool(Rect(self.pos, self.size).collidepoint(pos)))
