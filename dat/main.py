import pygame
import sys
from pygame.locals import *
from pygame.math import Vector2

velocity = 0
movement_direction = Vector2(0, 0)

def update(dt):
    global velocity, movement_direction
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()

    running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    if running:
        max_velocity = 350
        acceleration = 1200
    else:
        max_velocity = 270
        acceleration = 600

    dx = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    dy = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

    input_direction = Vector2(dx, dy)

    if input_direction.length() > 0:
        velocity += acceleration * dt
        velocity = min(velocity, max_velocity)

        movement_direction = input_direction.normalize()

        if dx < 0:
            entity.move("a")
        elif dx > 0:
            entity.move("d")
        elif dy < 0:
            entity.move("w")
        elif dy > 0:
            entity.move("s")

    else:
        velocity -= 1700 * dt
        velocity = max (velocity, 0)

    if velocity > 0:
        movement = movement_direction * velocity * dt
        backg.playermove(False, False, False, False, movement)
    else:
        entity.stand()



class background:
    def __init__(self, screen):
        self.screen = screen
        self.mainbacking = pygame.image.load("assets/textures/placeholderbackground.svg").convert_alpha()
        self.image = pygame.transform.scale(self.mainbacking, (1000,1000))
        self.backpos = Vector2(0, 0)      

    def update(self):
        screen.blit(self.image, (self.backpos.x,self.backpos.y))

    def playermove(self,w,a,s,d, movement):
        self.backpos.x -= movement.x
        self.backpos.y -= movement.y

class entity:
    def __init__(self, screen, w, h):
        self.screen = screen

        self.sprites = {
            "stand": pygame.image.load("assets/textures/placeholdermainentity.png").convert_alpha(),
            "w": pygame.image.load("assets/textures/placeholdermainentityup.png").convert_alpha(),
            "s": pygame.image.load("assets/textures/placeholdermainentitydown.png").convert_alpha(),
            "a": pygame.image.load("assets/textures/placeholdermainentityleft.png").convert_alpha(),
            "d": pygame.image.load("assets/textures/placeholdermainentityright.png").convert_alpha()
        }

        for direction in self.sprites:
            self.sprites[direction] = pygame.transform.scale(self.sprites[direction], (200,200))

        self.mainentpos = Vector2(w//2 - 50, h//2 - 50)
        self.direction = "stand"

    def move(self, direction):
        self.direction = direction

    def stand(self):
        self.direction = "stand"

    def draw(self):
        self.screen.blit(self.sprites[self.direction],self.mainentpos)
 
def draw(screen, backg, entity):
    screen.fill((189, 214, 255))
    backg.update()
    entity.draw()
    pygame.display.flip()


pygame.init()
fps = 60.0
fpsClock = pygame.time.Clock()

h = int(pygame.display.Info().current_h)
w = int(pygame.display.Info().current_w)
screen = pygame.display.set_mode((w,h))

backg = background(screen)
entity = entity(screen, w, h)

dt = 0
while True:
    update(dt)
    draw(screen, backg, entity)
    dt = fpsClock.tick(fps)/1000