import numpy as np
import curses
import time


class Firework(object):
    def __init__(self, fpath, width=10, height=4, nstage=6):
        self.ascii = np.full((nstage, height, width), ' ', dtype='|S1')
        self.nstage = nstage
        self.width = width
        self.height = height
        with open(fpath, 'r') as fh:
            s, h = 0, 0
            for line in fh:
                if line == '\n':
                    s += 1
                    h = 0
                    continue
                w = 0
                for c in line.rstrip():
                    self.ascii[s, h, w] = c
                    w += 1
                h += 1
        self.mask = []
        for i in range(nstage):
            self.mask.append(self.ascii[i] != ' ')
    

class Background(object):
    def __init__(self, fpath, width=60, height=16): 
        self.ascii = np.full((height, width+1), ' ', dtype='|S1')
        self.width = width
        self.height = height
        with open(fpath, 'r') as fh:
            h = 0
            for line in fh:
                w = 0
                for c in line.rstrip():
                    self.ascii[h, w] = c
                    w += 1
                h += 1
        self.ascii[:, -1] = '\n'
    

class Schedule(object):
    def __init__(self, H, loc, nstage):
        self.h = 0 # current top height
        self.stage = 1
        self.nstage = nstage
        self.H = H # height for next stage
        self.loc = loc # left
        self.stop = False
    
    def update(self):
        if self.h < self.H:
            self.h += 1
        elif self.stage < self.nstage:
            self.stage += 1
        else:
            self.stop = True


class Screen(object):
    def __init__(self, nfirework=5):
        self.background = Background('background.txt')
        self.firework = Firework('firework.txt')
        self.nfirework = nfirework
        self.locations = []
        l = int(self.background.width / nfirework)
        loc = max(int(l/2)-int(self.firework.width/2), 1)
        for i in range(nfirework):
            self.locations.append(loc)
            loc += l
        self.minh = self.firework.height + 2 # upper edge
        self.maxh = self.background.height - 1
        self.fireworks = []
        self.schedule = [1] * nfirework
        self.occupy = [False] * nfirework

    def scheduling(self):
        for i in range(self.nfirework):
            if self.schedule[i] == 1 and not self.occupy[i]:
                self.fireworks.append(Schedule(
                    np.random.randint(self.minh, self.maxh+1), 
                    self.locations[i], self.firework.nstage))
                self.occupy[i] = True
        self.schedule = np.random.choice([0, 1], self.nfirework)
        
    def animate(self, window):
        window.addstr(0, 0, self.background.ascii.tostring())
        window.refresh()
        self.scheduling()
        bh = self.background.height
        bw = self.background.width
        fh = self.firework.height
        fw = self.firework.width
        while self.fireworks:
            deletelist = []
            view = np.array(self.background.ascii)
            for i, firework in enumerate(self.fireworks):
                firework.update()
                low = bh - firework.h
                high = min(bh, low + fh)
                left = firework.loc
                right = min(firework.loc + fw, bw)
                mask = self.firework.mask[firework.stage-1][fh-high+low:, :right-left]
                view[low:high, left:right][mask] = self.firework.ascii[firework.stage-1,
                fh-high+low:, :right-left][mask]
                if firework.stop:
                    deletelist.append(i)
                    self.occupy[self.locations.index(firework.loc)] = False
            window.addstr(0, 0, view.tostring())
            window.refresh()
            time.sleep(0.1)
            self.fireworks = [f for i, f in enumerate(self.fireworks) if i not in deletelist]
            self.scheduling()


screen = Screen()
curses.wrapper(screen.animate)


