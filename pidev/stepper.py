"""
@file stepper.py
File containing stepper class to interface with stepper motors on the Slush Engine
"""
from threading import Thread

import Slush
from Slush.Devices import L6480Registers as LReg6480
from Slush.Boards.BoardUtilities import BoardTypes as Board

from .slush_manager import slush_board as slush_board  # https://elcodis.com/parts/5983789/L6470_p49.html
from .stepperutilities import *


class stepper(Slush.Motor):
    """
    DPEA stepper implementation, extended from Slush.Motor
    Reference Slush.Motor for additional functionality
    """

    def __init__(self, port: int = 0, micro_steps: int = 64, hold_current: float = 20.0, run_current: float = 20,
                 accel_current: float = 20, deaccel_current: float = 20,
                 steps_per_unit: float = 200 / 25.4, speed: float = 1, stepper_type: dict = None):
        """
        Constructor for the stepper class
        :param port: port the stepper is connected to. 0-3 on XLT, 0-6 on D. Default:0
        :param micro_steps: how much each step is subdivided. (1,2,4,8,16,32,64,128) Default:64
        :param hold_current: amount of current when motor is holding in place. Default:20
        :param run_current: amount of current when motor is moving at constant speed. Default:20
        :param accel_current: amount of current when motor is accelerating. Default:20
        :param deaccel_current: amount of current when motor is decelerating. Default:20
        :param steps_per_unit: amount of steps per unit. used so you can control motors by linear distance (with lead
               screws) or by revolutions if the motor rotates something Default:200/25.4 (used to move in mm on 8mm/turn lead screws)
        :param speed: how fast the stepper moves in units
        :param stepper_type: A dict holding all of the necessary motor parameters see pidev.stepperutilities for an example
        """
        super().__init__(port)
        self.port = port

        if stepper_type is None or not isinstance(stepper_type, dict):
            self.micro_steps = micro_steps
            self.set_micro_steps(self.micro_steps)
            self.setCurrent(hold_current,
                            run_current,
                            accel_current,
                            deaccel_current)
            self.steps_per_unit = steps_per_unit
            self.speed = speed
            self.set_speed(self.speed)

        else:
            self.setup_predefined_stepper(stepper_type=stepper_type)
            self.steps_per_unit = steps_per_unit

        """self.bordInUse is 1 when using model D, 0 when using model XLT"""
        if self.boardInUse == Board.D:  # a model D is being used
            self.setParam(LReg6480.GATECFG1, 0x5F)
            self.setParam(LReg6480.OCD_TH, 0x1F)

        stepper.instances.append(self)

    def setup_predefined_stepper(self, stepper_type: dict) -> None:
        """
        Setup a predefined stepper motor.
        :param stepper_type: A dictionary containing all of the stepper motor's settings
        :return: None
        """

        """Go through all of the stepper settings and apply them"""

        self.setCurrent(stepper_type['hold_current'], stepper_type['run_current'], stepper_type['acc_current'],
                        stepper_type['dec_current'])
        self.setAccel(stepper_type['accel'])
        self.setDecel(stepper_type['decel'])
        self.setMaxSpeed(stepper_type['max_speed'])
        self.setMinSpeed(stepper_type['min_speed'])
        self.setMicroSteps(stepper_type['micro_steps'])
        self.setThresholdSpeed(stepper_type['threshold_speed'])
        self.setOverCurrent(stepper_type['over_current'])
        self.setStallCurrent(stepper_type['stall_current'])
        self.setLowSpeedOpt(stepper_type['low_speed_opt'])

        slope = stepper_type['slope']
        self.setSlope(slope[0], slope[1], slope[2], slope[3])

    def get_micro_steps(self) -> float:
        """
        Get the number of microsteps the stepper motor is running at
        :return:
        """
        return self.micro_steps

    def setMicroSteps(self, micro_steps: int) -> None:
        """
        Overrides Motor.setMicroSteps to properly set microstep field
        :param micro_steps: number of microsteps. Must be of base 2 and less than 128
        :return: None
        """
        self.set_micro_steps(micro_steps=micro_steps)

    def set_micro_steps(self, micro_steps: int) -> None:
        """
        Set the number of microsteps the stepper motor runs at
        :param micro_steps: Number of microsteps of base 2 up to a maximum of 128
        :return: None
        """
        if micro_steps > 128 or micro_steps % 2:  # if microsteps > 128 or not of base 2
            stepper.free_all()
            raise ValueError("Slush Engine only supports microstepping values of base 2 up to a maximum of 128")

        self.micro_steps = micro_steps
        super().setMicroSteps(microSteps=micro_steps)  # Super this call as we override setMicroSteps

    def setMaxSpeed(self, speed: float) -> None:
        """
        Overrides Motor.setMaxSpeed
        :param speed: steppper motor max speed
        :return: None
        """
        self.set_max_speed(speed=speed)

    def set_speed(self, speed_in_units: float) -> None:
        """
        Set the speed the stepper motor runs at in units
        :param speed_in_units: Speed the motor will run at in units
        :return: None
        """
        self.speed = speed_in_units * self.steps_per_unit
        self.set_max_speed(self.speed)
        super().setMaxSpeed(speed=self.speed)  # Super this call as we override setMaxSpeed

    def set_speed_in_steps(self, speed: float) -> None:
        """
        set the speed the stepper motor runs at in steps
        :param speed: Speed the motor will run at in steps
        :return: None
        """
        self.set_max_speed(speed)

    def set_accel(self, acceleration: float) -> None:
        """
        Set the acceleration of the motor
        :param acceleration: Acceleration amount
        :return: None
        """
        self.setAccel(acceleration)

    def set_deaccel(self, deceleration: float) -> None:
        """
        Set the deceleration for the motor
        :param deceleration: Deceleration amount
        :return: None
        """
        self.setDecel(deceleration)

    def home(self, direction: int) -> None:
        """
        Home the motor
        :param direction: Direction (0 or 1) the motor should spin when homing 0-clockwise
        :return: None
        """
        self.run(direction, self.speed)

        while not self.read_switch():
            continue

        self.hard_stop()
        self.set_as_home()

    def home_threaded(self, direction: int) -> Thread:
        """
        Home the stepper motor in a thread.
        :param direction: Direction to move the stepper motor, 0-clockwise 1-ccw
        :return: Thread object handling the home action
        """
        thread = self._create_thread(target=self.home(direction))
        thread.start()

        return thread

    def read_switch(self) -> int:
        """
        Read the stepper motors corresponding switch
        :return: 1 if switch is depressed, 0 otherwise
        """
        if self.getStatus() & 0x4:
            return 1
        else:
            return 0

    def relative_move(self, distance_in_units: float) -> None:
        """
        Moves a certain distance in units (defined by steps_per_unit in constructor) with MOVEMENTS BLOCKED (synchronise)
        :param distance_in_units: a distance in units
        :return: None
        """
        self.start_relative_move(distance_in_units=distance_in_units)
        self.wait_move_finish()

    def start_relative_move(self, distance_in_units: float) -> None:
        """
        Starts moving a certain distance in units (defined by steps_per_unit in constructor) WITHOUT BLOCKING MOVEMENTS (a-synchronise)
        :param distance_in_units: a distance in units
        :return:
        """
        number_of_steps = distance_in_units * self.micro_steps * self.steps_per_unit
        self.move(int(number_of_steps))

    def relative_move_threaded(self, distance_in_units: float) -> Thread:
        """
        Perform a relative move in a thread
        :param distance_in_units: Distance in units to relatively move the stepper
        :return: Thread object handling the relative move
        """

        thread = self._create_thread(target=self.start_relative_move(distance_in_units))
        thread.start()
        return thread

    def go_to_position(self, position_in_units: float) -> None:
        """
        Goes to a set position in units (defined by steps_per_unit in constructor) WITH BLOCKING (synchronise)
        :param position_in_units: position to move to in units
        :return: None
        """
        position_in_steps = position_in_units * self.micro_steps * self.steps_per_unit
        self.go_to(int(position_in_steps))
        self.wait_move_finish()

    def start_go_to_position(self, position_in_units: float) -> None:
        """
        Begins going to a set position in units (defined by steps_per_unit in constructor) WITHOUT BLOCKING (a-synchronise)
        :param position_in_units: position to move to in units
        :return: None
        """
        position_in_steps = position_in_units * self.micro_steps * self.steps_per_unit
        self.go_to(int(position_in_steps))

    def go_to_position_threaded(self, position_in_units):
        """
        Begin a go to position threaded
        :param position_in_units: Position in units to go to
        :return: Thread object handling this method call
        """
        thread = self._create_thread(target=self.start_go_to_position(position_in_units))
        thread.start()
        return thread

    @staticmethod
    def get_GPIO_state(port: int, pin: int) -> bool:
        """
        Get the state of one of the GPIO pins
        :param port: GPIO port a=0, b=1
        :param pin: Pin to check, first pin=0 incrementing by one
        :return:
        """
        return slush_board.getIOState(port, pin)

    @staticmethod
    def set_GPIO_state(port: int, pin: int, state: int) -> None:
        """
        Set the state of one of the GPIO pins
        :param port: GPIO port a=0, b=1
        :param pin: Pin to set, first pin=0 incrementing by one
        :param state: State you want to set the pin at
        :return: None
        """
        return slush_board.setIOState(port, pin, state)

    def set_limit_hardstop(self, stop: bool) -> None:
        """
        Set whether the Slush Engine should stop moving the stepper motor when it hits the limit switch
        :param stop: True motor with stop when sensor is high (Should be used in cases where there is a mechanical stop)
                     False motor will continue past sensor (Should be used when motor can rotate freely)
        :return: None
        """
        try:
            self.setLimitHardStop(stop)
        except AttributeError:
            stepper.free_all()
            raise ImportError("Slush.setLimitHardStop isn't present update SlushEngine Code from DPEA Fork")

    def stop(self) -> None:
        """
        Stops the motor, same as performing a hard stop
        :return: None
        """
        self.hard_stop()

    def hard_stop(self) -> None:
        """
        Hard stop the motor
        :return: None
        """
        self.hardStop()

    def go_to(self, number_of_steps: int) -> None:
        """
        Make the stepper go to a position in steps
        :param number_of_steps: Number of steps to move
        :return: None
        """
        self.goTo(number_of_steps)

    def wait_move_finish(self) -> None:
        """
        Wait for the move to finish
        :return: None
        """
        self.waitMoveFinish()

    def set_as_home(self) -> None:
        """
        Set the current position as home
        :return: None
        """
        self.setAsHome()

    def set_max_speed(self, speed: float) -> None:
        """
        Set the max speed the stepper motor can run at
        :param speed: The maximum speed
        :return: None
        """
        super().setMaxSpeed(speed)

    def move_steps(self, steps: int) -> None:
        """
        Move the stepper motor a set amount of steps including microstepping. Forwards the call to Slush Motor move()
        :param steps: Number of steps to move (multiplied by microstepping amount)
        :return: None
        """
        self.move(steps * self.micro_steps)

    def go_until_press(self, dir: int, speed: int, act: int = 0) -> None:
        """
        Move the stepper until it hits a sensor.
        Forwards the call to Motor.goUntilPress
        :param dir: The direction 1 or 0
        :param speed: Speed in steps per second
        :param act: Act parameter in Slush.Motor.goUntilPress(). This defaults to 0 to ensure proper functionality
        :return: None
        """
        if self.read_switch() is 0:
            self.goUntilPress(act=act, dir=dir, spd=speed)

    def is_busy(self) -> bool:
        """
        Checks if the stepper is moving
        :return: True or False
        """
        return self.isBusy()

    def get_position(self) -> float:
        """
        Gets the position of the stepper in steps
        :return: position in steps
        """
        return self.getPosition()

    def get_position_in_units(self) -> float:
        """
        Gets the position of the stepper in units
        :return: position in units
        """
        return self.get_position() / self.steps_per_unit / self.micro_steps

    def __repr__(self) -> str:
        """
        Returns string representation of the stepper object
        :return: "stepper on port" with the corresponding port number
        """
        return "stepper on port " + str(self.port)

    def _create_thread(self, target):
        """
        Create a thread. Threads are used in multiple methods throughout stepper.py, this
        method allows for a standard thread creation implementation
        :param target: Threads target method
        :return: Thread object with the given target, daemon set to true
        """
        return Thread(target=target, daemon=True)
