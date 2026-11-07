import pygame
import sys
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
from pygame._sdl2.video import Window

basewidth = 1920
baseheight = 1080
velocity = 0
movement_direction = Vector2(0, 0)
menu_open = True
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "textures"
fullscreen = False
fpsstart = 0
framecount = 0
starttime = pygame.time.get_ticks()
display_fps = 0

def fpsmonitor():
    global framecount, starttime, display_fps
    currenttime = pygame.time.get_ticks()
    elapsed_time = currenttime - starttime
    framecount += 1

    if elapsed_time > 1000:
        display_fps = framecount / (elapsed_time / 1000.0)
        starttime = currenttime
        framecount = 0

    fpstext = tinyfont.render("FPS: {:.2f}".format(display_fps), True, (0, 255, 0), (0, 0, 0, 50))
    fpstext_rect = fpstext.get_rect(topright=(w, 0))
    screen.blit(fpstext, fpstext_rect)

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

                resizelayout()

                screen = window.get_surface()
                backg.screen = screen
                entity.screen = screen
                
        if event.type == MOUSEBUTTONDOWN and menu_open:
            menu.buttonpress(event.pos)
            menu.quitbutton(event.pos)

        if event.type in (VIDEORESIZE, getattr(pygame, "WINDOWRESIZED", -1)):
            resizelayout()

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
        self.map_size = 6000
        self.scale = 1.0
        self.image = pygame.transform.scale(self.mainbacking, (self.map_size, self.map_size))
        self.backpos = Vector2(0, 0)      
        self.viewport_size = screen.get_size()

    def resize(self, scale):
        old_scale = self.scale
        self.scale = max(0.01, scale)

        ratio = self.scale / old_scale
        old_center = Vector2(self.viewport_size) / 2
        new_center = Vector2(w, h) / 2

        self.backpos = new_center - (old_center - self.backpos) * ratio
        self.viewport_size = (w, h)

        mapsize = round(self.map_size * self.scale)
        self.image = pygame.transform.scale(self.mainbacking, (mapsize, mapsize))

    def update(self):
        self.screen.blit(self.image, (self.backpos.x,self.backpos.y))

    

    def playermove(self,w,a,s,d, movement):
        self.backpos -= movement * self.scale

class entity:
    def __init__(self, screen, w, h):
        self.screen = screen

        self.source_sprites = {
            "stand": pygame.image.load(ASSET_DIR / "placeholdermainentity.png").convert_alpha(),
            "w": pygame.image.load(ASSET_DIR / "placeholdermainentityup.png").convert_alpha(),
            "s": pygame.image.load(ASSET_DIR / "placeholdermainentitydown.png").convert_alpha(),
            "a": pygame.image.load(ASSET_DIR / "placeholdermainentityleft.png").convert_alpha(),
            "d": pygame.image.load(ASSET_DIR / "placeholdermainentityright.png").convert_alpha()
        }

        self.sprites = {}
        for direction, sprite in self.source_sprites.items():
            self.sprites[direction] = pygame.transform.scale(sprite, (200, 200))

        self.mainentpos = Vector2(w//2 - 100, h//2 - 100)
        self.direction = "stand"

    def resize(self,w,h,scale):
        size = max(1, round(200*scale))

        for direction, sprite in self.source_sprites.items():
            self.sprites[direction] = pygame.transform.scale(sprite, (size, size))
        self.mainentpos = Vector2(w//2-size//2,h//2-size//2)

    def move(self, direction):
        self.direction = direction

    def stand(self):
        self.direction = "stand"

    def draw(self):
        self.screen.blit(self.sprites[self.direction],self.mainentpos)

class gui:
    def __init__(self):

        self.hotbar = pygame.Rect((0, 0, 700,150))
        self.hotbar.midbottom = (w//2,h)
        self.cornericon = pygame.Rect(0, 0, w // 10, w // 10)
        self.cornericon.bottomleft = (0, h)
        self.sideicons = pygame.Rect(0, 0, 100, 500)
        self.sideicons.midright = (w, h // 2)

    def update(self):
        pygame.draw.rect(screen, (60, 60, 60), self.hotbar, border_radius=8)
        pygame.draw.rect(screen, (90, 140, 90), self.cornericon,border_radius=8, border_top_right_radius=30)        
        pygame.draw.rect(screen, (80, 80, 80), self.sideicons, border_radius=8)

    def resize(self, w, h, scale):
        self.hotbar.size = (round(700 * scale), round(150 * scale))
        self.hotbar.midbottom = (w // 2, h)
        icon_size = round(192 * scale)
        self.cornericon.size = (icon_size, icon_size)
        self.cornericon.bottomleft = (0, h)
        self.sideicons.size = (round(100 * scale), round(500 * scale))
        self.sideicons.midright = (w, h // 2)

    def hotbar(self):
        self.hotbar1 = pygame.rect ((0, 0, ))

class menu:
    def __init__(self):
        self.translucent = pygame.Surface((w, h), pygame.SRCALPHA)
        self.translucent.fill((232, 232, 232, 50))
        self.backgame = pygame.Rect(0, 0, 300, 100)
        self.backgame.center = (w // 2, h // 2)
        self.backgame_text = pygame.font.Font(None, 32).render("Continue", True, (255,255,255))
        self.backgame_text_rect = self.backgame_text.get_rect()
        self.backgame_text_rect.center = self.backgame.center
        self.quit = pygame.Rect(0, 0, 300, 100)
        self.quit.center = (w // 2, h // 2 + 150)
        self.quit_text = pygame.font.Font(None, 32).render("Quit", True, (255,255,255))
        self.quit_text_rect = self.quit_text.get_rect()
        self.quit_text_rect.center = self.quit.center
        self.guiicon = pygame.Surface((w,h))
        
    def resize(self, w, h, scale):
        buttonwidth = round(300 * scale)
        buttonheight = round(100 * scale)
        font_size = max(1, round(32 * scale))

        self.translucent = pygame.Surface((w, h), pygame.SRCALPHA)
        self.translucent.fill((232,232,232,50))

        self.backgame.size = (buttonwidth, buttonheight)
        self.backgame.center = (w // 2, h // 2)

        self.quit.size = (buttonwidth, buttonheight)
        self.quit.center = (w//2, h//2 + round(150 * scale))

        font = pygame.font.Font(None, font_size)

        self.backgame_text = font.render("Continue", True, (255,255,255))
        self.backgame_text_rect = self.backgame_text.get_rect(center = self.backgame.center)

        self.quit_text = font.render("Quit", True, (255, 255, 255))
        self.quit_text_rect = self.quit_text.get_rect(center = self.quit.center)

    def menupress(self, screen):
        screen.blit(self.translucent, (0, 0))
        pygame.draw.rect(screen, (44, 219, 0), self.backgame, border_radius=12)
        screen.blit(self.backgame_text, self.backgame_text_rect)
        pygame.draw.rect(screen, (168, 62, 50), self.quit, border_radius=12)
        screen.blit(self.quit_text, self.quit_text_rect)

    def buttonpress(self, mousepos):
        global menu_open
        if self.backgame.collidepoint(mousepos):
            menu_open = False

    def quitbutton(self, mousepos):
        if self.quit.collidepoint(mousepos):
            pygame.quit()
            sys.exit()

def resizelayout():
    global screen, w, h
    screen = window.get_surface()
    w, h = screen.get_size()

    scale  = min(w/basewidth, h/baseheight)

    backg.resize(scale)
    entity.resize(w, h, scale)
    gui.resize(w,h, scale)
    menu.resize(w, h,scale)

    backg.screen = screen
    entity.screen = screen
 
def draw(window, screen, backg, entity):
    screen = window.get_surface()

    backg.screen = screen
    entity.screen = screen

    screen.fill((110, 168, 67))
    backg.update()
    entity.draw()

    if menu_open:
        menu.menupress(screen)
    else:
        gui.update()

    fpsmonitor()
    window.flip()


pygame.init()

window = Window("Experimental release", size = (1920,1090), resizable=True,)

window.maximize()
screen = window.get_surface()
w,h = screen.get_size()

fps = 60.0
fpsClock = pygame.time.Clock()

font = pygame.font.SysFont('freesans', 32)
tinyfont = pygame.font.SysFont('freesans', 10)

backg = background(screen)
entity = entity(screen, w, h)
menu = menu()
gui = gui()

dt = 0
while True:
    update(dt)
    draw(window, screen, backg, entity)
    dt = fpsClock.tick(fps)/1000