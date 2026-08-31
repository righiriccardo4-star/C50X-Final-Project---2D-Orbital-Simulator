    
from physics import CelestialBody, gravity
def pre_simulation(bodies, sub_steps, dt_small, warmup_days):
    
    print(f"Inizializzazione orbite per {warmup_days} giorni...")
    
    for giorno in range(warmup_days):
        # Fisica (Verlet) per il singolo giorno
        for _ in range(sub_steps):
            # 1. Aggiorna posizioni di tutti i corpi
            for body in bodies:
                body.update_position(dt_small)
            
            # 2. Salva vecchie accelerazioni
            old_accel = {body: (body.ax, body.ay) for body in bodies}
            
            # 3. Calcola nuove accelerazioni (Gravità globale)
            gravity(bodies)
            
            # 4. Aggiorna velocità di tutti i corpi
            for body in bodies:
                old_ax, old_ay = old_accel[body]
                body.update_velocity(old_ax, old_ay, dt_small)
        
        # Dopo aver completato i sub_steps del giorno, registra la posizione
        for body in bodies:
            body.trail.append((body.x, body.y))

    print("Sistema solare inizializzato e orbite caricate!")