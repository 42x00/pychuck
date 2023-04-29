import pygame
from pychuck import *

pygame.init()
screen = pygame.display.set_mode((640, 480))

s = SinOsc(freq=440, gain=.5)
s >= dac

x = 320
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x -= 10
                s.gain -= 0.05
            elif event.key == pygame.K_RIGHT:
                x += 10
                s.gain += 0.05
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (0, 0, 0), (x, 240 + s.last * 200), 30)
    pygame.display.flip()
    now += 800 * samp

pygame.quit()
