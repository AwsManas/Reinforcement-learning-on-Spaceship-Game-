import pygame
import random
import os
import constants as constants
from datetime import datetime
WIDTH = constants.WIDTH
HEIGHT = constants.HEIGHT
FPS = constants.FPS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
Yellow = (255, 255, 0)
green = (0, 255, 0)
""" Initialise pygame and create window"""
pygame.init()
# pygame.mixer.init() # initialise sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HueHue:)")
clock = pygame.time.Clock()
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "shooter-graphics")
# song_folder = os.path.join(game_folder,"sounds")
# Loading all game graphics
background = pygame.image.load(os.path.join(img_folder, "back.png")).convert()
background_rect = background.get_rect()
ship_img = pygame.image.load(os.path.join(img_folder, "ship.png")).convert()
ship_tag = pygame.transform.scale(ship_img, (15, 15))
ship_tag.set_colorkey(black)
laser_img = pygame.image.load(os.path.join(
    img_folder, "ebullet1.png")).convert()
asteroid_images = []
asteroid_list = ["ast1.png", "ast2.png", "ast3.png", "ast4.png"]
for img in asteroid_list:
    asteroid_images.append(pygame.image.load(
        os.path.join(img_folder, img)).convert())
power_img = {}
power_img['gun'] = pygame.image.load(
    os.path.join(img_folder, 'bolt_gold.png')).convert()
power_img['health'] = pygame.image.load(
    os.path.join(img_folder, 'pill_green.png')).convert()

# DELETE THE BELOW THING
power_img['live'] = pygame.image.load(os.path.join(
    img_folder, 'powerupRed_star.png')).convert()
# Loading sounds
# shoot_sound = pygame.mixer.Sound(os.path.join(song_folder,"bf.wav"))
# explo_sound = pygame.mixer.Sound(os.path.join(song_folder,'explosion.wav'))
# background_sound = pygame.mixer.music.load(os.path.join(song_folder,'bck.wav'))
# power_sound = pygame.mixer.Sound(os.path.join(song_folder,"sfx_zap.ogg"))
# pygame.mixer.music.set_volume(0.3)
# player_die_sound = pygame.mixer.Sound(os.path.join(song_folder,'shipdes.ogg'))
explosion_anim = {}
explosion_anim['lar'] = []
explosion_anim['sml'] = []
explosion_anim['player'] = []

missed_meteroids = 0
for i in range(9):
    filename = 'regularExplosion0'+str(i)+'.png'
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(black)
    img_lr = pygame.transform.scale(img, (60, 60))
    img_sm = pygame.transform.scale(img, (30, 30))
    explosion_anim['lar'].append(img_lr)
    explosion_anim['sml'].append(img_sm)
    filename = 'sonicExplosion0'+str(i)+'.png'
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(black)
    img_tr = pygame.transform.scale(img, (100, 100))
    explosion_anim['player'].append(img_tr)


class battleship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.image.load(os.path.join(img_folder,"battleship.jpg")).convert()
        self.image = pygame.transform.scale(
            ship_img, (60, 60))  # pygame.Surface((30,40))
        self.image.set_colorkey(black)
        # self.image.fill(red)
        self.rect = self.image.get_rect()
        self.radius = 29
        # pygame.draw.circle(self.image,red,self.rect.center,self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 0
        self.speedy = 0
        self.health = constants.SHIP_HEALTH
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.power_level >= 2 and pygame.time.get_ticks() - self.power_timer > constants.Power2xMS:
            self.power_level -= 1
            self.power_timer = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > constants.HiddenMS:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        global action
        if action == 'move_left':
            self.speedx = -constants.Ship_speed
        elif action == 'move_right':
            self.speedx = constants.Ship_speed
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH - 1
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.x += self.speedx

    def shoot(self):
        if self.power_level == 1:
            bullet = bullets(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            Bull.add(bullet)
            # shoot_sound.play()
        if self.power_level >= 2:
            bullet1 = bullets(self.rect.centerx-25, self.rect.top-20)
            bullet2 = bullets(self.rect.centerx+25, self.rect.top-20)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            Bull.add(bullet1)
            Bull.add(bullet2)
            # shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+200)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.transform.scale(random.choice(
            asteroid_images), (30, 30))  # pygame.Surface((20,20))
        self.image_orig.set_colorkey(black)
        self.image = self.image_orig.copy()
        # self.image.fill(black)
        self.rect = self.image.get_rect()
        self.radius = 15
        # pygame.draw.circle(self.image,red,self.rect.center,self.radius)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rot = 0
        self.rotspeed = random.randrange(-10, 10)
        self.rect.y = random.randrange(-140, -40)
        self.speedy = random.randrange(1, constants.MAX_VERTICAL_SPEED)
        self.speedx = random.randrange(-constants.MAX_HORIZONTAL_SPEED,
                                       constants.MAX_HORIZONTAL_SPEED+1)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 60:
            self.last_update = now
            self.rot = (self.rot + self.rotspeed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center  # rotating by center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 20:
            global missed_meteroids
            missed_meteroids += 1
        if self.rect.top > HEIGHT + 20 or self.rect.left < -20 or self.rect.right > WIDTH+20:
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-140, -40)
            self.speedy = random.randrange(1, constants.MAX_VERTICAL_SPEED)
            self.speedx = random.randrange(-constants.MAX_HORIZONTAL_SPEED,
                                           constants.MAX_HORIZONTAL_SPEED+1)


class bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            laser_img, (5, 10))  # pygame.Surface((5,8))
        # self.image.fill((0,100,0))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -constants.BULLET_SPEED

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class explo(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['gun', 'health'])
        self.image = power_img[self.type]
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = constants.POWER_SPEED

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


font_name = pygame.font.match_font('comic')


def draw_text(surfacee, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, Yellow)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surfacee.blit(text_surface, text_rect)


def draw_health(surface, x, y, health):
    if health < 0:
        health = 0
    height = 5
    lenght = WIDTH
    fill = (health/100) * lenght
    outerrect = pygame.Rect(x, y, lenght, height)
    innerrect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, red, outerrect)
    pygame.draw.rect(surface, green, innerrect)


def draw_lives(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 20*i
        img_rect.y = y
        surface.blit(img, img_rect)


def first_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'Hue Hue Hue', 25, WIDTH/2, HEIGHT/5)
    draw_text(screen, 'SpaceShip!', 50, WIDTH/2, 2*HEIGHT/5)
    draw_text(screen, 'Arrow Key - Left/Right  : Space - Shoot',
              25, WIDTH/2, 4*HEIGHT/5)
    draw_text(screen, 'Press any key to continue...', 20, WIDTH/2, HEIGHT-20)
    pygame.display.flip()
    wait = True
    while wait:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                wait = False


# Game loop
# pygame.mixer.music.play(loops=-1)

running = True
game_over = True
firsttime = True
time_ = ''


def reset_game():
    firsttime = False
    time_ = datetime.now()
    game_over = False
    missed_meteroids = 0
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    Bull = pygame.sprite.Group()
    PWups = pygame.sprite.Group()
    ship = battleship()
    all_sprites.add(ship)
    for i in range(constants.MAX_METEROIDS):
        m = Mob()
        mobs.add(m)
        all_sprites.add(m)
    points = 10


frame_iteration = 0
actions_list = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def getaction(act):
    if act == [1, 0, 0, 0]:
        return 'move_left'
    elif act == [0, 1, 0, 0]:
        return 'move_right'
    elif act == [0, 0, 1, 0]:
        return 'fire'
    elif act == [0, 0, 0, 1]:
        return 'idle'


action = 'idle'
while running:
    if game_over:
        if not firsttime:
            with open('scores.txt', 'a') as f:
                f.write(str((datetime.now() - time_).total_seconds()))
                f.write('\n')
                f.close()
        # first_screen()
        firsttime = False
        time_ = datetime.now()
        game_over = False
        missed_meteroids = 0
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        Bull = pygame.sprite.Group()
        PWups = pygame.sprite.Group()
        ship = battleship()
        all_sprites.add(ship)
        for i in range(constants.MAX_METEROIDS):
            m = Mob()
            mobs.add(m)
            all_sprites.add(m)
        points = constants.INITPOINTS
    clock.tick(FPS)
    # Events
    act = random.choice(actions_list)  # TODO
    action = getaction(act)
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False

    if action == 'fire':
        ship.shoot()
        points -= constants.SHOOT_POINTS
        if points < 1:
            game_over = True

    all_sprites.update()

    points -= constants.MISSPENALTY*missed_meteroids
    missed_meteroids = 0

    if points < 1:
        game_over = True

    # check  collision
    destroyed = False
    hits = pygame.sprite.groupcollide(mobs, Bull, True, True)
    for hit in hits:
        points += constants.HIT_POINTS
        if random.random() > 0.9:
            Pow = Power(hit.rect.center)
            all_sprites.add(Pow)
            PWups.add(Pow)
        # explo_sound.play()
        expl = explo(hit.rect.center, 'lar')
        all_sprites.add(expl)
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
        destroyed = True

    hits = pygame.sprite.spritecollide(
        ship, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
        ship.health -= constants.COLLISION_DAMAGE
        if not ship.health < 1:
            # explo_sound.play()
            expl = explo(hit.rect.center, 'sml')
            all_sprites.add(expl)
        if ship.health < 1:
            # player_die_sound.play()
            death_explo = explo(ship.rect.center, 'player')
            all_sprites.add(death_explo)
            ship.hide()
            ship.lives -= 1
            ship.health = constants.SHIP_HEALTH
        destroyed = True

    hits = pygame.sprite.spritecollide(ship, PWups, True)
    for hit in hits:  # gun,live
        # power_sound.play()
        if hit.type == 'health':
            ship.health += random.randrange(constants.HEALTH_MIN,
                                            constants.HEALTH_MAX)
            if ship.health > 100:
                ship.health = 100
        elif hit.type == 'live':
            ship.lives += 1
        elif hit.type == 'gun':
            ship.powerup()
    if ship.lives == 0 and not death_explo.alive():
        game_over = True
    screen.fill(white)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(points), 20, WIDTH/2, 20)
    draw_health(screen, 0, HEIGHT-7, ship.health)
    draw_lives(screen, WIDTH-75, 5, ship.lives, ship_tag)

    reward = 1
    if destroyed:
        reward = 10
        destroyed = False
    if game_over and not firsttime:
        reward = -10

    # Reward to be extracted from here

    # Draw where?
    pygame.display.flip()
pygame.quit()
