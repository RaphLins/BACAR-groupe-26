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
TIME_STOPPING = 3

# Setup up the state machine. The following code is called when the state
# machine is loaded for the first time.
logging.info('StateMachine has been initialized')

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
last_time_stop_detected = 0
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
    global last_time_stop_detected
    global turn_direction
    event = Event.poll()
    if event is not None:
        if event.type == Event.CMD and event.val == "GO":
            logging.info("remotely ordered to GO!")
            state = MOVING

        elif event.type == Event.CMD and event.val[0:3] == "MAN":
            Car.send(int(event.val[3:5]), 0, 0, 0)
            print("Sent manoeuvre", int(event.val[3:5]))

        elif event.type == Event.PATH and state != IDLE:
            if (time.time() - last_time_detected) > 3 and sign_value == "":
                reset_sign_count()
            handle_path_event(event)

        elif event.type == Event.SIGN and DETECT_SIGN and state != IDLE:
            sign_dict = event.val
            sign_value = sign_dict["sign"]
            if sign_value != "":
                sign_count_dict[sign_value] += 1
                last_time_detected = time.time()
                if sign_value == "stop":
                    last_time_stop_detected = time.time()
                print(sign_count_dict)

        elif event.type == Event.CMD and event.val == "STOP":
            logging.info("remotely ordered to stop")
            emergency_stop()


def reset_sign_count():
    global sign_value
    global sign_count_dict
    for i in sign_count_dict.keys():
        sign_count_dict[i] = 0
    sign_value = ""


def emergency_stop():
    global state
    send_stop()
    state = IDLE


def handle_path_event(event):
    global state
    global heading
    global sign_value
    global sign_count_dict
    global turn_direction
    global action_start_time
    path_dict = event.val
    now = time.time()
    if state == TURNING and (sign_value == "right" or sign_value == "left"):
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
            reset_sign_count()
            print("stop turning")

    if state == STOPPED:
        if now - action_start_time < TIME_STOPPING:
            send_stop()
            print("stopping", TIME_STOPPING - int(now - action_start_time))
        else:
            state = MOVING
            reset_sign_count()
            print("stop stopping")

    if state == MOVING:
        values = list(sign_count_dict.keys())
        counts = list(sign_count_dict.values())
        if max(counts) >= 2:
            sign_value = values[counts.index(max(counts))]

        if sign_value != "":  # Panneau detecte
            if sign_value == "stop" and (now - last_time_stop_detected) > 2:
                action_start_time = time.time()
                send_stop()
                print("start stopping")
                state = STOPPED
            if sign_value == "right" or sign_value == "left":
                if path_dict[sign_value] is not None:
                    action_start_time = time.time()
                    heading = path_dict[sign_value]
                    state = TURNING
                    print("start turning", sign_value)
        if state == MOVING:
            found = False
            for direction in priority_order:
                if path_dict[direction] is not None and not found:
                    heading = path_dict[direction]
                    found = True
            if not found:
                if heading > 0:
                    heading = path_dict["max_left"]
                else:
                    heading = path_dict["max_right"]
        actuate_heading(heading)


def send_stop():
    if SIMU:
        Car.send(0, 0, 0, 0)
    else:
        Car.send(0, 1, 0, 0)


def actuate_heading(heading):
    if SIMU:
        v = 0.4 * heading  # Heading
        if heading < -15:  # ignore absurd angles
            v = -15.0
        if heading > 15:  # ignore absurd angles
            v = 15.0
    else:
        if heading == "" or heading is None:
            heading = 0
        v = heading * 2.5

    Car.send(0, 0, 3, v)
