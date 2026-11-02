import pygame
import sys
from pygame.locals import *
from pygame.math import Vector2

velocity = 0

def update(dt):
    global velocity
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
        velocity += 0.1
        if velocity > 3:
            velocity = 3
    else:
        velocity -= 0.3
        if velocity < 0:
            velocity = 0
    if velocity > 0 and keys[pygame.K_w]:
        backg.playermove(True, False, False, False, velocity * (dt/16.67))
    if velocity > 0 and keys[pygame.K_s]:
        backg.playermove(False, False, True, False, velocity * (dt/16.67))
    if velocity > 0 and keys[pygame.K_a]:
        backg.playermove(False, True, False, False, velocity * (dt/16.67))
    if velocity > 0 and keys[pygame.K_d]:
        backg.playermove(False, False, False, True, velocity * (dt/16.67))

class background:
    def __init__(self, screen):
        self.screen = screen
        self.mainbacking = pygame.image.load("assets/textures/placeholderbackground.svg").convert_alpha()
        self.image = pygame.transform.scale(self.mainbacking, (1000,1000))
        self.backpos = Vector2(0, 0)      

    def update(self):
        screen.blit(self.image, (self.backpos.x,self.backpos.y))

    def playermove(self,w,a,s,d, velocity):
        if w:
            self.backpos.y += velocity
        if s:
            self.backpos.y -= velocity
        if a:
            self.backpos.x += velocity
        if d:
            self.backpos.x -= velocity

def draw(screen, backg):
    screen.fill((189, 214, 255))
    backg.update()
    pygame.display.flip()


pygame.init()
fps = 60.0
fpsClock = pygame.time.Clock()

h = int(pygame.display.Info().current_h)
w = int(pygame.display.Info().current_w)
screen = pygame.display.set_mode((w,h))

backg = background(screen)

dt = 1/fps
while True:
    update(dt)
    draw(screen, backg)
    dt = fpsClock.tick(fps)