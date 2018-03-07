"""State Machine"""
import logging
import time
from event import Event
from car import Car

SIMU = True
# Mettre cette valeur sur True pour que le code fonctionne en simulation
DETECT_SIGN = True
# Mettre cette valeur sur True pour que la voiture detecte les panneaux

# constants for the different states in which we can be operating
IDLE = 1
STOPPED = 2
MOVING = 3
TURNING = 4
# You can add other states here

TIME_TURNING = 2
TIME_STOPPING = 2

# Setup up the state machine. The following code is called when the state
# machine is loaded for the first time.
logging.info('Simplistic StateMachine has been initialized')

# The next variable is a global variable used to store the state between
# successive calls to loop()
state = IDLE
heading = 0
sign_value = ""
sign_count_dict = {"left": 0, "right": 0, "stop": 0}
path_dict = {}
priority_order = ["straight", "left", "right"]
turn_direction = "right"
last_time_detected = 0
action_start_time = 0


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
    global sign_value
    global heading
    global sign_count_dict
    global last_time_detected
    global turn_direction
    event = Event.poll()
    if event is not None:
        if event.type == Event.CMD and event.val == "GO":
            logging.info("remotely ordered to GO!")
            state = MOVING

        elif event.type == Event.CMD and event.val == "TEST_COMM":
            Car.send(5, -10, 3.14, -37.2)

        elif event.type == Event.CMD and event.val[0:3] == "MAN":
            Car.send(int(event.val[3:5]), 0, 0, 0)
            print("manoeuvre", int(event.val[3:5]))

        elif event.type == Event.PATH:
            handle_path_event(event)

        elif event.type == Event.SIGN and DETECT_SIGN:
            sign_dict = event.val
            sign_value = sign_dict["sign"]
            sign_count_dict[sign_value] += 1
            last_time_detected = time.time()
            print(sign_count_dict)

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
    global sign_count_dict
    global turn_direction
    global action_start_time
    path_dict = event.val

    if path_dict["straight"] is not None:
        path_dict["straight"] *= 0.4
    now = time.time()
    if state == TURNING:
        if now - action_start_time < TIME_TURNING:
            if path_dict[sign_value] is not None:
                heading = path_dict[sign_value]
            elif path_dict["straight"] is not None:
                heading = path_dict["straight"]
            else:
                if sign_value == "left":
                    heading = path_dict["max_left"]
                elif sign_value == "right":
                    heading = path_dict["max_right"]
            print("turning", sign_value, TIME_TURNING - int(now - action_start_time))
            actuate_heading(heading)
        else:
            state = MOVING
            for i in sign_count_dict.keys():
                sign_count_dict[i] = 0
            sign_value = ""
            print("stop turning")

    if state == STOPPED:
        if now - action_start_time < TIME_STOPPING:
            print("stoping")
        else:
            state = MOVING
            for i in sign_count_dict.keys():
                sign_count_dict[i] = 0
            sign_value = ""
            print("stop stoping")

    if state == MOVING:
        values = list(sign_count_dict.keys())
        counts = list(sign_count_dict.values())
        if max(counts) >= 2:
            sign_value = values[counts.index(max(counts))]

        if sign_value != "":  # Panneau detecte
            action_start_time = time.time()
            if sign_value == "stop" and (now - last_time_detected) > 2:
                Car.send(0, 0, 0.0, 0.0)
                print("start stopping")
                state = STOPPED
            elif sign_value == "right" or sign_value == "left":
                if path_dict[sign_value] is not None:
                    heading = path_dict[sign_value]
                    state = TURNING
                    print("start turning", sign_value)
        else:
            found = False
            for direction in priority_order:
                if path_dict[direction] is not None and not found:
                    heading = path_dict[direction]
                    # print("following", direction, heading)
                    found = True
            if not found:
                if heading > 0:
                    heading = path_dict["max_left"]
                else:
                    heading = path_dict["max_right"]
            actuate_heading(heading)


def actuate_heading(heading):
    if SIMU:
        u = 3  # Speed
        v = 0.4 * heading  # Heading
        if heading < -15:  # ignore absurd angles
            v = -15.0
            u = 3.0  # turn quicker
        if heading > 15:  # ignore absurd angles
            v = 15.0
            u = 3.0
    else:
        offSet = heading*0.2/45
        u = 1-offSet  # Vitesse moteur gauche
        v = 1+offSet  # Vitesse moteur droit

    Car.send(0, 0, u, v)
