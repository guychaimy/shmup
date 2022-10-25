# Schump game
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 <http://creativecommons.org/licenses/by/3.0/>
# Art from Kenney.nl

import sys
import pygame
import random
import os

WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TME = 5000

# Define usefull colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 25)
YELLOW = (255, 255, 0)

# set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')

# initiate the pygame model
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shmup!')
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')


# Draw text on surface
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# Add new mob to the game when one is destroied
def new_mob():
    m = Mob()
    all_sprits.add(m)
    mobs.add(m)


# Draw the progress bar for the shield
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# A class of sprite for the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.original_image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        # Unhide if hidden
        now = pygame.time.get_ticks()
        if self.hidden and now - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        # timeout the powerup
        if player.power >= 2 and pygame.time.get_ticks() - player.power_timer > POWERUP_TME:
            player.power -= 1
            player.power_timer = pygame.time.get_ticks()

        # Control the left/right movement of the player
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        # Keeps shooting as long as the space-bar is pressed
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_timer = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprits.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprits.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# A class of sprite for the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = random.choice(meteor_images)
        self.original_image.set_colorkey(BLACK)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.original_image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedx = random.randrange(-3, 3)
        self.speedy = random.randrange(1, 8)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


# A class of sprite for the bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        #  kill it if
        if self.rect.bottom < 0:
            self.kill()


# Power up for the player
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_list[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        #  kill it if
        if self.rect.top > HEIGHT:
            self.kill()


# A class of sprite an explosion when ever a mob hit by bullet
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[size][0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

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


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHUMP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys to move, Space-bar to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen,"Press a key to begin", 18,WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                pygame.quit()
            # use arrow keys for control
            elif event.type == pygame.KEYUP:
                waiting = False


# load game graphics
background = pygame.image.load(os.path.join(img_folder, 'starfield.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_folder, 'playerShip1_orange.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 25))
player_mini_img.set_colorkey(BLACK)
# meteor_img = pygame.image.load(os.path.join(img_folder, 'meteorBrown_med1.png')).convert()
laser_img = pygame.image.load(os.path.join(img_folder, 'laserRed16.png')).convert()
meteor_images = []
meteors_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png',
                'meteorBrown_small1.png', 'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
for img in meteors_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())

# load explosion files
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['player'].append(img_lg)

powerup_list = {}
powerup_list['shield'] = pygame.image.load(os.path.join(img_folder, 'shield_gold.png')).convert()
powerup_list['gun'] = pygame.image.load(os.path.join(img_folder, 'bolt_gold.png')).convert()

# Load Game sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'Laser_Shoot4.wav'))
shield_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'shmup_snd_pow4.wav'))
power_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'shmup_snd_pow5.wav'))
player_expl = pygame.mixer.Sound(os.path.join(snd_folder, 'rumble1.ogg'))
exp_son_sounds = []
exp_list = ['Explosion1.wav', 'Explosion2.wav']
for exp in exp_list:
    exp_son_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, exp)))
pygame.mixer.music.load(os.path.join(snd_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)  # loop the music indefinitely

# Game loop
running = True
game_over = True

while running:
    if game_over:
        show_go_screen()
        game_over = False
        # Groups for the game
        all_sprits = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprits.add(player)
        # Adding 8 mobs  to the game. The total amount of mobs simultaneously.
        for i in range(8):
            new_mob()

        score = 0
    # Keep the running at the right speed
    clock.tick(FPS)
    # process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            pygame.quit()
        # use arrow keys for control
        elif event.type == pygame.KEYDOWN:
            # exit the game when ESCAPE is pressed
            if event.key == pygame.K_ESCAPE:
                running = False

    # update screen
    all_sprits.update()

    # Check if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(exp_son_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprits.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprits.add(pow)
            powerups.add(pow)
        new_mob()

    # Check if the player hit a powerups
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            shield_sound.play()
            if player.shield > 100:
                player.shield = 100
        elif hit.type == 'gun':
            player.powerup()
            power_sound.play()

    # check to see if the mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprits.add(expl)
        new_mob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprits.add(death_explosion)
            player_expl.play()
            player.hide()
            player.lives -= 1
            player.shield = 100

    # if the player dies and  the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Drae / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprits.draw(screen)
    draw_text(screen, "your score: " + str(score), 25, WIDTH // 2, 10)
    draw_shield_bar(screen, 8, 8, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    # *After* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
