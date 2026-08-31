import numpy as np
import pygame
import math
from physics import CelestialBody, gravity, deque
from pre_simulation import pre_simulation
from scenarios import get_scenario
from spaceship import data_collection
W = 1200 #This is the dimension of our window
H = 800

class Camera:
    def __init__(self):
        self.zoom = 1e-9
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.pause = False
    
    def to_screen(self, x_real, y_real):
        X_pixel = (x_real * self.zoom) + self.offset_x + (W / 2)
        Y_pixel = - (y_real * self.zoom) + self.offset_y + (H / 2)
        return X_pixel , Y_pixel
    
    def to_world (self, x_pixel, y_pixel):
        X_real = (x_pixel - self.offset_x - (W/2)) / self.zoom
        Y_real = -((y_pixel - self.offset_y - (H/2))) / self.zoom
        return X_real, Y_real
    
    def to_zoom(self, factor, mouse_pos):
        x_real, y_real = self.to_world(mouse_pos[0], mouse_pos[1])
        self.zoom *= factor
        
        self.offset_x = mouse_pos[0] - (x_real * self.zoom) - (W / 2)
        self.offset_y = mouse_pos[1] - (-y_real * self.zoom) - (H / 2)


def run_simulation():
    bodies, dt, sub_steps, warmup_days, ship = get_scenario()
    pygame.init()
    font_dv = pygame.font.SysFont(None, 24)
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    camera = Camera()
    has_moon = any(body.name.lower() == 'moon' for body in bodies)
    
    if has_moon:
        camera.zoom = 5e-7
    else:
        camera.zoom = 1e-9

    dt_small = dt / sub_steps      # Dividiamo il giorno in frazioni più piccole
    running = True
    step = 0
    gravity(bodies)

    if warmup_days > 0:
        pre_simulation(bodies, sub_steps, dt_small, warmup_days)

    time_scale = 1
    while running:

        actual_dt = dt * time_scale
        dt_small = actual_dt / sub_steps 
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    camera.to_zoom(1.15, event.pos)
                elif  event.button == 5:
                    camera.to_zoom(0.85, event.pos)
                elif event.button == 1:
                    camera.dragging = True
                    camera.last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    camera.dragging = False
            elif event.type == pygame.MOUSEMOTION:    
                if camera.dragging == True:
                    dx = event.pos[0] - camera.last_mouse_pos[0]
                    dy = event.pos[1] - camera.last_mouse_pos[1]
                    camera.offset_x += dx
                    camera.offset_y += dy
                    camera.last_mouse_pos = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    camera.pause = not camera.pause
                elif event.key == pygame.K_r:
                    bodies = [b for b in bodies if b.name.lower() != "spaceship"]
                    while True:
                        target_name = input("From which planet do you want to start? ").strip().lower()
                        selected_body = next((b for b in bodies if b.name.lower() == target_name), None)
                        if selected_body:
                            print("\n[RESET] Riconfigurazione della navicella...")
                            ship = data_collection(selected_body)
                            bodies.append(ship)
                            break
                        else:
                            print(f"Planet '{target_name}' not found. Try again.")
                elif event.key == pygame.K_t:  # Rallenta
                    if time_scale <= 0.1:
                        print("the timescale is too low")
                        time_scale = 1
                    else:
                        time_scale = max(0.01, time_scale / 2.0)
                        print(f"Time scale: {time_scale}x")
                elif event.key == pygame.K_y :    # Accelerazione normale
                    if time_scale >= 4.0:
                        print("the time scale is at the maximum")
                        time_scale = 1
                    else:
                        time_scale *= 2.0
                        print(f"Time scale: {time_scale}x")
                elif event.key == pygame.K_u:
                    time_scale = 1
                    print(f"Time scale: {time_scale}x")

        ship = next((b for b in bodies if b.name.lower() == "spaceship"), None)
        if ship is not None:
            target, distance = ship.get_nearest_body(bodies)
            if distance <= target.radius_meters:
                print(f"\n[CRASH] the starship shot {target.name} surface ")
                camera.pause = True
                running = False

        screen.fill((0, 0, 0))  
        if camera.pause == False:

            for _ in range(sub_steps):
                # 1. Fase 1: Aggiorna le posizioni usando l'accelerazione corrente
                for body in bodies:
                    body.update_position(dt_small) 

                # 2. Salva le VECCHIE accelerazioni prima che gravity le azzeri e le sovrascriva
                # Usiamo un dizionario temporaneo o una lista di tuple
                old_accel = {body: (body.ax, body.ay) for body in bodies}

                # 3. Calcola le NUOVE accelerazioni nelle nuove posizioni
                gravity(bodies) 

                if keys[pygame.K_UP]:
                    if ship is not None:
                        ship.apply_thrust(1, dt_small, target)    # 1 = Prograde
                if keys[pygame.K_DOWN]:
                    if ship is not None:
                        ship.apply_thrust(2, dt_small, target)  # 2 = Retrograde
                if keys[pygame.K_RIGHT]:
                    if ship is not None:
                        ship.apply_thrust(3, dt_small, target) # 3 = Radial Out
                if keys[pygame.K_LEFT]:
                    if ship is not None:
                        ship.apply_thrust(4, dt_small, target)  # 4 = Radial In
                

                # 4. Fase 2: Aggiorna le velocità passando le vecchie accelerazioni salvate
                for body in bodies:
                    old_ax, old_ay = old_accel[body]
                    body.update_velocity(old_ax, old_ay, dt_small)

        for body in bodies:
            # Calcola la lunghezza dinamica basata sul valore originale del corpo
            current_max_points = int(body.trail_length / time_scale)
            
            # Aggiorna il maxlen della deque se è cambiato
            if body.trail.maxlen != current_max_points:
                body.trail = deque(body.trail, maxlen=current_max_points)
                
            body.trail.append((body.x, body.y))

            

        # DISEGNO A SCHERMO
        for body in bodies:
            if len(body.trail) > 1:
                pixel_points = [camera.to_screen(pt[0], pt[1]) for pt in body.trail]
                pygame.draw.lines(screen, body.color, False, pixel_points, 1)

            pixel_x, pixel_y = camera.to_screen(body.x, body.y)

            # Gestione della dimensione visiva in base allo zoom
            if body.name.lower() == "spaceship":
                current_radius = 4  # La navicella è sempre un puntino chiaro
            else:
                # Scala il raggio reale in pixel, ma metti dei limiti per evitare che coprano lo schermo
                current_radius = max(2, int(body.radius_meters * camera.zoom))

            if pixel_x is not None and pixel_y is not None:
                pygame.draw.circle(screen, body.color, (int(pixel_x), int(pixel_y)), current_radius)

        ship = next((b for b in bodies if b.name.lower() == "spaceship"), None)
        if ship is not None:
            current_dv = ship.delta_v()  # O ship.get_remaining_deltav() se tieni quel nome
            dv_surface = font_dv.render(f"Delta-V: {current_dv:.1f} m/s", True, (255, 255, 255))
            screen.blit(dv_surface, (20, 20))
        pygame.display.flip()

pygame.quit()

if __name__ == "__main__":
    run_simulation()