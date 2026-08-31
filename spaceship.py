import math
from physics import CelestialBody
G = 6.6743e-11
class SpaceShip(CelestialBody):
    def __init__(self, name, mass_without_propellent, mass_propellent, x, y, vx, vy, color, radius, trail_length, thrust, specific_impulse, radius_meters = 10):
        # Inizializza i parametri ereditati da CelestialBody (la massa iniziale è vuota + propellente)
        total_mass = mass_without_propellent + mass_propellent
        super().__init__(name, total_mass, x, y, vx, vy, color, radius, trail_length, radius_meters=radius_meters)
        
        # Proprietà specifiche della navicella
        self.mass_without_propellent = mass_without_propellent
        self.mass_propellent = mass_propellent
        self.initial_mass_propellent = mass_propellent
        self.thrust = thrust                    # Spinta massima in Newton
        self.specific_impulse = specific_impulse  # Impulso specifico in secondi (es. 300-450s)
        self.initial_mass = total_mass

    def get_nearest_body(self, bodies):
        nearest_body = None
        min_distance = float('inf')

        for body in bodies:
            if body == self:
                continue
            
            dx = self.x - body.x
            dy = self.y - body.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < min_distance:
                min_distance = distance
                nearest_body = body

        return nearest_body, min_distance

    def apply_thrust(self, direction, dt_small, target_body):
        if self.mass_propellent > 0:
            # L'accelerazione generata dai motori in questo istante
            engine_accel = self.thrust / self.mass
            
            # Calcolo dei versori in base alla direzione scelta
            if direction == 1: #prograde
                velocity = math.sqrt((self.vx ** 2) + (self.vy ** 2))
                if velocity > 0:
                    versor_x, versor_y = self.vx / velocity, self.vy / velocity
                else:
                    versor_x, versor_y = 0, 0

            elif direction == 2: #retrograde
                velocity = math.sqrt((self.vx ** 2) + (self.vy ** 2))
                if velocity > 0:
                    versor_x, versor_y = - (self.vx / velocity), - (self.vy / velocity)
                else:
                    versor_x, versor_y = 0, 0

            elif direction == 3: #radial out
                dx = self.x - target_body.x
                dy = self.y - target_body.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    versor_x, versor_y = dx / distance, dy / distance
                else:
                    versor_x, versor_y = 0, 0

            elif direction == 4: #radial in
                dx = self.x - target_body.x
                dy = self.y - target_body.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    versor_x, versor_y = - (dx / distance), - (dy / distance)
                else:
                    versor_x, versor_y = 0, 0

            # AGGIUNTA DELLA SPINTA ALLE ACCELERAZIONI (ax, ay)
            # Nel metodo Verlet, aggiungiamo la spinta direttamente all'accelerazione 
            # generata dalla gravità calcolata da gravity(bodies)!
            self.ax += versor_x * engine_accel
            self.ay += versor_y * engine_accel

            # Consumo di propellente e aggiornamento della massa totale del corpo
            dm = (self.thrust / (self.specific_impulse * 9.81)) * dt_small
            self.mass_propellent = max(0.0, self.mass_propellent - dm)
            self.mass = self.mass_without_propellent + self.mass_propellent
    def delta_v(self):
        # Evitiamo divisioni per zero o logaritmi non validi se la massa scende troppo
        if self.mass <= 0 or self.initial_mass <= self.mass_without_propellent:
            return 0.0
        
        g0 = 9.80665  # Accelerazione di gravità standard a livello del mare
        Dv = self.specific_impulse * g0 * math.log( self.mass / self.mass_without_propellent)
        return Dv

def data_collection(target_body):
    print("\n--- SPACESHIP CONFIGURATION ---")
    while True:
        try:
            mass_empty = float(input("Insert the empty mass of your ship (kg): "))
            mass_prop = float(input("Insert the initial propellent mass (kg): "))
            isp = float(input("Insert the specific impulse (seconds, e.g. 300): "))
            thrust = float(input("Insert the maximum thrust of your engine (Newton): "))
            altitude_km = float(input("Insert the altitude above the surface of your object (km): "))
            break
        except ValueError:
            print("Error: Insert a valid numeric number.")

    # Distanza dal centro del corpo
    r = target_body.radius_meters + (altitude_km * 1000.0)
    
    # Posizione iniziale (a destra del pianeta)
    ship_x = target_body.x + r
    ship_y = target_body.y
    
    # Velocità orbitale circolare teorica
    v_circ = math.sqrt((G * target_body.mass) / r)
    
    # La navicella eredita la velocità del pianeta e aggiunge la velocità orbitale perpendicolare (asse Y)
    ship_vx = target_body.vx
    ship_vy = target_body.vy - v_circ # Oppure +v_circ a seconda del verso, solitamente -v_circ per antiorario

    ship = SpaceShip(
        name="Spaceship",
        mass_without_propellent=mass_empty,
        mass_propellent=mass_prop,
        x=ship_x,
        y=ship_y,
        vx=ship_vx,
        vy=ship_vy,
        color=(255, 255, 255),
        radius=3,             # Raggio visivo piccolo per non sgranare
        trail_length=1000,
        thrust=thrust,
        specific_impulse=isp,
        radius_meters=10.0,
    )
    
    print("Navicella configurata e inserita in orbita con successo!\n")
    return ship

