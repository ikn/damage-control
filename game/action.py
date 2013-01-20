from random import choice, triangular

import pygame as pg
from pygame import Surface

from conf import conf
from util import ir, weighted_rand, combine_drawn
import wmap
import ui

def mk_button (wmap, action):
    def cb (evt, last_up, inside):
        if last_up and inside:
            Action(wmap, action)

    return ui.Button(conf.ACTIONS_LIST_RECT[2], action['desc'], cb)


class Action (object):
    def __init__ (self, wmap, data):
        self._wmap = wmap
        self.data = data
        self.type = data['type']
        wmap.ask_select_target(self)

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
        data = self.data
        del self.data
        self._news_end = data['news end']
        # generate news substitution text
        t = triangular(*data['time'])
        self._news_data = n_data = {
            't': '{0} days'.format(ir(t)),
            'r': '{0}-{1} days'.format(data['time'][0], data['time'][2])
        }
        if data['type'] == 'p':
            p = target.name
            n_data['p'] = p
            n_data['P'] = p.capitalize()
            t_pos = target.pos
        elif data['type'] == 'c':
            t_pos = target.centre
        else: # data['type'] == 'a'
            n_data['a'] = target[0]
        if data['type'] != 'a':
            n_data['a'] = self._wmap.area(t_pos)
        # generate initial news and register with map
        news = data['news start']
        return (ir(t * conf.DAY_FRAMES), self._mk_news(news))

    def end (self):
        return self._mk_news(self._news_end)


class Selected (ui.Container):
    def __init__ (self, bg):
        ui.Container.__init__(self)
        self.size = conf.SELECTED_RECT[2:]
        self._bg = bg
        self.show(None)

    def _cancel (self, evt, last_up, inside):
        if last_up and inside:
            self.wmap.cancel_selecting()

    def _start (self, evt, last_up, inside):
        if last_up and inside:
            self.wmap.start_action()
            self.wmap.cancel_selecting()

    def show (self, obj, action = None):
        """Show something.

show(obj, action = None)

obj: the thing to show: None for nothing, a Person, a Connection, or
     name for an area.  If action is given, area is (name, people, cons), where
     people and cons are those inside the area.
action: if the player is selecting an area for an action, this is the Action
        instance.

"""
        # store what we're showing
        if obj is None:
            showing_type = ''
        elif isinstance(obj, wmap.Connection):
            showing_type = 'c'
        elif isinstance(obj, wmap.Person):
            showing_type = 'p'
        else: # area
            showing_type = 'a'
        if action:
            showing_type += ' action'
        if hasattr(self, 'showing') and obj == self.showing and \
           showing_type == self.showing_type:
            return
        self.showing = obj
        self.showing_type = showing_type
        # data is a list of rows, each a list of widget representations, or
        # just a row if there's only one row.  Widgets are vertically centred
        # within rows.  Representations are (font, text, width), a surface, a
        # Widget, or an int for padding.  A row can also be an int for padding.
        width = self.size[0]
        if obj is None:
            data = (('subhead', 'Nothing selected', width),)
        elif showing_type[0] == 'c':
            current_method = obj.current_method if obj.sending else None
            s = ''
            for method, data in obj.methods.iteritems():
                s += method[:2]
                if method == current_method:
                    s += '+'
                elif not data['allowed']:
                    s += '/'
            data = (
                (('subhead', 'Selected: connection', width),),
                (('normal', s, None),),
                (('normal', '{0} km long'.format(ir(obj.dist)), None),)
            )
        elif showing_type[0] == 'p':
            data = (
                ('subhead', 'Selected: {0}'.format(obj.name), width),
            )
            #ic_w = obj.img.get_width()
            #data = (
                #ic_w + 5,
                #('subhead', 'Selected: connection', width - ic_w - 10),
                #5,
                #obj.img
            #)
        else: # area
            if action:
                name, people, cons = obj
            else:
                name = obj
            data = ((('subhead', 'Selected: {0}'.format(name), width),),)
            if action:
                body_text = 'contains {0} people, {1} connections'
                data += ((('normal', body_text.format(len(people),
                           len(cons)),
                          width),),)
        if isinstance(data[0], pg.Surface) or \
           isinstance(data[0][0], basestring):
            data = (data,)
        if action:
            data += (5, (ui.Button(width, 'Cancel', self._cancel),),)
            if obj is None:
                pass # TODO: show 'please select a(n) person/connection/area'
            else:
                data += (5, (ui.Button(width, 'OK', self._start),),)
        # generate widgets
        ws = []
        y = 0
        for row in data:
            if isinstance(row, int):
                y += row
                continue
            this_ws = []
            hs = []
            # create widgets and position in x
            x = 0
            for w in row:
                if isinstance(w, pg.Surface):
                    w = ui.Img(w)
                elif isinstance(w, int):
                    # padding
                    x += w
                    continue
                elif isinstance(w, ui.Widget):
                    pass
                else:
                    # text
                    font, text, ww = w
                    w = ui.Text((ww, None), text, font)
                w.bg = self._bg
                this_ws.append((x, w))
                x += w.size[0]
                hs.append(w.size[1])
            # centre in the row
            h = max(hs)
            for this_h, (x, w) in zip(hs, this_ws):
                ws.append(((x, y + (h - this_h) / 2), w))
            y += h
        self.widgets = ws
        self.dirty = True

    def draw (self, screen, pos, draw_bg = True):
        # Container doesn't draw its BG, but we want to, so call Widget.draw
        rtn = False
        if ui.Widget.draw(self, screen, pos, draw_bg):
            rtn = True
            draw_bg = False
        return combine_drawn(rtn,
                             ui.Container.draw(self, screen, pos, draw_bg))
