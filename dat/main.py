import pygame
import sys
from pygame.locals import *
from pygame.math import Vector2

velocity = 0
movement_direction = Vector2(0, 0)

####
menu = True
####
def update(dt):
####
    global velocity, movement_direction, screen, h, w
####
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
########

        if event.type == MOUSEBUTTONDOWN():
            x,y = event.pos
            for button in menu.backgame:
                if button.menu.backgame.collidepoint(x,y):
                    menu.buttonpress()
            
########
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

    ####

    if menu.menuupdate == True:
        menu.menupress(screen)
    else:
        gui.update(screen)

    ####


class background:
    def __init__(self, screen):
        self.screen = screen
        self.mainbacking = pygame.image.load("assets/textures/map.png").convert_alpha()
        self.image = pygame.transform.scale(self.mainbacking, (6000,6000))
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


######################################################################################################

class gui:
    def __init__(self):
        self.hotbar_back = pygame.image.load("assets/textures/placeholdermainentity.png")
        self.hotbar_back = pygame.transform.scale(self.hotbar_back, (500,150))
        self.hotbar_back.bottom = (w//2, h)
        self.cornericon = pygame.image.load("assets/textures/placeholdermainentity.png")
        self.cornericon = pygame.transform.scale(self.cornericon, (w//10,w//10))
        self.cornericon.bottomleft = (0, h)

    def update(self):
        pygame.draw.rect(screen, (138, 138, 138, [30]), self.hotbar_back)
        pygame.draw.rect(screen, (138, 138, 138), self.cornericon, border_top_right_radius=35)
    
class menu:
    def __init__(self):
        self.menuback = pygame.image.load("assets/textures/placeholderbackground.svg")
        self.menuback = pygame.transform.scale(self.menuback, (w,h))
        self.translucent = pygame.rect(w,h)
        self.translucent.center = (w//2,h//2)
        self.backgame = pygame.rect(300,100)
        self.backgame.center = (w//2, h//2)
        self.quit = pygame.rect (300,100)
        self.quit.center = (w//2,h//2 + 150)

    def menupress(self, screen):
        pygame.draw.rect(screen, self.translucent, (232, 232, 232, [50]))
        pygame.draw.rect(screen, self.backgame, (44, 219, 0), border_radius=12)
        pygame.draw.rect(screen, self.quit, (168, 62, 50), border_radius=12)

    def menuupdate(self):
        global menu
        self.keys = pygame.key.get_pressed()
        f = int(self.keys[pygame.K_f])
        if f > 0:
            return False
        elif f < 0:
            menu = True
            return True

    def buttonpress(self):
        global menu
        self.mousepos = pygame.mouse.get_pos()
        if pygame.self.backgame.collidepoint(self.mousepos) == True:
            if menu == True:
                menu = False

    def quitbutton(self):
        global menu
        self.mousepos = pygame.mouse.get_pos()
        if pygame.self.quit.collidepoint(self.mousepos):
            if menu == True:
                pygame.quit()
                sys.exit()

        

############################################################################################################
 
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
####
menu = menu(w, h)
####
dt = 0
while True:
    update(dt)
    draw(screen, backg, entity)
    dt = fpsClock.tick(fps)/1000