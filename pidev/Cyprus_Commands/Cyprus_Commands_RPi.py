"""
@file Cyprus_Commands_RPi.py
File containing the commands to interface with the cyprus
"""
import spidev
import os
from time import sleep

spi = spidev.SpiDev()

DELAY = .001
SPI_FREQUENCY = 1000000
PWM_CLOCK_FREQUENCY = 1000000

COMPARE_MODE = 0
PERIOD = 1
COMPARE = 2

EQUAL = 0
LESS_THAN = 1
LESS_THAN_OR_EQUAL = 2
GREATER_THAN = 3
GREATER_THAN_OR_EQUAL = 4

TRIGGER_OFF = 0xFFFF
DEFAULT_TRIGGER_RADIUS = 0x5
DEFAULT_PERIOD = 20000
SERVO_POSITION_MINIMUM = 400 
SERVO_POSITION_MAXIMUM = 2200 
SERVO_SPEED_COUNTERCLOCKWISE = 1350 
SERVO_SPEED_CLOCKWISE = 1650 

TRIGGER_MODE = 1 
GPIO_MODE = 0

READY = 0xFFFF

currentPeriod = DEFAULT_PERIOD

def initialize():
    currentPeriod = DEFAULT_PERIOD
    open_spi()

    for i in range(1, 3, 1):
        setup_servo(i)
        set_servo_speed(i, 0)
        set_pwm_values(i, currentPeriod, 0, compare_mode = LESS_THAN_OR_EQUAL)

    reset_all_encoder_triggers()
    sleep(DELAY * 100)

def close():
    reset_all_encoder_triggers()

    for i in range(1, 3, 1):
        set_servo_speed(i, 0)

    close_spi()

# break_into_list() and form_word() translate between lists of 2 bytes and 16 bit words
def break_into_list(word):
    return [word >> 8, word & 0x0FF]

def form_word(byte_list):
    return (byte_list[0] << 8) + byte_list[1]

def spi_write_word(word):
    """
    Sends a 16 bit word to the cyprus
    :param word: 16 bit word
    :return: None
    """
    spi.xfer(break_into_list(word), SPI_FREQUENCY)

def spi_read_tx():
    """
    reads the current value in the tx register
    :return:
    """
    return form_word(spi.xfer([0x00, 0x00], 1000000, 1))

def spi_read_word():
    """
    reads a word from the Cyprus when it is ready
    :return:
    """
    sleep(DELAY)
    while True:
        sleep(DELAY)
        if (spi_read_tx() == READY):
            return spi_read_tx()

def open_spi():
    """
    Open SPI communication with the Cyprus
    :return: None
    """
    spi.open(0,0)
    spi.mode = 0b00

def close_spi(): #closes spi communication
    """
    Close SPI communication with the Cyprus
    :return: None
    """
    spi.close()

def read_spi_command(command):
    spi_write_word(command)
    sleep(5 * DELAY)
    word = spi_read_word()
    sleep(5 * DELAY)
    return word

def read_spi(port, channel):
    """
    Read SPI on a given port and channel

    :param port: SPI port to read from
    :param channel: SPI channel on port to read from
    :return: returns the response received by the cyprus from the given port and channel
    """
    command_data = 0x0300 | (port << 4) | channel
    spi_write_word(command_data)
    sleep(2*DELAY)
    return spi_read_word()

def write_spi(port, channel, value):
    """
    Writes the given value to the given spi port and channel of the cyprus
    :param port: Port on the cyprus to write to
    :param channel: Channel on the cyprus to write to
    :param value: The value to write on the given spi port and channel
    :return:
    """
    command_data = 0x0400 | (port << 4) | channel
    spi_write_word(command_data)
    sleep(DELAY)
    spi_write_word(value)

def write_pwm(port, parameter, value):
    """
    changes the given parameter, either COMPARE_MODE, PERIOD, or COMPARE,
    of the given port to the given value. 
    Compare modes: LESS_THAN, LESS_THAN_OR_EQUAL, GREATER_THAN, GREATER_THAN_OR_EQUAL, EQUAL

    :param port: PWM Port
    :param parameter: PWM parameter to change
    :param value: value to change the parameter to
    :return: None
    """
    if ((parameter != PERIOD) and (parameter != COMPARE) and (parameter != COMPARE_MODE)):
        print("ERROR: write_pwm, parameter not recognized (" + str(parameter) + ")")
        return

    if (parameter == PERIOD):
        currentPeriod = int(value)

    command_data = 0x0500 | (port << 4) | parameter
    spi_write_word(command_data)
    sleep(DELAY)
    spi_write_word(int(value))
    sleep(DELAY)
	
def set_pwm_values(port, period_value, compare_value, compare_mode = LESS_THAN_OR_EQUAL):
    write_pwm(port, COMPARE_MODE, compare_mode)
    sleep(DELAY)
    write_pwm(port, PERIOD, period_value)
    sleep(DELAY)
    write_pwm(port, COMPARE, compare_value)
    sleep(DELAY)

def setup_servo(port):
    """
    sets up the given pwm port to control a servo
    :param port: PWM port to setup a servo on
    :return: None
    """
    write_pwm(port, COMPARE, LESS_THAN_OR_EQUAL)
    sleep(DELAY)
    write_pwm(port, PERIOD, currentPeriod)
	
def set_servo_position(port, position):
    """
    sets servo on given port to position given by a number in the interval [0, 1], 
    where 0 corresponds to one end of its range and 1 to the top
    :param port: Port the servo motor is attached to
    :param position: Position to write the servo to in the given interval [0,1]
    :return: None
    """
    if (position > 1):
        position = 1
    elif (position < 0):
        position = 0

    compare = (position * SERVO_POSITION_MAXIMUM) + SERVO_POSITION_MINIMUM
    write_pwm(port, COMPARE, compare)
	
def set_servo_speed(port, speed):
    """
    sets servo on given port to speed given by a number in the interval [-1, 1], 
    where -1 corresponds to maximum in one direction and 1 to the other
    :param port: Port the servo motor is attached to
    :param speed: Speed to set the servo to in the interval [1, 1]
    :return:
    """

    if (speed < -1):
        speed = -1
    elif (speed > 1):
        speed = 1

    if (speed == 0):
        compare = (SERVO_SPEED_COUNTERCLOCKWISE + SERVO_SPEED_CLOCKWISE)/2
    elif (speed < 0):
        compare = SERVO_SPEED_COUNTERCLOCKWISE + ((1.0 + speed) * 100)
    elif (speed > 0):
        compare = SERVO_SPEED_CLOCKWISE + ((speed - 1.0) * 100)

    write_pwm(port, COMPARE, compare)

def set_motor_speed(port, position):
    """
    sets servo on given port to position given by a number in the interval [0, 1], 
    where 0 corresponds to one end of its range and 1 to the top
    :param port: Port the servo motor is attached to
    :param position: Position to write the servo to in the given interval [0,1]
    :return: None
    """
    if (position > 1):
        position = 1
    elif (position < 0):
        position = 0

    compare = position * currentPeriod
    write_pwm(port, COMPARE, compare)
	
def read_gpio():
    """
    Read the GPIO
    :return: returns a 4 bit number, each bit corresponds to a gpio pin
    """
    return read_spi_command(0x0100)

def write_gpio(value):
    """
    given a 4 bit number, writes the bits to the gpio pins
    :param value: 4 bit number
    :return: None
    """
    spi_write_word(0x0200)
    sleep(DELAY)
    spi_write_word(value & 0x0F)

def read_i2c(port, address):
    """
    Read i2c at a given port and address
    :param port: i2c port to read from
    :param address: address on the i2c port
    :return: value read from i2c at the given address
    """
    command_data = 0x0600 | port
    spi_write_word(command_data)
    sleep(DELAY)
    spi_write_word(address << 8)
    sleep(DELAY)
    return spi_read_word()

def write_i2c_data_byte(value):
    """
    writes a single byte to the stored i2c data in the cyprus in advance of send i2c command
    :type value: single byte
    :param value: value to write to the stored i2c data in the cyprus
    :return:
    """
    spi_write_word(0x0800)
    sleep(2*DELAY)
    spi_write_word(value)
    
def write_i2c_data_list(values):
    """
    writes a list of bytes to stored i2c data in the cyprus
    :type values: list of bytes
    :param values: list of bytes to write to the i2c stored data in the cyprus
    :return: None
    """
    for i in range(len(values)):
        write_i2c_data_byte(values[i] & 0x00FF)
        sleep(2*DELAY)

def write_i2c_address(address):
    """
    writes the stored i2c address in the cyprus in advance of send i2c command
    :param address: i2c address to write
    :return: None
    """
    spi_write_word(0x0900)
    sleep(DELAY)
    spi_write_word(address)

def send_i2c(port):
    """
    signals the cyprus to send the prewritten data to the prewritten address through the given port
    :param port: i2c port to write to
    :return:
    """
    command_data = 0x0700 | port
    spi_write_word(command_data)
    
def write_i2c(port, address, values):
    """
    complete procedure to send given list of bytes to given address through given i2c port
    :param port: i2c port
    :param address: i2c address
    :param values: values to write to the i2c port and address
    :return: None
    """
    write_i2c_data_list(values)
    write_i2c_address(address)
    sleep(2*DELAY)
    send_i2c(port)
    
def write_encoder_trigger(command, value):
    spi_write_word(command)
    sleep(DELAY)
    spi_write_word(value)
    sleep(DELAY)

def set_encoder_trigger(channel, value):
    """
    sets trigger on given channel to given value, cyprus activates corresponding gpio pin when encoder reads
    within radius of trigger set value to TRIGGER_OFF to disable trigger
    :param channel: channel to set the trigger value
    :param value: value to set the trigger on the given channel
    :return:
    """
    command_data = 0x0a00 | channel
    write_encoder_trigger(command_data, value)
    
def set_encoder_trigger_auto_reset(channel, value):
    """
    sets trigger on given channel to given value, cyprus activates corresponding gpio pin when encoder reads
    within radius of trigger. The trigger only fires once, the trigger value is reset after it is hit.
    :param channel: channel to set the trigger value
    :param value: value to set the trigger on the given channel
    :return:
    """
    command_data = 0x0a10 | channel
    write_encoder_trigger(command_data, value)

def reset_encoder_trigger(channel):
    set_encoder_trigger(channel, TRIGGER_OFF)
    set_trigger_radius(channel, DEFAULT_TRIGGER_RADIUS)

def reset_all_encoder_triggers():
    for i in range(0, 4, 1):
        set_encoder_trigger(i, TRIGGER_OFF)
        set_trigger_radius(i, DEFAULT_TRIGGER_RADIUS)

def read_encoder(port, channel):
    """
    returns the value from the encoder at the given channel
    :param port: port of the encoder
    :param channel: channel the encoder is on
    :return:
    """
    command_data = 0x0b00 | (port << 4) | channel
    return read_spi_command(command_data)

def set_trigger_radius(channel, value):
    """
    sets the encoder trigger radius of the given channel to the given value
    :param channel: channel of the encoder
    :param value: value of the trigger radius
    :return:
    """
    command_data = 0x0c00 | channel
    spi_write_word(command_data)
    sleep(DELAY)
    spi_write_word(value)
    sleep(DELAY)

def set_pinmode(mode):
    """
    sets the pins to either encoder trigger mode or gpio mode, using constants TRIGGER_MODE and GPIO_MODE
    :param mode: mode to set the pins to
    :return: None
    """
    spi_write_word(0x0d00)
    sleep(DELAY)
    spi_write_word(mode)
	
def read_firmware_version():
    """
    reads the firmware version from the cyprus
    :return: list in the form of [major, minor, patch]

    MAJOR version when you make incompatible API changes,
    MINOR version when you add functionality in a backwards-compatible manner, and
    PATCH version when you make backwards-compatible bug fixes.

    Displayed in the following format: MAJOR.MINOR.PATCH (MM/DD/YY)
    """

    major = read_spi_command(0x0f00)
    minor = read_spi_command(0x0f01)
    patch = read_spi_command(0x0f02)

    month = read_spi_command(0x0f03)
    day = read_spi_command(0x0f04)
    year = read_spi_command(0x0f05)

    return str(major) + "." + str(minor) + "." + str(patch) + \
           " (" + str(month) + "/" + str(day) + "/" + str(year) + ")"

def no_command():
    """
    sends command to cyprus that tells it to do nothing
    :return: None
    """
    spi_write_word(0x0000)
