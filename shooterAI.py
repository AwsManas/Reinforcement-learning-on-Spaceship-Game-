import pygame
import random
import os
import constants as constants
from datetime import datetime
from collections import deque

######## Globals ##########
action = 'idle'
all_sprites = pygame.sprite.Group()
Bull = pygame.sprite.Group()
#########################


def draw_text(surfacee, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('comic'), size)
    text_surface = font.render(text, True, constants.Yellow)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surfacee.blit(text_surface, text_rect)


def draw_health(surface, x, y, health):
    if health < 0:
        health = 0
    height = 5
    lenght = constants.WIDTH
    fill = (health/100) * lenght
    outerrect = pygame.Rect(x, y, lenght, height)
    innerrect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, constants.red, outerrect)
    pygame.draw.rect(surface, constants.green, innerrect)


def draw_lives(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 20*i
        img_rect.y = y
        surface.blit(img, img_rect)


def getaction(act):
    if act == [1, 0, 0, 0]:
        return 'move_left'
    elif act == [0, 1, 0, 0]:
        return 'move_right'
    elif act == [0, 0, 1, 0]:
        return 'fire'
    elif act == [0, 0, 0, 1]:
        return 'idle'


class battleship(pygame.sprite.Sprite):
    def __init__(self, ship_img, laser_img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(ship_img, (60, 60))
        self.image.set_colorkey(constants.black)
        self.rect = self.image.get_rect()
        self.radius = 29
        self.rect.centerx = constants.WIDTH/2
        self.rect.bottom = constants.HEIGHT-10
        self.speedx = 0
        self.speedy = 0
        self.health = constants.SHIP_HEALTH
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = pygame.time.get_ticks()
        self.laser_img = laser_img

    def update(self):
        if self.power_level >= 2 and pygame.time.get_ticks() - self.power_timer > constants.Power2xMS:
            self.power_level -= 1
            self.power_timer = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > constants.HiddenMS:
            self.hidden = False
            self.rect.centerx = constants.WIDTH/2
            self.rect.bottom = constants.HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        global action
        if action == 'move_left':
            self.speedx = -constants.Ship_speed
        elif action == 'move_right':
            self.speedx = constants.Ship_speed
        if self.rect.right >= constants.WIDTH:
            self.rect.right = constants.WIDTH - 1
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.x += self.speedx

    def shoot(self):
        if self.power_level == 1:
            bullet = bullets(self.rect.centerx, self.rect.top, self.laser_img)
            global all_sprites
            global Bull
            all_sprites.add(bullet)
            Bull.add(bullet)
            # shoot_sound.play()
        if self.power_level >= 2:
            bullet1 = bullets(self.rect.centerx-25,
                              self.rect.top-20, self.laser_img)
            bullet2 = bullets(self.rect.centerx+25,
                              self.rect.top-20, self.laser_img)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            Bull.add(bullet1)
            Bull.add(bullet2)
            # shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (constants.WIDTH/2, constants.HEIGHT+200)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self, asteroid_images):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.transform.scale(
            random.choice(asteroid_images), (30, 30))
        self.image_orig.set_colorkey(constants.black)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = 15
        self.rect.x = random.randrange(0, constants.WIDTH-self.rect.width)
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
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > constants.HEIGHT + 20:
            global missed_meteroids
            missed_meteroids += 1
        if self.rect.top > constants.HEIGHT + 20 or self.rect.left < -20 or self.rect.right > constants.WIDTH + 20:
            self.rect.x = random.randrange(0, constants.WIDTH-self.rect.width)
            self.rect.y = random.randrange(-140, -40)
            self.speedy = random.randrange(1, constants.MAX_VERTICAL_SPEED)
            self.speedx = random.randrange(-constants.MAX_HORIZONTAL_SPEED,
                                           constants.MAX_HORIZONTAL_SPEED+1)


class bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, laser_img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img, (5, 10))
        self.image.set_colorkey(constants.black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -constants.BULLET_SPEED

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class explo(pygame.sprite.Sprite):
    def __init__(self, center, size, explosion_anim):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.explosion_anim = explosion_anim

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center, power_img):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['gun', 'health'])
        self.image = power_img[self.type]
        self.image.set_colorkey(constants.black)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = constants.POWER_SPEED

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > constants.HEIGHT:
            self.kill()


class SpaceshipAI:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (constants.WIDTH, constants.HEIGHT))
        pygame.display.set_caption("HueHue:)")
        self.clock = pygame.time.Clock()
        game_folder = os.path.dirname(__file__)
        img_folder = os.path.join(game_folder, "shooter-graphics")
        self.background = pygame.image.load(
            os.path.join(img_folder, "back.png")).convert()
        self.background_rect = self.background.get_rect()
        self.ship_img = pygame.image.load(
            os.path.join(img_folder, "ship.png")).convert()
        self.ship_tag = pygame.transform.scale(self.ship_img, (15, 15))
        self.ship_tag.set_colorkey(constants.black)
        self.laser_img = pygame.image.load(
            os.path.join(img_folder, "ebullet1.png")).convert()
        self.asteroid_images = []
        asteroid_list = ["ast1.png", "ast2.png", "ast3.png", "ast4.png"]
        for img in asteroid_list:
            self.asteroid_images.append(pygame.image.load(
                os.path.join(img_folder, img)).convert())
        self.power_img = {}
        self.power_img['gun'] = pygame.image.load(
            os.path.join(img_folder, 'bolt_gold.png')).convert()
        self.power_img['health'] = pygame.image.load(
            os.path.join(img_folder, 'pill_green.png')).convert()
        self.explosion_anim = {}
        self.explosion_anim['lar'] = []
        self.explosion_anim['sml'] = []
        self.explosion_anim['player'] = []
        for i in range(9):
            filename = 'regularExplosion0'+str(i)+'.png'
            img = pygame.image.load(os.path.join(
                img_folder, filename)).convert()
            img.set_colorkey(constants.black)
            img_lr = pygame.transform.scale(img, (60, 60))
            img_sm = pygame.transform.scale(img, (30, 30))
            self.explosion_anim['lar'].append(img_lr)
            self.explosion_anim['sml'].append(img_sm)
            filename = 'sonicExplosion0'+str(i)+'.png'
            img = pygame.image.load(os.path.join(
                img_folder, filename)).convert()
            img.set_colorkey(constants.black)
            img_tr = pygame.transform.scale(img, (100, 100))
            self.explosion_anim['player'].append(img_tr)
        self.font_name = pygame.font.match_font('comic')
        self.actions_list = [[1, 0, 0, 0], [
            0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        self.reset_game()

    def reset_game(self):
        self.firstTime = False
        self.time_ = datetime.now()
        self.game_over = False
        self.death_explo = False
        global missed_meteroids
        missed_meteroids = 0
        self.destroyed = False
        global all_sprites
        global Bull
        all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        Bull = pygame.sprite.Group()
        self.PWups = pygame.sprite.Group()
        self.ship = battleship(self.ship_img, self.laser_img)
        all_sprites.add(self.ship)
        for i in range(constants.MAX_METEROIDS):
            m = Mob(self.asteroid_images)
            self.mobs.add(m)
            all_sprites.add(m)
        self.points = constants.INITPOINTS
        self.last_5_moves = deque(maxlen=5)
        self.last_5_moves.append(1)
        self.last_5_moves.append(2)
        self.last_5_moves.append(3)
        self.last_5_moves.append(4)
        self.last_5_moves.append(5)

    def get_states(self):
        states_to_return = []
        states_to_return.append(self.ship.rect.centerx)
        states_to_return.append(self.ship.health)
        ship_pwr_lvl = self.ship.power_level
        if ship_pwr_lvl >= 2:
            ship_pwr_lvl = 2
        states_to_return.append(ship_pwr_lvl)
        states_to_return.append(self.points)
        left = 0
        right = 0
        center = 0
        for met in self.mobs:
            if met.rect.centerx//5 == self.ship.rect.centerx//5:
                center = 1
            elif met.rect.centerx//5 > self.ship.rect.centerx//5:
                right += 1
            else:
                left += 1
        states_to_return.extend((left, center, right))

        is_bull = -1
        global Bull
        for one_b in Bull:
            x = one_b.rect.centerx//5
            x = min(x, 79)
            x = max(x, 0)
            y = one_b.rect.bottom

            if x == self.ship.rect.centerx//5 and y > is_bull:
                is_bull = y
        states_to_return.append(is_bull)

        power_ret = [-100, -100, -100, -100]
        for p in self.PWups:
            if p.type == 'gun':
                if p.rect.y > power_ret[1]:
                    power_ret[0] = p.rect.x
                    power_ret[1] = p.rect.y
            elif p.type == 'health':
                if p.rect.y > power_ret[3]:
                    power_ret[2] = p.rect.x
                    power_ret[3] = p.rect.y
        states_to_return.extend(power_ret)
        return states_to_return

    def play_step(self, act):
        self.clock.tick(constants.FPS)
        global action
        action = getaction(act)
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()

        if action == 'fire':
            self.ship.shoot()
            self.points -= constants.SHOOT_POINTS
            if self.points < 1:
                self.game_over = True

        all_sprites.update()
        global missed_meteroids
        global Bull
        self.points -= constants.MISSPENALTY*missed_meteroids
        missed_meteroids = 0
        if self.points < 1:
            self.game_over = True

        hits = pygame.sprite.groupcollide(self.mobs, Bull, True, True)
        for hit in hits:
            self.points += constants.HIT_POINTS
            if random.random() > 0.9:
                Pow = Power(hit.rect.center, self.power_img)
                all_sprites.add(Pow)
                self.PWups.add(Pow)

            expl = explo(hit.rect.center, 'lar', self.explosion_anim)
            all_sprites.add(expl)
            m = Mob(self.asteroid_images)
            all_sprites.add(m)
            self.mobs.add(m)
            self.destroyed = True

        hits = pygame.sprite.spritecollide(
            self.ship, self.mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            m = Mob(self.asteroid_images)
            all_sprites.add(m)
            self.mobs.add(m)
            self.ship.health -= constants.COLLISION_DAMAGE
            if not self.ship.health < 1:
                expl = explo(hit.rect.center, 'sml', self.explosion_anim)
                all_sprites.add(expl)
            if self.ship.health < 1:
                self.death_explo = explo(self.ship.rect.center,
                                         'player', self.explosion_anim)
                all_sprites.add(self.death_explo)
                self.ship.hide()
                self.ship.lives -= 1
                self.ship.health = constants.SHIP_HEALTH
            self.destroyed = True

        hits = pygame.sprite.spritecollide(self.ship, self.PWups, True)
        for hit in hits:  # gun,live
            if hit.type == 'health':
                self.ship.health += random.randrange(constants.HEALTH_MIN,
                                                     constants.HEALTH_MAX)
            if self.ship.health > 100:
                self.ship.health = 100
            elif hit.type == 'gun':
                self.ship.powerup()

        if self.ship.lives == 0 and not self.death_explo.alive():
            self.game_over = True
        self.screen.fill(constants.white)
        self.screen.blit(self.background, self.background_rect)
        all_sprites.draw(self.screen)
        draw_text(self.screen, str(self.points), 20, constants.WIDTH/2, 20)
        draw_health(self.screen, 0, constants.HEIGHT-7, self.ship.health)
        draw_lives(self.screen, constants.WIDTH-75,
                   5, self.ship.lives, self.ship_tag)

        reward = 0
        if self.destroyed:
            reward = 10
            self.destroyed = False
        if self.game_over == True:
            reward = -10

        self.last_5_moves.append(act)
        cnt = 0
        for i in range(5):
            if self.last_5_moves[i] == act:
                cnt += 1
        if cnt == 5:
            reward = 0

        pygame.display.flip()
        self.score = (datetime.now() - self.time_).total_seconds()
        return reward, self.game_over, self.score


# choices = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
# _ = SpaceshipAI()
# i = 0
# while True:
#     _.play_step(random.choice(choices))
#     if i % 1000 == 0:
#         sts = _.get_states()
#         print(sts)
#         print(len(sts))
#     i += 1
