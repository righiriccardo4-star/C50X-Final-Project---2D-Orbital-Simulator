# C50X-Final-Project---2D-Orbital-Simulator
**Video Link:** https://youtu.be/CbY3S-B4Qak

Hi, I am Riccardo, an Italian 18 years old student who attended this course in order to develop skills that will be useful for my goal: **aerospace engineering**.

I decided to create this orbital simulator because I thought that it would be a nice first project for my GitHub portfolio and because it required a lot of skills that I learnt in CS50x and during my studies.
I put all my effort in creating a **physic simulator** that would be as accurate as possible and also quite good looking. 
Initially, the program prints a menu on the screen from which it is possible to choose between **4 scenarios**:
1. **Inner Solar System** (that includes the Sun and the planets from Mercury to Jupiter)
2. **Full Solar System** 
3. **The Earth - Moon system** 
4. **Custom Sandbox** , a scenario that permit the user to create as many planets as he wants and that allows total customization. This scenario do not have "safety protocols" so whether the user insert a wrong velocity or a wrong distance between two planets they would collide.

Moreover, this simulator contains some additional features that make it more interactive:
- **Pre orbit simulation**, this feature allows the user to immediately see the full trail of the planet but it needs to be processed so it requires time. If this option is not chosen the simulation will begin without the trail and the planet will draw it on the screen.
- **Use of a spaceship** , it is possible to create a spaceship and after adding all the parameters "driving" it in the solar system. When the Delta V is finished the ship can be reset.
- **Time scale** . The simulation time can be frozen, sped up, slowed down or reset.
- **Zoom in and zoom out and camera moving**


---

## File Structure

- **`simularion_V3.py`** : This file contains the third (and final) version of my program (the other versions are available in the folder). It is the main that menages the main loop, the graphic interface created with Pygame, the mouse and keyboard inputs, the camera and the rendering of planets, trails and of the interface on the screen.
- **`Physics.py`**: This file contain the class `CelestialBody` and the physics engine based on newton's law of universal gravitation and based on the numeric integration of Verlet on sub-steps.
- **`Spaceship.py`**: This file menages the specific logic of the ship that includes the Tsiolkovsky law for the Delta V calculation and the application of the thrust (prograde, retrograde, radials)
-  **`Scenarios.py `** : This file defines the initial presets of celestial bodies of different game scenarios.
-  **`Pre_simulation.py `** : This file execute a preliminary calculation of celestial bodies (warmup) to permit the orbital stabilization and show the trails from the first frame.


---

## Design Choices

- **Verlet integration**, adopted instead of Euler's method to ensure long therm energy conservation and to avoid the numeric dispersion typical of long term orbits.
- **Sub-stepping and Time Scaling**,  The sub_steps implementation for each simulated day preserve physics precision even when the passage of time is drastically enhanced. 
- **Dynamic trail**, the orbits exploit double termination trails which maximum length (`maxlen`) adjust inversely to the time scale factor, keeping the visual length of the orbits constant in space regardless of the chosen speed.


---

## How to Execute

1. Clone or download this repository to your local machine.
2. Ensure you have Python installed, then install the required dependencies by running the following command in your terminal:
```
pip install pygame numpy
```
3. Start the simulator by executing the main script:
```
python main.py
```


---

## How to Use

- **`Spacebar`**: Freeze or unfreeze the simulation time.
    
- **`T`** / **`Y`**: Speed up or slow down the simulation time scale.
    
- **`U`**: Reset the simulation time scale to default.
    
- **`R`**: Reset the spaceship when its Delta-V is exhausted.
    
- **Spaceship Controls**: Use the **arrow keys** (directional arrows) to apply thrust (Prograde, Retrograde, and Radials) while piloting your custom ship.
    
- **`Mouse Scroll`**: Zoom in and zoom out.
    
- **`Click & Drag`**: Pan the camera across the simulation space.


---

## Future Improvements

Even though with this version I reached all my initial goals, I plan to expand and **refine this simulator** as i advance through my aerospace engineering and programming studies. Planned features includes:

- Gravity Grid: Implementing a 2D background mesh that deforms based on the gravitational potential fields of massive bodies.
- Maneuver Nodes and Orbital Planning: Adding interactive nodes to plan burns (retrograde/prograde) ahead of time and predict future trajectories using conic projections
- Optimized Physics Engine: Transitioning heavy calculation to NumPy vectorization or C extensions to handle larger number of custom sandbox bodies without performance drops.
