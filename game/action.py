from random import triangular

import pygame as pg
from pygame import Surface

from conf import conf
from util import ir, weighted_rand, combine_drawn, blank_sfc
import wmap
import ui

def mk_button (wmap, action):
    def cb (evt, last_up, inside):
        if last_up and inside:
            Action(wmap, action)

    desc = '[{0}] {1}'.format(action['cost'], action['desc'])
    return ui.Button(conf.ACTIONS_LIST_RECT[2], desc, cb)


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
        methods = data['affects']
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
        # and put action into effect
        else: # data['type'] == 'a'
            n_data['a'] = target[0]
            for obj in target[1] + target[2]: # people and connections
                obj.disable_methods(self, *methods)
        if data['type'] != 'a':
            n_data['a'] = self._wmap.area(t_pos)
            target.disable_methods(self, *methods)
        # generate initial news
        news = self._mk_news(data['news start'])
        return (ir(t * conf.DAY_FRAMES), data['cost'], news)

    def end (self):
        # undo action's effects
        target = self.target
        t_type = self.data['type']
        methods = self.data['affects']
        if t_type in 'pc':
            target.enable_methods(self, *methods)
        else: # area
            for obj in target[1] + target[2]:
                obj.enable_methods(self, *methods)
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

    def _method_map (self, methods):
        width = self.size[0]
        pad = 1
        using_b_c = conf.LINE_COLOUR_BAD[0]
        affected_b_c = conf.LINE_COLOUR_GOOD[0]
        sz = conf.METHOD_ICON_SIZE
        n_per_row = (width + pad) / (sz + 6 + pad)
        x0 = (width - (n_per_row * (sz + 6) + (n_per_row - 1) * pad)) / 2
        rows = []
        row = [x0]
        for method in methods:
            method, disabled, using, affected = method
            if len(row) == 2 * n_per_row + 1:
                rows.append(row)
                rows.append(pad)
                row = [x0]
            img = game.img(method + '.png')
            sfc = blank_sfc((sz + 6, sz + 6))
            if using:
                sfc.fill(using_b_c)
            if affected:
                if using:
                    sfc.fill(affected_b_c, (1, 1, sz + 4, sz + 4))
                else:
                    sfc.fill(affected_b_c)
            if using or affected:
                sfc.fill((0, 0, 0, 0), (2, 2, sz + 2, sz + 2))
            sfc.blit(img, (3, 3))
            if disabled:
                sfc.fill((150, 150, 150), None, pg.BLEND_RGBA_MULT)
            row.append(sfc)
            row.append(pad)
        rows.append(row)
        row.pop(-1)
        return rows

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
        if hasattr(self, 'showing') and obj == self.showing and \
           showing_type == self.showing_type and action == self.action:
            return
        # update things' selected states
        if not hasattr(self, 'showing') or obj != self.showing:
            if hasattr(self, 'showing'):
                if self.showing_type in ('p', 'c'):
                    self.showing.unselect()
                elif self.action and self.showing_type == 'a':
                    self.wmap.unsel_area()
            if showing_type in ('p', 'c'):
                obj.select()
            elif action and showing_type == 'a':
                self.wmap.sel_area(action.pos, action.data['radius'])
        self.showing = obj
        self.showing_type = showing_type
        self.action = action
        # data is a list of rows, each a list of widget representations.
        # Widgets are vertically centred within rows.  Representations are
        # (font, text, width), a surface, a Widget, or an int for padding.  A
        # row can also be an int for padding.
        width = self.size[0]
        data = []
        if obj is None:
            head = 'Nothing selected'
        elif showing_type == 'c':
            current_method = obj.current_method if obj.sending else None
            affected = action.data['affects'] if action else []
            head = 'Selected: connection'
            data.append(5)
            data += self._method_map(
                [(method, data['disabled'], method == current_method,
                  method in affected)
                 for method, data in obj.methods.iteritems()]
            )
            data += [
                5,
                (('normal', '{0} km long'.format(ir(obj.dist)), None),)
            ]
        elif showing_type == 'p':
            head = 'Selected: {0}'.format(obj.name)
            # icon
            img = obj.img(False)
            img_w = img.get_width()
            data += [5, (img,)]
        else: # area
            if action:
                name, people, cons = obj
            else:
                name = obj
            head = 'Selected: {0}'.format(name)
            if action:
                body_text = 'contains {0} people, {1} connections'
                data += [
                    5,
                    (('normal', body_text.format(len(people), len(cons)),
                      width),)
                ]
        if action:
            # insert action note
            if obj is None:
                text = 'Select {0} for the action \'{1}\'.'
                text = text.format({
                    'p': 'a person',
                    'c': 'a connection',
                    'a': 'an area'
                }[action.type], action.data['desc'])
            else:
                text = '(For the action \'{0}\'.)'.format(action.data['desc'])
            data = [5, (('normal', text, width),)] + data
            if obj is None:
                methods = [(method, False, False, True)
                           for method in action.data['affects']]
                data = [data[0]] + self._method_map(methods) + data[1:]
        # add heading
        data = [5, (('subhead', head, width),)] + data
        if action:
            # add buttons
            data.append(10)
            if obj is not None:
                data += [
                    (ui.Button(width, 'OK', self._start),),
                    5
                ]
            data.append((ui.Button(width, 'Cancel', self._cancel),))
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
                    just = 0 if font == 'normal' else 1
                    w = ui.Text((ww, None), text, font, just)
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
