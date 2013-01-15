from wmap import Map


class Level (object):
    def __init__ (self, game, event_handler):
        self.game = game
        self.init()

    def init (self):
        self.wmap = Map((702, 600))
        self.wmap.bg = self.game.img('bg.png')
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
        return self.wmap.draw(screen, (149, 0))
