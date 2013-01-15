from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict
from glob import glob
from random import gammavariate

import pygame as pg

import settings
from util import dd


class Conf (object):

    IDENT = 'damage-control'
    USE_SAVEDATA = False
    USE_FONTS = True

    # save data
    SAVE = ()
    # need to take care to get unicode path
    if system() == 'Windows':
        try:
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA',
                                                               None, 0)
            if n == 0:
                raise ValueError()
        except Exception:
            # fallback (doesn't get unicode string)
            CONF_DIR = os.environ[u'APPDATA']
        else:
            buf = ctypes.create_unicode_buffer(u'\0' * n)
            ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', buf, n)
            CONF_DIR = buf.value
        CONF_DIR = join_path(CONF_DIR, IDENT)
    else:
        CONF_DIR = join_path(os.path.expanduser(u'~'), '.config', IDENT)
    CONF = join_path(CONF_DIR, 'conf')

    # data paths
    DATA_DIR = ''
    IMG_DIR = DATA_DIR + 'img' + sep
    SOUND_DIR = DATA_DIR + 'sound' + sep
    MUSIC_DIR = DATA_DIR + 'music' + sep
    FONT_DIR = DATA_DIR + 'font' + sep

    # display
    WINDOW_ICON = None #IMG_DIR + 'icon.png'
    WINDOW_TITLE = 'Damage Control'
    MOUSE_VISIBLE = dd(True) # per-backend
    FLAGS = 0
    FULLSCREEN = False
    RESIZABLE = False # also determines whether fullscreen togglable
    RES_W = (1000, 600)
    RES_F = pg.display.list_modes()[0]
    RES = RES_W
    MIN_RES_W = (320, 180)
    ASPECT_RATIO = None

    # timing
    FPS = dd(30) # per-backend

    # debug
    PROFILE_STATS_FILE = '.profile_stats'
    DEFAULT_PROFILE_TIME = 5

    # input
    KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
    KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
    KEYS_MINIMISE = (pg.K_F10,)
    KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                    (pg.K_KP_ENTER, pg.KMOD_ALT, True))
    KEYS_LEFT = (pg.K_LEFT, pg.K_a, pg.K_q)
    KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
    KEYS_UP = (pg.K_UP, pg.K_w, pg.K_z, pg.K_COMMA)
    KEYS_DOWN = (pg.K_DOWN, pg.K_s, pg.K_o)
    KEYS_DIRN = (KEYS_LEFT, KEYS_UP, KEYS_RIGHT, KEYS_DOWN)

    # audio
    MUSIC_AUTOPLAY = False # just pauses music
    MUSIC_VOLUME = dd(.5) # per-backend
    SOUND_VOLUME = .5
    EVENT_ENDMUSIC = pg.USEREVENT
    SOUND_VOLUMES = dd(1)
    # generate SOUNDS = {ID: num_sounds}
    SOUNDS = {}
    ss = glob(join_path(SOUND_DIR, '*.ogg'))
    base = len(join_path(SOUND_DIR, ''))
    for fn in ss:
        fn = fn[base:-4]
        for i in xrange(len(fn)):
            if fn[i:].isdigit():
                # found a valid file
                ident = fn[:i]
                if ident:
                    n = SOUNDS.get(ident, 0)
                    SOUNDS[ident] = n + 1

    # graphics
    UI_WIDTH = 149 # has 1px border in bg.png
    WMAP_RECT = (UI_WIDTH, 0, RES[0] - 2 * UI_WIDTH, RES[1])
    NEWS_LIST_RECT = (0, 40, UI_WIDTH, RES[1])
    rhs_ui = RES[0] - UI_WIDTH
    ACTIONS_LIST_RECT = (rhs_ui, 40, UI_WIDTH, RES[1])
    # world map
    PERSON_ICON_RADIUS = 5
    WMAP_BORDER = 15 # contains no people
    # ui
    UI_HEAD = {
        'font size': 25,
        'box height': 32
    }
    UI_LIST_GAP = 2
    UI_LIST_ITEM = {
        'bg colour': (255, 255, 255, 52),
        'font size': 12,
        'font colour': (255, 255, 255),
        'padding': (5, 2) # x, y
    }
    BUTTON = {
        'top colour': (255, 255, 255, 84),
        'top width': 2,
        'bottom colour': (164, 164, 164, 46),
        'bottom width': 2
    }

    # text rendering
    FONT = None
    # per-backend, each a {key: value} dict to update Game.fonts with
    REQUIRED_FONTS = dd({}, level = {
        #'ui_list_item': (FONT, UI_LIST_ITEM['font size']),
        #'ui_head': (FONT, UI_HEAD['font size'])
    })

    # gameplay
    # world map initialisation
    PERSON_NEAREST = 20
    NUM_PEOPLE = 50
    CONS_PER_PERSON = lambda: gammavariate(5, .5)
    MAX_CONS_PER_PERSON = 6
    SHORT_CONNECTION_BIAS = 4
    METHODS_PER_CON = lambda: gammavariate(3, .5)
    # world map: running
    # if dist, speed is in pixels per second
    # else time is in frames
    METHODS = {
        'phone': {'dist': False, 'time': 6, 'freq': 1},
        'in person': {'dist': True, 'speed': 2, 'freq': 1},
        'e-mail': {'dist': False, 'time': 6, 'freq': 1},
        'fax': {'dist': False, 'time': 6, 'freq': 1},
        'mail': {'dist': True, 'speed': 6, 'freq': 1},
        'carrier pigeon': {'dist': True, 'speed': 6, 'freq': 1},
        'message in a bottle': {'dist': True, 'speed': 1, 'freq': 1},
        'telepathy': {'dist': False, 'time': 6, 'freq': 1},
        'beacon': {'dist': True, 'speed': 6, 'freq': 1},
        'drums': {'dist': True, 'speed': 6, 'freq': 1},
        'radio': {'dist': False, 'time': 6, 'freq': 1},
        'pager': {'dist': False, 'time': 6, 'freq': 1},
        'newspaper crossword': {'dist': False, 'time': 6, 'freq': 1},
        'skywriting': {'dist': False, 'time': 6, 'freq': 1},
        'telegraph': {'dist': False, 'time': 6, 'freq': 1}
    }


def translate_dd (d):
    if isinstance(d, defaultdict):
        return defaultdict(d.default_factory, d)
    else:
        # should be (default, dict)
        return dd(*d)
conf = dict((k, v) for k, v in Conf.__dict__.iteritems()
            if k.isupper() and not k.startswith('__'))
types = {
    defaultdict: translate_dd
}
if Conf.USE_SAVEDATA:
    conf = settings.SettingsManager(conf, Conf.CONF, Conf.SAVE, types)
else:
    conf = settings.DummySettingsManager(conf, types)
