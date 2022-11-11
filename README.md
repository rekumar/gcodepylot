# gcodepylot
A python package to manually control 3D printers or other gcode-based hardware. Useful if you are hacking a 3dp to do something else!

This codebase is written to interface with [Marlin](https://marlinfw.org). We tested this code specifically with SKR Mini E3 V1.2-2.0 boards, both attached to Ender 3's and custom gantrys. 

## Example Usage

```
from gcodepylot import Robot

r = Robot(port="COM3") #update the port to your robot's communication port!

r.gohome() #home the robot -- you won't have to do this unless the robot has just been powered on. Can't hurt though!

r.moveto(x=10, y=10, z=10) #moves to (10,10,10)

r.moveto(y=15) #moves in y, xz are not moved. Goes to (10,15,10)

r.moveto(x=30, zhop=False) #moves in x, does not "z-hop". A z-hop is a temporary raise in z during motion to avoid collisions. Goes to (30,15,10)

r.moverel(x=5) #moves +5 in x. Goes to (35,15,10). zhop=False flag is valid here too!

r.gui() #opens a graphical user interface to jog the robot in x,y,z. Close it whenever you're done -- you can continue to control via python code.
```
