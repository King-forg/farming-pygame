import pygame
import sys
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
from pygame._sdl2.video import Window


velocity = 0
movement_direction = Vector2(0, 0)
menu_open = True
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "textures"
fullscreen = False


def update(dt):
    global velocity, movement_direction, menu_open
    global fullscreen, screen

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_f:
                menu_open = not menu_open
            if event.key == K_F11:
                if fullscreen:
                    window.set_windowed()
                    fullscreen = False
                else:
                    window.set_fullscreen()
                    fullscreen = True

                screen = window.get_surface()
                backg.screen = screen
                entity.screen = screen
                
        if event.type == MOUSEBUTTONDOWN and menu_open:
            menu.buttonpress(event.pos)
            menu.quitbutton(event.pos)

    if menu_open:
        return
            
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
        self.mainbacking = pygame.image.load(ASSET_DIR / "Map.png").convert_alpha()
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
            "stand": pygame.image.load(ASSET_DIR / "placeholdermainentity.png").convert_alpha(),
            "w": pygame.image.load(ASSET_DIR / "placeholdermainentityup.png").convert_alpha(),
            "s": pygame.image.load(ASSET_DIR / "placeholdermainentitydown.png").convert_alpha(),
            "a": pygame.image.load(ASSET_DIR / "placeholdermainentityleft.png").convert_alpha(),
            "d": pygame.image.load(ASSET_DIR / "placeholdermainentityright.png").convert_alpha()
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


class gui:
    def __init__(self):
        self.hotbar_back = pygame.image.load(ASSET_DIR / "placeholdermainentity.png")
        self.hotbar_back = pygame.transform.scale(self.hotbar_back, (700,150))
        self.hotbar_back_rect = self.hotbar_back.get_rect(midbottom = (w//2,h))
        self.cornericon = pygame.image.load(ASSET_DIR / "placeholdermainentity.png")
        self.cornericon = pygame.transform.scale(self.cornericon, (w//10,w//10))
        self.cornericon_rect = self.cornericon.get_rect(bottomleft = (0,h))
        self.sideicons = pygame.image.load(ASSET_DIR / "placeholdermainentity.png")
        self.sideicons = pygame.transform.scale(self.sideicons, (100,500))
        self.sideicons_rect = self.sideicon.get_rect(midright = (w,h//2))

    def update(self):
        screen.blit(self.hotbar_back, self.hotbar_back_rect)
        screen.blit(self.cornericon, self.cornericon_rect)
        screen.blit(self.sideicons, self.sideicons_rect)

class menu:
    def __init__(self):
        self.translucent = pygame.Surface((w, h), pygame.SRCALPHA)
        self.translucent.fill((232, 232, 232, 50))
        self.backgame = pygame.Rect(0, 0, 300, 100)
        self.backgame.center = (w // 2, h // 2)
        self.backgame_text = pygame.font.render("Continue", True, (255,255,255))
        self.backgame_text_rect = self.backgame_text.get_rect()
        self.backgame_text_rect.center = self.backgame.center
        self.quit = pygame.Rect(0, 0, 300, 100)
        self.quit.center = (w // 2, h // 2 + 150)
        self.guiicon = pygame.Surface(w,h)

    def menupress(self, screen):
        screen.blit(self.translucent, (0, 0))
        pygame.draw.rect(screen, (44, 219, 0), self.backgame, border_radius=12)
        pygame.blit(self.backgame_text, self.backgame_text_rect)
        pygame.draw.rect(screen, (168, 62, 50), self.quit, border_radius=12)

    def buttonpress(self, mousepos):
        global menu_open
        if self.backgame.collidepoint(mousepos):
            menu_open = False

    def quitbutton(self, mousepos):
        if self.quit.collidepoint(mousepos):
            pygame.quit()
            sys.exit()

        
 
def draw(window, screen, backg, entity):
    screen = window.get_surface()

    backg.screen = screen
    entity.screen = screen

    screen.fill((189, 214, 255))
    backg.update()
    entity.draw()

    if menu_open:
        menu.menupress(screen)
    else:
        gui.update()

    window.flip()


pygame.init()

window = Window("Experimental release", size = (1920,1090), resizable=True,)

window.maximize()
screen = window.get_surface()
w,h = screen.get_size()


fps = 60.0
fpsClock = pygame.time.Clock()

normal = pygame.font.Font('freesansbold.ttf', 32)

backg = background(screen)
entity = entity(screen, w, h)
menu = menu()
gui = gui()

dt = 0
while True:
    update(dt)
    draw(window, screen, backg, entity)
    dt = fpsClock.tick(fps)/1000