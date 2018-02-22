
"""This is a template for State Machine Modules

   A State Machine module is a python file that contains a  `loop` function.
   Similar to how an Arduino program operates, `loop` is called continuously:
   when the function terminates, it is called again.

   The `loop` function should continuously listens to messages generated by:
   - the path detector (concerning the path to follow),
   - the sign detector (concerning road signs detected, if any),
   - the remote command operator (concerning commands to start/stop driving,
     or do specific manoeuvers)
   - and the arduino controller of the physical car (concerning the current
     state; possible sensor readings, ...)

   and decide on how to drive the car correspondingly. See the description of
   the `loop` method below for more details.

   This simplistic State Machine responds to remote commands "GO", "STOP"
   and "TEST_COMM". In addition, it listens to path information from the
   Simplistic Path detector, and sends actuation commands that are
   compatible with the simulator.
"""


import logging
import time
from event import Event
from car import Car
import time

# constants for the different states in which we can be operating
IDLE = 1
STOPPED = 2
MOVING = 3
# You can add other states here


# Setup up the state machine. The following code is called when the state
# machine is loaded for the first time.
logging.info('Simplistic StateMachine has been initialized')

# The next variable is a global variable used to store the state between
# successive calls to loop()
state = IDLE
heading = 0
sign_count = 0
sign_value = ""
path_dict = {}
priority_order = ["straight", "left", "right"]


def loop():
    '''State machine control loop.
    Like an arduino program, this method is called repeatedly: whenever
    it exits it is called again. Inside the function, call:
    - time.sleep(x) to sleep for x seconds (x can be fractional)
    - Event.poll() to get the next event (output of Path and/or Sign detector,
      status sent by the car, or remote command).
    - Car.send(x,y,u,v) to communicate two integers (x and y) and
      two floats(u,v) to the car. How the car interprets this message depends
      on how you implement the arduino nano. For the simulator, x, and y
      are ignored while u encodes the speed and v the relative angle to turn
      to.
    '''
    global state
    global sign_count
    global sign_value
    global heading
    event = Event.poll()
    if event is not None:
        if event.type == Event.CMD and event.val == "GO":
            logging.info("remotely ordered to GO!")
            state = MOVING

        elif event.type == Event.CMD and event.val == "TEST_COMM":
            Car.send(5, -10, 3.14, -37.2)

        elif event.type == Event.CMD and event.val[0:4] == "MAN ":
            Car.send(int(event.val[4:6]), 0, 0, 0)
            print ("manoeuvre ",int(event.val[4:6]))

        elif event.type == Event.PATH:
            if sign_count > 0:
                sign_count -= 1
            handle_path_event(event)

        elif event.type == Event.SIGN:
            sign_dict = event.val
            sign_value = sign_dict["sign"]
            if sign_value == "stop":
                sign_count = 18
            elif sign_value == "left" and sign_count == 0:
                sign_count = 30
            elif sign_value == "right "and sign_count == 0:
                sign_count = 30

        elif event.type == Event.CMD and event.val == "STOP":
            logging.info("remotely ordered to stop")
            emergency_stop()
            time.sleep(100)

        elif event.type == Event.CAR:
            logging.info("Received CAR event with x=%d, y=%d, u=%f, v=%f" % (event.val['x'], event.val['y'], event.val['u'], event.val['v']))
            pass


def emergency_stop():
    global state
    Car.send(0, 0, 0.0, 0.0)
    state = STOPPED


def handle_path_event(event):
    global state
    global heading
    global sign_value
    path_dict = event.val
    if 0 < sign_count < 18 and sign_value != "stop":
        if sign_value == "left":
            heading = path_dict["max_left"]
            print("Turning left", sign_count)
        elif sign_value == "right":
            heading = path_dict["max_right"]
            print("Turning right", sign_count)
    else:

        found = False
        for direction in priority_order:
            if path_dict[direction] is not None and not found:
                heading = path_dict[direction]
                found = True
        if not found:
            if heading > 0:
                heading = 10
            else:
                heading = -10
        if sign_value == "stop" and 0 < sign_count < 10:
            Car.send(0, 0, 0.0, 0.0)
            print("stop", sign_count)
            return
    actuate_heading(heading)


def actuate_heading(heading):
    offSet = heading*0.2/45
    speedL = 1-offSet
    speedR = 1+offSet
    Car.send(0, 0, speedL, speedR)
