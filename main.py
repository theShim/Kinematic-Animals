import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import sys

from scripts.animals.lizard import Lizard
from scripts.animals.snake import Snake
from scripts.animals.fish import Fish

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io

    ##############################################################################################

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode(SIZE, flags)
        self.clock = pygame.time.Clock()
        self.running = True

        #the actual animals just comment them out as needed
        self.animals = pygame.sprite.Group()
        # Snake(self, [self.animals])
        Snake(self, [self.animals], anchor_pos=vec(100, HEIGHT * 0.75), angle_constraint_flag=True)
        Fish(self, [self.animals])
        Fish(self, [self.animals], ai=True)
        Lizard(self, [self.animals], scale=0.5)

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
        pygame.mixer.init()

        pygame.event.set_blocked(None) #setting allowed events to reduce lag
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

    def run(self):
        if DEBUG:
            PROFILER = cProfile.Profile()
            PROFILER.enable()

        last_time = pygame.time.get_ticks()
        while self.running:
            #deltatime
            self.dt = (current_time := pygame.time.get_ticks()) - last_time
            self.dt /= 1000
            last_time = current_time
            
            self.handle_events()
                    
            self.screen.fill((20, 20, 20))
            self.animals.update()


            if DEBUG:
                debug_info = f"FPS: {int(self.clock.get_fps())}"
                pygame.display.set_caption(f"{WINDOW_TITLE} | {debug_info}")

            pygame.display.update()
            self.clock.tick(FPS)

        if DEBUG:
            PROFILER.disable()
            PROFILER.dump_stats("test.stats")
            pstats.Stats("test.stats", stream=(s:=io.StringIO())).sort_stats((sortby:=pstats.SortKey.CUMULATIVE)).print_stats()
            print(s.getvalue())

        pygame.quit()
        sys.exit()
    

    ##############################################################################################

if __name__ == "__main__":
    game = Game()
    game.run()