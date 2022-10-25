# Pygame template - skelton for a new pygame project
import pygame
import random

WIDTH = 360
HEIGHT = 480
FPS = 30

# Define usefull colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 25)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('My Game')
clock = pygame.time.Clock()

all_sprits = pygame.sprite.Group()

# Game loop
running = True
while running:
    # Keep the running at the right speed
    clock.tick(FPS)
    # process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False



    # update
    all_sprits.update()
    # Drae / render
    screen.fill(BLACK)
    all_sprits.draw(screen)

    # *After* drawing everything, flip the display
    pygame.display.flip()
