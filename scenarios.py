from physics import CelestialBody
from spaceship import data_collection
from collections import deque
import numpy as np
import pygame

SUN     = (255, 215, 0)    # Gold
MERCURY = (169, 169, 169)  # Dark Gray
VENUS   = (224, 192, 144)  # Beige/Sand
EARTH   = (100, 149, 237)  # Cornflower Blue
MARS    = (193, 68, 14)    # Rust Red
JUPITER = (218, 165, 32)   # Golden Rod
SATURN  = (238, 232, 170)  # Pale Golden Rod
URANUS  = (175, 238, 238)  # Pale Turquoise
NEPTUNE = (65, 105, 225)   # Royal Blue
MOON = (239, 237, 211)


def get_scenario():
    sun = CelestialBody("Sun", 1.989e30, 0, 0, 0, 0, SUN, 16, trail_length=1, radius_meters=6.9634e8)
    mercury = CelestialBody("Mercury", 3.301e23, 5.791e10, 0, 0, 47870, MERCURY, 4, trail_length=89, radius_meters=2.4397e6)
    venus = CelestialBody("Venus", 4.867e24, 1.082e11, 0, 0, 35020, VENUS, 6, trail_length=225, radius_meters=6.0518e6)
    earth = CelestialBody("Earth", 5.972e24, 1.496e11, 0, 0, 29780, EARTH, 6, trail_length=365, radius_meters=6.3710e6)
    mars = CelestialBody("Mars", 6.417e23, 2.279e11, 0, 0, 24070, MARS, 5, trail_length=687, radius_meters=3.3895e6)
    jupiter = CelestialBody("Jupiter", 1.898e27, 7.785e11, 0, 0, 13070, JUPITER, 12, trail_length=4333, radius_meters=6.9911e7)   
    saturn = CelestialBody("Saturn", 5.683e26, 1.434e12, 0, 0, 9680, SATURN, 10, trail_length=10759, radius_meters=5.8232e7)   
    uranus = CelestialBody("Uranus", 8.681e25, 2.871e12, 0, 0, 6800, URANUS, 8, trail_length=30687, radius_meters=2.5362e7)    
    neptune = CelestialBody("Neptune", 1.024e26, 4.495e12, 0, 0, 5430, NEPTUNE, 8, trail_length=60190, radius_meters=2.4622e7)
    moon = CelestialBody("Moon", 7.342e22, 3.844e8, 0, 0, 1022, MOON, 12, trail_length=1, radius_meters=1.7374e6)  

    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

    print("\n" + "╔" + "═"*48 + "╗")
    print(f"║ {'ORBITAL SIMULATOR - SCENARIO SELECTOR':^46} ║")
    print("╚" + "═"*48 + "╝")
    print(" [1] ☀️  Inner Solar System    (Fast, up to Jupiter)")
    print(" [2] 🪐 Full Solar System     (Slow, includes outer giants)")
    print(" [3] 🌍 Earth - Moon System   (Close-range dynamics)")
    print(" [4] 🧪 Custom Sandbox        (Create your own bodies)")
    print("-" * 50)
    
    while True:
        choose = input(" Select a mode [1-4]: ").strip()
        if choose in ["1", "2", "3", "4"]:
            break 
        print(" ❌ Invalid choice. Please enter a number between 1 and 4.")

    ship = None

    if choose == "1":
        bodies = planets[0:6]
        dt = 86400                   
        sub_steps = 200
    elif choose == "2":
        bodies = planets
        dt = 86400                   
        sub_steps = 200
    elif choose == "3":
        earth.x, earth.y, earth.vx, earth.vy = 0, 0, 0, 0
        earth.radius = 24
        earth.trail.clear()
        bodies = [earth, moon]
        dt = 60               
        sub_steps = 1000
    else:
        bodies = setup_sandbox_bodies()  
        dt = 86400
        sub_steps = 200

    # Gestione Pre-Simulazione
    if choose in ["1", "2", "3"]:
        do_presim, max_days = Do_Pre_Simulation(bodies)
        warmup_days = max_days if do_presim else 0
    else:
        try:
            revolution_days = int(input("Insert your pre simulation days: "))
        except ValueError:
            revolution_days = 0
        warmup_days = revolution_days

    # Gestione Navicella
    spaceship_choice = input("Do you want to use a spaceship? [Y/N]: ").strip().lower()
    if spaceship_choice in ("yes", "y", "yeah", "sì", "si"):
        while True:
            target_name = input("From which planet do you want to start? ").strip().lower()
            selected_body = next((b for b in bodies if b.name.lower() == target_name), None)
            if selected_body:
                ship = data_collection(selected_body)
                bodies.append(ship)  # AGGIUNTA A TUTTI GLI SCENARI!
                break
            else:
                print(f"Planet '{target_name}' not found. Try again.")

    return bodies, dt, sub_steps, warmup_days, ship

def Do_Pre_Simulation(active_bodies):
    confirmation = "N"
    max_days = max(body.trail_length for body in active_bodies)
    while True:
        confirmation = input(f"Are you sure you want to pre-simulate {max_days} days? The pre-simulation time could be long, especially with a planet whose revolution time is greater than 10000 earth days. [Y/N] ")
        clean_conf = confirmation.strip().lower()
    
        if clean_conf in ("yes", "y", "yeah", "sì", "si"):
            return True, max_days
        elif clean_conf in ("no", "n"):
            return False, 0
        print("Invalid input. Please enter Y or N.")

def setup_sandbox_bodies():
    custom_bodies = []
    while True:
        Input = input("Insert your body name or type exit to exit the sandbox setup: ")
        name = Input.strip().lower()
        if  name == "exit":
            break
        temp = CelestialBody("", 0, 0, 0, 0, 0, 0, 0, trail_length=0)
        temp.name = name
        
        while True:
            try:
                mass = int(input("Insert your body mass "))
                if mass < 0:
                    print("Your body must have mass")
                    continue
                temp.mass = mass
                break
            except ValueError:
                print("Insert a valid mass value")
        
        while True:
            try:
                distance = int(input("Insert the distance from the centre, if the body is the centre just type 0: "))
                if distance < 0:
                    print("Your body must have a positive distance")
                    continue
                temp.x = distance
                break
            except ValueError:
                print("Insert a valid distance value")

        while True:
            try:
                velocity = int(input("Insert the velocity, if the body is the centre just type 0: "))
                if velocity < 0:
                    print("Your body must have a positive and >0 velocity")
                    continue
                temp.vy = velocity
                break
            except ValueError:
                print("Insert a valid velocity value")        
            
        while True:
            try:
                y = int(input("Insert the Y position: "))
                temp.y = y
                break
            except ValueError:
                print("Insert a valid Y position value")

        while True:
            try:
                vx = int(input("Insert the X velocity: "))
                temp.vx = vx
                break
            except ValueError:
                print("Insert a valid X velocity value")

        while True:
            try:
                radius = int(input("Insert the graphical radius (e.g. 4-15): "))
                if radius <= 0:
                    print("Radius must be greater than 0")
                    continue
                temp.radius = radius
                break
            except ValueError:
                print("Insert a valid radius value")

        print("Insert the color (RGB format, values between 0 and 255)")
    
        while True:
            try:
                r = int(input("  Red [0-255]: "))
                g = int(input("  Green [0-255]: "))
                b = int(input("  Blue [0-255]: "))
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    print("Values must be between 0 and 255")
                    continue
                temp.color = (r, g, b)
                break
            except ValueError:
                print("Insert valid integer numbers for RGB")

        while True:
            try:
                trail = int(input("Insert the trail length (days, e.g. 365): "))
                if trail < 0:
                    print("Trail length cannot be negative")
                    continue
                temp.trail_length = trail
                break
            except ValueError:
                print("Insert a valid number for the trail length")

        while True:
            try:
                radius = int(input("what is your body radius in meters? "))
                if radius < 0:
                    print("radius cannot be negative")
                    continue
                temp.radius_meters = radius
                break
            except ValueError:
                print("Insert a valid number for radius")
        custom_bodies.append(temp)

    return custom_bodies


