import numpy as np
import pygame
from physics import CelestialBody, gravity
from pre_simulation import load_snapshot, get_simulation_state, save_snapshot

SNAPSHOT_FILE = "orbital_data.npy"
W = 1200 #This is the dimension of our window
H = 800
SUN     = (255, 215, 0)    # Gold
MERCURY = (169, 169, 169)  # Dark Gray
VENUS   = (224, 192, 144)  # Beige/Sand
EARTH   = (100, 149, 237)  # Cornflower Blue
MARS    = (193, 68, 14)    # Rust Red
JUPITER = (218, 165, 32)   # Golden Rod
SATURN  = (238, 232, 170)  # Pale Golden Rod
URANUS  = (175, 238, 238)  # Pale Turquoise
NEPTUNE = (65, 105, 225)   # Royal Blue

class Camera:
    def __init__(self):
        self.zoom = 1e-9
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
    
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
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    camera = Camera()
    sun     = CelestialBody("Sun", 1.989e30, 0, 0, 0, 0, SUN, 16, trail_length=1)
    mercury = CelestialBody("Mercury", 3.301e23, 5.791e10, 0, 0, 47870, MERCURY, 4, trail_length=88)
    venus   = CelestialBody("Venus", 4.867e24, 1.082e11, 0, 0, 35020, VENUS, 6, trail_length=225)
    earth   = CelestialBody("Earth", 5.972e24, 1.496e11, 0, 0, 29780, EARTH, 6, trail_length=365)
    mars    = CelestialBody("Mars", 6.417e23, 2.279e11, 0, 0, 24070, MARS, 5, trail_length=687)
    
    # --- I GIGANTI GASSOSI (Richiedono molti più punti) ---
    jupiter = CelestialBody("Jupiter", 1.898e27, 7.785e11, 0, 0, 13070, JUPITER, 12, trail_length=4333)   # ~12 anni
    saturn  = CelestialBody("Saturn", 5.683e26, 1.434e12, 0, 0, 9680, SATURN, 10, trail_length=10759)   # ~29 anni
    uranus  = CelestialBody("Uranus", 8.681e25, 2.871e12, 0, 0, 6800, URANUS, 8, trail_length=30687)    # ~84 anni
    neptune = CelestialBody("Neptune", 1.024e26, 4.495e12, 0, 0, 5430, NEPTUNE, 8, trail_length=60190)  # ~165 anni

    bodies = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

    dt = 86400
    sub_steps = 200                 # Più è alto, più la fisica è precisa (40 è perfetto per Mercurio)
    dt_small = dt / sub_steps      # Dividiamo il giorno in frazioni più piccole
    running = True
    step = 0
    gravity(bodies)
    save_counter = 0

    verification = load_snapshot(bodies, dt, SNAPSHOT_FILE)
    if not verification:
        print("File non trovato o non valido. Inizio warm-up del sistema (60.190 giorni)...")
        giorni_warmup = 60190
        
        # Inizializziamo un contatore per mostrare il progresso
        progress_step = 5000 
        
        for giorno in range(1, giorni_warmup + 1):
            # 1. Calcolo fisico (Verlet)
            for _ in range(sub_steps):
                # Aggiorna posizioni
                for body in bodies:
                    body.update_position(dt_small)
                
                # Salva accelerazioni correnti
                old_accel = {body: (body.ax, body.ay) for body in bodies}
                
                # Calcola nuove accelerazioni basate sulle nuove posizioni
                gravity(bodies)
                
                # Aggiorna velocità
                for body in bodies:
                    body.update_velocity(old_accel[body][0], old_accel[body][1], dt_small)
            
            # 2. Registra la posizione nel trail dopo ogni giorno simulato
            for body in bodies:
                body.trail.append((body.x, body.y))
            
            # 3. Feedback a console (per non stare a guardare lo schermo nero)
            if giorno % progress_step == 0:
                print(f"Warm-up in corso: {giorno}/{giorni_warmup} giorni calcolati...")

        # 4. Salva lo stato finale dopo il warm-up
        print("Warm-up completato. Salvataggio snapshot...")
        snapshot = get_simulation_state(bodies, dt)
        save_snapshot(snapshot, SNAPSHOT_FILE)
        print("Sistema inizializzato con successo!")
    else:
        print("Snapshot caricato correttamente. Orbite pronte!")

    while running:
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

        save_counter += 1

        if save_counter % 10000 == 0:
            print(f"Salvataggio automatico allo step {save_counter}")
            snapshot = get_simulation_state(bodies, dt)
            save_snapshot(snapshot, SNAPSHOT_FILE)

        screen.fill((0, 0, 0))  

        for _ in range(sub_steps):
            # 1. Fase 1: Aggiorna le posizioni usando l'accelerazione corrente
            for body in bodies:
                body.update_position(dt_small) 

            # 2. Salva le VECCHIE accelerazioni prima che gravity le azzeri e le sovrascriva
            # Usiamo un dizionario temporaneo o una lista di tuple
            old_accel = {body: (body.ax, body.ay) for body in bodies}

            # 3. Calcola le NUOVE accelerazioni nelle nuove posizioni
            gravity(bodies) 

            # 4. Fase 2: Aggiorna le velocità passando le vecchie accelerazioni salvate
            for body in bodies:
                old_ax, old_ay = old_accel[body]
                body.update_velocity(old_ax, old_ay, dt_small)

        for body in bodies:
            body.trail.append((body.x, body.y))
        
        for body in bodies:
            if body.name != 'sun':
                if len(body.trail) > 1:
                    pixel_points = [camera.to_screen(pt[0], pt[1]) for pt in body.trail]
                    pygame.draw.lines(screen, body.color, False, pixel_points, 2)

                pixel_x, pixel_y = camera.to_screen(body.x, body.y)
                pygame.draw.circle(screen, body.color, (int(pixel_x), int(pixel_y)), body.radius)

        pygame.display.flip()

        clock.tick(60)

        if step % 30 == 0:
            distanza = np.sqrt(mercury.x**2 + mercury.y**2)
            print(f"Giorno: {step:<4} | Posizione: ({mercury.x/1e9:6.2f}e9, {mercury.y/1e9:6.2f}e9) m | Distanza dal Sole: {distanza/1e9:6.2f}e9 m")
            
        step += 1

pygame.quit()

if __name__ == "__main__":
    run_simulation()
