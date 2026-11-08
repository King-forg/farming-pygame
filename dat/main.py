import pygame
import sys
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
from pygame._sdl2.video import Window
import pytmx


basewidth = 1920
baseheight = 1080
mapscale = 7.5
spritesize = 100
velocity = 0
movement_direction = Vector2(0, 0)
menu_open = True
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "textures"
fullscreen = False
fpsstart = 0
framecount = 0
starttime = pygame.time.get_ticks()
displayfps = 0
collisions = []


def fpsmonitor():
    global framecount, starttime, displayfps
    currenttime = pygame.time.get_ticks()
    elapsed_time = currenttime - starttime
    framecount += 1

    if elapsed_time > 1000:
        displayfps = framecount / (elapsed_time / 1000.0)
        starttime = currenttime
        framecount = 0

    fpstext = tinyfont.render("FPS: {:.2f}".format(displayfps), True, (0, 255, 0), (0, 0, 0, 50))
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
        max_velocity = 87.5
        acceleration = 1200
    else:
        max_velocity = 43.75
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
        player_world = backg.getplayerworldpos(entity.hitbox.center)

        newworld_x = player_world + Vector2(movement.x, 0)

        newhitbox_x = entity.hitbox.copy()
        newhitbox_x.center = (round(newworld_x.x),round(newworld_x.y))

        if not backg.checkcollision(newhitbox_x):
            backg.playermove(False, False, False, False, Vector2(movement.x,0))

        player_world = backg.getplayerworldpos(entity.hitbox.center)

        newworld_y = player_world + Vector2(0, movement.y)

        newhitbox_y = entity.hitbox.copy()
        newhitbox_y.center = (round(newworld_y.x), round(newworld_y.y))

        if not backg.checkcollision(newhitbox_y):
            backg.playermove(False, False, False, False, Vector2(0, movement.y))
    else:
        entity.stand()

class background:

    chunksize = 512

    def __init__(self, screen):
        self.screen = screen
        mappath = Path(__file__).resolve().parent / "farmrpg assets" / "map2.tmx"
        self.tmx = pytmx.load_pygame(str(mappath))
        self.collisions = []

        collisionlayer = self.tmx.get_layer_by_name("Collisions")

        for obj in collisionlayer:
            if obj.width > 0 and obj.height > 0:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.collisions.append(rect)
        print(f"Loaded {len(self.collisions)} collision rects")

        print("First collision:", self.collisions[0])
        print("Tile size:", self.tmx.tilewidth, self.tmx.tileheight)
        self.scale = mapscale
        print("Map scale:", self.scale)

        self.backpos = Vector2(
            w / 2 - 1590 * self.scale,
            h / 2 - 1920 * self.scale
        )
        self.viewport_size = screen.get_size()

        self.chunks = {}
        self.scaledtiles = {}

        for layer_index in self.tmx.visible_tile_layers:
            layer = self.tmx.layers[layer_index]

            if not isinstance(layer, pytmx.TiledTileLayer):
                continue

            for x, y , image in layer.tiles():

                world_x = x * self.tmx.tilewidth
                world_y = y * self.tmx.tileheight

                chunkx = world_x // self.chunksize
                chunky = world_y // self.chunksize

                key = (chunkx, chunky)

                self.chunks.setdefault(key, []).append( (world_x, world_y, image, layer_index))

        print(f"Loaded all {len(self.chunks)} chunks")
        self.updatetilecache()

    def updatetilecache(self):
        self.scaledtiles.clear()

        for tiles in self.chunks.values():
            for x, y, image, layer in tiles:
                image_id = id(image)

                if image_id not in self.scaledtiles:
                    tile_width = max(1, round(image.get_width() * self.scale))
                    tile_height = max(1, round(image.get_height() * self.scale))

                    scaledimage = pygame.transform.scale(image, (tile_width, tile_height))

                    self.scaledtiles[image_id] = scaledimage

    def checkcollision(self, player_rect):
        for wall in self.collisions:
            if player_rect.colliderect(wall):
                return True
        return False

    def getplayerworldpos(self, screen_pos):
        return Vector2((screen_pos[0] - self.backpos.x) / self.scale, (screen_pos[1] - self.backpos.y) / self.scale) 

    def resize(self, scale):
        old_scale = self.scale
        self.scale = max(0.01, mapscale * scale)
        self.updatetilecache()

        ratio = self.scale / old_scale

        old_center = Vector2(self.viewport_size) / 2
        new_center = Vector2(w, h) / 2

        self.backpos = new_center - (old_center - self.backpos) * ratio
        self.viewport_size = (w, h)

    def update(self, above_player=False):
        left = -self.backpos.x / self.scale
        top = -self.backpos.y / self.scale

        right = left + w / self.scale
        bottom = top + h / self.scale

        min_x = int(left // self.chunksize)
        max_x = int(right // self.chunksize)
        min_y = int(top // self.chunksize)
        max_y = int(bottom // self.chunksize)

        for cx in range(min_x, max_x + 1):
            for cy in range(min_y, max_y + 1):
                for x, y, image, layer in self.chunks.get((cx, cy), []):
                    isaboveplayer = (self.tmx.layers[layer].name in ("Top","Fence"))

                    if isaboveplayer != above_player:
                        continue
                    scaled_x = round(x * self.scale + self.backpos.x)
                    scaled_y = round(y * self.scale + self.backpos.y)
                    scaledimage = self.scaledtiles[id(image)]
                    self.screen.blit(scaledimage, (scaled_x, scaled_y))
    

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
            self.sprites[direction] = pygame.transform.scale(sprite, (spritesize, spritesize))

        self.mainentpos = Vector2(w//2 - 100, h//2 - 100)
        self.direction = "stand"

        self.hitbox = pygame.Rect(0, 0, 15, 15)
        self.hitbox.center = (round(self.mainentpos.x + self.sprites["stand"].get_width() / 2), round(self.mainentpos.y + self.sprites["stand"].get_height() / 2))


    def resize(self,w,h,scale):
        size = max(1, round(spritesize * scale))

        for direction, sprite in self.source_sprites.items():
            self.sprites[direction] = pygame.transform.scale(sprite, (size, size))
        self.mainentpos = Vector2(w//2-size//2,h//2-size//2)

        self.hitbox.center = (
            round(self.mainentpos.x + size / 2),
            round(self.mainentpos.y + size / 2)
        )

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

        self.slot_count = 8
        self.slot_size = 65
        self.slot_gap = 8

        self.slots = []
        self.createslots()

        self.slotfont = pygame.font.Font(ASSET_DIR / "SmoochSans-VariableFont_wght.ttf", 18)

    def createslots(self):
        self.slots = []

        total_width = (self.slot_count * self.slot_size) + (self.slot_count-1) * self.slot_gap

        start_x = self.hotbar.centerx - total_width // 2

        for i in range (self.slot_count):
            slot = pygame.Rect(start_x + i * (self.slot_size + self.slot_gap), self.hotbar.centery - self.slot_size // 2, self.slot_size, self.slot_size)

            self.slots.append(slot)

        
    def update(self):
        hotbar_surface = pygame.Surface(self.hotbar.size, pygame.SRCALPHA)

        hotbar_surface.fill((0, 0, 0, 0))
        screen.blit(hotbar_surface, self.hotbar)

        pygame.draw.rect(screen, (90, 140, 90), self.cornericon,border_radius=8, border_top_right_radius=30)        
        pygame.draw.rect(screen, (80, 80, 80), self.sideicons, border_radius=8)

        for i, slot in enumerate(self.slots):
            slot_surface = pygame.Surface(slot.size, pygame.SRCALPHA)

            pygame.draw.rect(slot_surface, (35, 35,35, 150), slot_surface.get_rect(), border_radius=8)

            screen.blit(slot_surface, slot)

            pygame.draw.rect(screen, (210, 210, 210, 180), slot, width = 2, border_radius=5)

            number = self.slotfont.render(str(i+1), True, (255,255,255))

            screen.blit(number, (slot.x + 6, slot.y + 4))

    def resize(self, w, h, scale):
        self.hotbar.size = (round(700 * scale), round(150 * scale))
        self.hotbar.midbottom = (w // 2, h)
        icon_size = round(192 * scale)
        self.cornericon.size = (icon_size, icon_size)
        self.cornericon.bottomleft = (0, h)
        self.sideicons.size = (round(100 * scale), round(500 * scale))
        self.sideicons.midright = (w, h // 2)
        self.slot_size = max(1, round(65 * scale))
        self.slot_gap = max(1, round(8 * scale))
        self.createslots()
        self.slotfont = pygame.font.Font(ASSET_DIR / "SmoochSans-VariableFont_wght.ttf", max(1, round(18*scale)))


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
    backg.update(False)
    entity.draw()
    backg.update(True)

    # pygame.draw.rect(screen, (255, 0, 0), entity.hitbox, 2)

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
scale = min(w/ basewidth, h/ baseheight)
backg.resize(scale)
entity = entity(screen, w, h)
menu = menu()
gui = gui()

dt = 0
while True:
    update(dt)
    draw(window, screen, backg, entity)
    dt = fpsClock.tick(fps)/1000