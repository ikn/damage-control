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
    CLICK_BTNS = (1, 2, 3)
    SCROLL_BTNS = (4, 5)

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
    # images
    METHOD_ICON_SIZE = 12
    # layout
    sidebar_t = 40
    NEWS_LIST_RECT = (0, sidebar_t, 249, RES[1] - sidebar_t)
    actions_w = 149
    sel_h = 200
    SELECTED_RECT = (RES[0] - actions_w + 2, RES[1] - sel_h, actions_w - 4,
                     sel_h - 2)
    influence_h = 40
    INFLUENCE_RECT = (RES[0] - actions_w + 2, RES[1] - sel_h - influence_h,
                      actions_w - 4, influence_h)
    ACTIONS_LIST_RECT = (RES[0] - actions_w, sidebar_t, actions_w,
                         RES[1] - sidebar_t - sel_h - influence_h)
    WMAP_RECT = (NEWS_LIST_RECT[2], 0, RES[0] - NEWS_LIST_RECT[2] - actions_w,
                 RES[1])
    # world map
    WMAP_BORDER = 15 # contains no people
    LINE_COLOUR_GOOD = (17, 209, 93),
    LINE_COLOUR_BAD = (196, 94, 99)
    # ui
    HEAD_HEIGHT = 32
    LIST_GAP = 2
    LIST_ITEM = {
        'bg colour': (255, 255, 255, 52),
        'padding': (2, 2) # x, y
    }
    BUTTON_BORDER = {
        'width': 3,
        'colour': ((255, 255, 255, 90), (150, 150, 150, 46)) # lt, rb
    }
    # text rendering
    TEXT_COLOUR = (255, 255, 255)
    # per-backend, each a {key: value} dict to update Game.fonts with
    REQUIRED_FONTS = dd({}, level = {
        'normal': ('Jura-Regular.ttf', 12),
        'head': ('Jura-DemiBold.ttf', 27),
        'subhead': ('Jura-DemiBold.ttf', 16)
    })

    # gameplay
    INITIAL_INFLUENCE = 0
    INFLUENCE_GROWTH_RATE = .1 # increase per frame
    DAY_FRAMES = 4 * FPS['level']
    # world map initialisation
    PERSON_NEAREST = 5 # must be > 0
    NUM_PEOPLE = 50
    CONS_PER_PERSON = lambda: gammavariate(5, .5)
    MAX_CONS_PER_PERSON = 6
    SHORT_CONNECTION_BIAS = 4
    METHODS_PER_CON = lambda: gammavariate(3, .5)
    # world map: running
    PERSON_RADIUS = 12 # must be <= PERSON_NEAREST
    CON_RADIUS_SQ = 30 ** 2
    AREAS = ['Area 11']
    NUM_AREAS = min(len(AREAS), 9)
    FACTS = [
        'your favourite game is Superman 64',
        'you\'re actually a vampire'
    ]
    # person names
    FULL_NAMES = [
        'your mother', 'your father', 'your brother', 'your sister',
        'your son', 'your daughter', 'your spouse', 'your nemesis',
        'your neighbour', 'the prime minister of the world', 'some guy',
        'your pet ferret', 'the king of the homeless', 'King Henry VIII',
        'your evil clone', 'your future self', 'a rabid boar', 'Zeus',
        'Mack McMacdonald'
    ]
    # keys can be (male, female); values are weightings
    TITLES = {
        None: 20, ('King', 'Queen'): 1, ('Sir', 'Dame'): 4, 'Angel': .5,
        'Reverend': 1, 'Reverend Doctor Doctor': .2, 'Doctor': 2, 'Colonel': 1,
        'Sideshow': 1
    }
    FORENAMES = {
        'male': ['Cuthbert', 'Reginald', 'Satan'],
        'female': []
    }
    SURNAMES = [
        'of Narnia', 'the Conqueror'
    ]
    # if dist, speed is in pixels per day
    # else time is in days
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
    # type: 'c' (connection), 'p' (person) or 'a' (area); area type requires
    #       radius in pixels
    # time: triangular distribution (min, mean, max) in days
    # news *: {text: freq} or tuple of texts for equal freqs; can contain %p/%P
    #         for person, %a for area
    # news_start can contain %t for time, %r for time range
    ACTIONS = [
        {
            'desc': 'cut phone line',
            'type': 'c',
            'cost': 10,
            'affects': ('phone', 'fax', 'telegraph'),
            'time': (5, 7, 10),
            'news start': (
'An engineer will be sent to fix reported telephone outages.  Job time ' \
'estimate: %t.',
            ), 'news end': (
'end phone',
            )
        }, {
            'desc': 'broadcast jamming signal',
            'type': 'a',
            'radius': 150,
            'cost': 10,
            'affects': ('telepathy', 'radio', 'pager'),
            'time': (4, 6, 7),
            'news start': (
'Disruptions to wireless services have been detected in %a.  We expect to ' \
'find the source in %r.',
            ), 'news end': (
'end jamming',
            )
        }
    ]


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
