import numpy as np
import pygame
from physics import CelestialBody, gravity

W = 1200 #This is the dimension of our window
H = 800

class Camera:
    def __init__(self):
        self.zoom = 1e-9
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = 0
    
    def to_screen(self, x_real, y_real):
        X_pixel = (x_real * self.zoom) + self.offset_x + (W / 2)
        Y_pixel = - (y_real * self.zoom) + self.offset_y + (H / 2)
        return X_pixel , Y_pixel
    
    def to_world (self, x_pixel, y_pixel):
        X_real = (x_pixel - self.offset_x - (W/2)) / self.zoom
        Y_real = -((y_pixel - self.offset_y - (H/2))) / self.zoom

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    camera = Camera()
    sun = CelestialBody("Sun", 1.989e30, 0, 0, 0, 0)
    earth = CelestialBody("Earth", 5.97e24, 1.496e11, 0, 0, 29780)
    dt = 86400
    tot_days = 365
    gravity(earth, sun)
    running = True
    step = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

        screen.fill((0, 0, 0))        
        earth.update_position(dt)
        next_ax, next_ay =  gravity(earth, sun)
        earth.update_velocity(next_ax, next_ay, dt)
        sun_pixel_x, sun_pixel_y = camera.to_screen(sun.x, sun.y)
        earth_pixel_x, earth_pixel_y = camera.to_screen(earth.x, earth.y)

        pygame.draw.circle(screen, (255, 215, 0), (int(sun_pixel_x), int(sun_pixel_y)), 15)
        pygame.draw.circle(screen, (100, 149, 237), (int(earth_pixel_x), int(earth_pixel_y)), 6)

        pygame.display.flip()

        clock.tick(60)

        if step % 30 == 0:
            distanza = np.sqrt(earth.x**2 + earth.y**2)
            print(f"Giorno: {step:<4} | Posizione: ({earth.x/1e9:6.2f}e9, {earth.y/1e9:6.2f}e9) m | Distanza dal Sole: {distanza/1e9:6.2f}e9 m")
            
        step += 1

pygame.quit()

if __name__ == "__main__":
    run_simulation()
