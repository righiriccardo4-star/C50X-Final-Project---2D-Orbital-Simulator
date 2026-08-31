import math
import time
import numpy as np
import pygame
from collections import deque

G = 6.6743e-11
class CelestialBody:
    def __init__(self, name, mass, x, y, vx, vy, color, radius, trail_length, radius_meters):
        """
        Inizializza un nuovo corpo celeste con il suo stato fisico iniziale.
        """
        self.name = name        # Nome del corpo (stringa)
        self.mass = mass        # Massa in kg
        
        # Componenti cartesiane della posizione (in metri)
        self.x = x
        self.y = y
        
        # Componenti cartesiane della velocità (in metri al secondo)
        self.vx = vx
        self.vy = vy
        
        # Componenti cartesiane dell'accelerazione attuale (in m/s^2)
        # All'inizio viene impostata a 0, verrà calcolata nel ciclo di fisica
        self.ax = 0
        self.ay = 0

        self.color = color
        self.radius = radius

        self.trail_length = trail_length
        self.trail = deque(maxlen = trail_length)

        self.radius_meters = radius_meters

    def update_position(self, dt):
        # Spostamento basato su velocità e accelerazione corrente
        self.x += self.vx * dt + 0.5 * self.ax * (dt ** 2)
        self.y += self.vy * dt + 0.5 * self.ay * (dt ** 2)

    def update_velocity(self, old_ax, old_ay, dt):
        # Qui facciamo la media tra la VECCHIA accelerazione (passata come parametro)
        # e la NUOVA accelerazione (che è già stata calcolata in self.ax)
        self.vx += 0.5 * (old_ax + self.ax) * dt
        self.vy += 0.5 * (old_ay + self.ay) * dt

def gravity(bodies):
    for body in bodies:
        body.ax = 0.0
        body.ay = 0.0
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            body1 = bodies[i]
            body2 = bodies[j]

            Dx = body1.x - body2.x
            Dy = body1.y - body2.y
            Distance = np.sqrt((Dx**2) + (Dy**2))

            if Distance == 0:
                continue
            
            body1.ax -= (G * body2.mass * Dx) / (Distance**3)
            body1.ay -= (G * body2.mass * Dy) / (Distance**3)

            body2.ax += (G * body1.mass * Dx) / (Distance**3)
            body2.ay += (G * body1.mass * Dy) / (Distance**3)

            