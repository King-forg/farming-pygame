import pygame
import sys
from pygame.locals import *

pygame.init()

fps = 60
fpsClock = pygame.time.Clock()

w, h = 1920, 1080
screen = pygame.display.set_mode((w,h))

while True:
    screen.fill((0,0,0))

    for events in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        #update

        #draw

        pygame.display.flip()
        fpsClock.tick(fps)
        


