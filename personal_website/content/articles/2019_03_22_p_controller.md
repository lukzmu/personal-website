Title: P-Controller for robot control
Date: 2019-03-22 10:00

Below I present a simple implementation of the P-Controller in python. The presented function can be used in a loop and will allow the movement of the robot from the start position to the goal. You can chain the whole path and input the goal of next path points, when one is reached.

```python
import math

def run_p_controller(pos, goal, heading, speed=70, ksi=0.8, precision=80):
    """Function for running robot motors using P-controller
    Parameters
    ----------
    pos: float tuple
        The current position of the robot
    goal: float tuple
        The goal position
    heading: float
        The current heading of the robot
    speed: int
        The initial speed at which wheels should be turned
    ksi: float
        The value of the steering scalar
    precision: int
        The precision of the P-controller orientation
    """

    # Direction estimation based on robot and goal positions
    delta_x = goal[0] - pos[0]
    delta_y = goal[1] - pos[1]
    direction = math.atan2(delta_x, delta_y) / math.pi * 180

    # Orientation conversion into the interval [0...179;-180,...,-1]
    orient = heading - direction
    if orient > 180:
        orient -= 360
    if orient < -180:
        orient += 360

    # P-controller
    left_wheel = speed
    right_wheel = speed
    if orient <= 0:
        if abs(orient) > precision:
            left_wheel = -right_wheel
        else:
            left_wheel = right_wheel + (ksi * orient)
    if orient > 0:
        if orient > precision:
            right_wheel = -left_wheel
        else:
            right_wheel = left_wheel - (ksi * orient)

    # Return wheel power values
    return left_wheel, right_wheel
```
