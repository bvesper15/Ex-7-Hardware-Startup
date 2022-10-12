"""
@file stepperutilites.py Responsible for holding all utilities (chip statuses, predefined steppers) used with the Slush Engine
"""

"""
Predefined Stepper Motors.

These are Stepper Motors where the settings are known and have been optimized. The aforementioned values are held in a dictionary.
"""

"""Nema 17 Stepper Motor Settings"""
NEMA_17 = {
    'hold_current': 8,
    'run_current': 10,
    'acc_current': 10,
    'dec_current': 10,
    'max_speed': 525,
    'min_speed': 0,
    'micro_steps': 32,
    'threshold_speed': 1000,
    'over_current': 2000,
    'stall_current': 2187.5,
    'accel': 0x50,
    'decel': 0x10,
    'low_speed_opt': False,
    'slope': [0x562, 0x010, 0x01F, 0x01F]
    }

"""Nema 23 Stepper Motor settings"""
NEMA_23 = {
    'hold_current': 8,
    'run_current': 51,
    'acc_current': 51,
    'dec_current': 51,
    'max_speed': 500,
    'min_speed': 100,
    'micro_steps': 2,
    'threshold_speed': 1000,
    'over_current': 1500,
    'stall_current': 1531.25,
    'accel': 0x10,
    'decel': 0x10,
    'low_speed_opt': False,
    'slope': [0x102, 0xB0B, 0x0E1, 0x0E1]
    }

"""Nema 23 Planetary Stepper Motor settings"""
NEMA_23_PLANETARY = {
    'hold_current': 8,
    'run_current': 43,
    'acc_current': 43,
    'dec_current': 43,
    'max_speed': 500,
    'min_speed': 0,
    'micro_steps': 2,
    'threshold_speed': 1000,
    'over_current': 3000,
    'stall_current': 3031.25,
    'accel': 0x01,
    'decel': 0x01,
    'low_speed_opt': False,
    'slope': [0x08BB, 0x02A, 0x06F, 0x06F]
    }
