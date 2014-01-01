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
    WINDOW_ICON = IMG_DIR + 'icon.png'
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
    METHOD_USING_BORDER_COLOUR = (17, 209, 93)
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
    # (unselected, selected)
    LINE_COLOUR_GOOD = ((17, 209, 93), (225, 255, 225))
    LINE_COLOUR_BAD = ((196, 94, 99), (255, 200, 200))
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
    INITIAL_INFLUENCE = 100
    INFLUENCE_GROWTH_RATE = .15 # increase per frame
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
    AREAS = ['Area 51']
    NUM_AREAS = min(len(AREAS), 9)
    FACTS = [
        'your favourite game is Superman 64',
        'you\'re actually a vampire',
        'you hate fruit',
        'you\'re always contagious',
        'you hate rumours',
        'you have a monopoly on the world\'s supply of chocolate',
        'you\'re a politician at night',
        'you can\'t grow eyebrows',
        'you feed your guests to your pet dragon',
        'you stretch your children on a daily basis',
        'you lock up sane people in mental asylums',
        'you test cosmetics on babies',
        'you\'re scared of bright lights and are plotting to block out the Sun',
        'you hate snow',
        'you float in water and have more broomsticks than necessary'
    ]
    # person names
    FULL_NAMES = [
        'your mother', 'your father', 'your brother', 'your sister',
        'your son', 'your daughter', 'your spouse', 'your nemesis',
        'your neighbour', 'the prime minister of the world', 'some guy',
        'your pet ferret', 'the king of the homeless', 'King Henry VIII',
        'your evil clone', 'your future self', 'a rabid boar', 'Zeus',
        'Mack McMacdonald', 'Frog?', 'the Grinch'
    ]
    NUM_FULL_NAMES = min(len(FULL_NAMES) / 2, int(.4 * NUM_PEOPLE))
    # keys can be (male, female); values are weightings
    TITLES = {
        None: 30, ('King', 'Queen'): 1, ('Sir', 'Dame'): 5, 'Angel': .5,
        'Reverend': 2, 'Reverend Doctor Doctor': .2, 'Doctor': 3, 'Colonel': 1,
        'Sideshow': 1, ('Duke', 'Duchess'): 1, ('Count', 'Countess'): 1,
        'Pope': .5, 'Baby': .2, 'Captain': 1.5
    }
    FORENAMES = {
        'male': [
            'Cuthbert', 'Satan', 'Aloisius', 'Mortimer', 'Balthasar',
            'Caspian', 'Bartholomew', 'Basil', 'Rudyard', 'Gerald', 'Reginald',
            'Crofton', 'Charles', 'Archibald', 'Blake', 'Casper', 'Edgar',
            'Elias', 'Elwin', 'Horace', 'Ignatius', 'Julius', 'Lucius',
            'Maurice', 'Quinn', 'Raleigh', 'Wilbur', 'Xavier', 'Alfred',
            'Kermit', 'Leopold'
        ], 'female': [
            'Agatha', 'Agnes', 'Edith', 'Gertrude', 'Guinevere', 'Mabel',
            'Ophelia', 'Salome', 'Beatrice', 'Millicent', 'Mable', 'Vera',
            'Penelope', 'Matilda', 'Aurelia', 'Euphemia', 'Lillith', 'Ethel',
            'Mildred', 'Ada', 'Nettie', 'Minerva', 'Aurelia', 'Doris', 'Rowena'
        ]
    }
    SURNAMES = [
        'of Narnia', 'the Conqueror', 'Doe', 'the Third',
        'Safecracker\'s apprentice', 'Gluemaker\'s horse',
        'Knight of the Round', 'the Reliable', 'Lord of Gnats', 'the Pitiful',
        'Closer of Deals', 'the Proud', 'the Passive', 'Binman\'s apprentice',
        'the Passive', 'of the North', 'Soler\'s soulmate', 'Test Subject 042',
        ('Haberdasher\'s son', 'Haberdasher\'s daughter'),
        'Wielder of Crowbars'
    ]
    # if dist, speed is in pixels per day
    # else time is in days
    METHODS = {
        'phone': {'dist': False, 'time': 3, 'freq': 5},
        'in person': {'dist': True, 'speed': 10, 'freq': 10},
        'e-mail': {'dist': False, 'time': 1.5, 'freq': 2},
        'fax': {'dist': False, 'time': 4, 'freq': 1},
        'mail': {'dist': True, 'speed': 15, 'freq': 8},
        'carrier pigeon': {'dist': True, 'speed': 20, 'freq': 1},
        'message in a bottle': {'dist': True, 'speed': 5, 'freq': 5},
        'telepathy': {'dist': False, 'time': 1, 'freq': .5},
        'beacon': {'dist': True, 'speed': 15, 'freq': 3},
        'drums': {'dist': True, 'speed': 15, 'freq': 4},
        'radio': {'dist': False, 'time': 6, 'freq': 6},
        'pager': {'dist': False, 'time': 2, 'freq': 2},
        'newspaper crossword': {'dist': False, 'time': 14, 'freq': 1},
        'skywriting': {'dist': False, 'time': 7, 'freq': .5},
        'telegraph': {'dist': False, 'time': 7, 'freq': 3}
    }
    # type: 'c' (connection), 'p' (person) or 'a' (area); area type requires
    #       radius in pixels
    # time: triangular distribution (min, mean, max) in days
    # news *: {text: freq} or tuple of texts for equal freqs; can contain %p/%P
    #         for person, %a for area
    # news_start can contain %t for time, %r for time range
    ACTIONS = [
        {
            'desc': 'hire a mugger',
            'type': 'p',
            'cost': 15,
            'affects': ('in person',),
            'time': (2, 3, 5),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'cut phone line',
            'type': 'c',
            'cost': 25,
            'affects': ('phone', 'fax', 'telegraph'),
            'time': (5, 7, 10),
            'news start': (
None,
#'An engineer will be sent to fix reported telephone outages.  Job time ' \
#'estimate: %t.',
            ), 'news end': (
None,
            )
        }, {
            'desc': 'broadcast jamming signal',
            'type': 'a',
            'radius': 100,
            'cost': 100,
            'affects': ('telepathy', 'radio', 'pager'),
            'time': (4, 6, 7),
            'news start': (
None,
#'Disruptions to wireless services have been detected in %a.  We expect to ' \
#'find the source in %r.',
            ), 'news end': (
None,
            )
        }, {
            'desc': 'send virus to computer',
            'type': 'p',
            'cost': 35,
            'affects': ('e-mail', 'fax'),
            'time': (7, 8, 10),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'shoot down a pigeon',
            'type': 'c',
            'cost': 45,
            'affects': ('carrier pigeon',),
            'time': (10, 12, 14),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'bribe newspaper editor not to include crossword message',
            'type': 'c',
            'cost': 30,
            'affects': ('newspaper crossword',),
            'time': (6, 7, 8),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'cause fog',
            'type': 'a',
            'radius': 150,
            'cost': 60,
            'affects': ('beacon',),
            'time': (2, 4, 6),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'play a loud sound',
            'type': 'a',
            'radius': 80,
            'cost': 50,
            'affects': ('message in a bottle', 'drums'),
            'time': (1, 3, 4),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'order a hit',
            'type': 'p',
            'cost': 250,
            'affects': METHODS.keys(),
            'time': (10, 14, 21),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'cause a storm',
            'type': 'a',
            'radius': 150,
            'cost': 250,
            'affects': ('phone', 'fax', 'carrier pigeon', 'beacon',
                        'telegraph'),
            'time': (3, 4, 7),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'cause an earthquake',
            'type': 'a',
            'radius': 200,
            'cost': 800,
            'affects': METHODS.keys(),
            'time': (5, 10, 14),
            'news start': (
None,
            ), 'news end': (
None,
            )
        }, {
            'desc': 'incite a riot',
            'type': 'a',
            'radius': 100,
            'cost': 250,
            'affects': ('in person', 'mail', 'carrier pigeon', 'beacon',
                        'drums', 'newspaper crossword'),
            'time': (4, 6, 8),
            'news start': (
None,
            ), 'news end': (
None,
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
