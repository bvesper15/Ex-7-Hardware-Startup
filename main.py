import os

os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.clock import Clock

from pidev.Joystick import Joystick
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel

import spidev
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers

from datetime import datetime

time = datetime

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'

joy = Joystick(0, True)

spi = spidev.SpiDev()

s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=2)
s0.setMaxSpeed(600)
s0.setMinSpeed(0)

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    joyx = joy.get_axis('x')
    joyy = joy.get_axis('y')

    anim = Animation(size=(400, 300), duration=3) + Animation(size=(200, 150), duration=3)
    anim.repeat = True

    def slider(self,dt):
        s0.setMaxSpeed(self.ids.sl.value_normalized * 600)
        if self.ids.mtr.text == 'motor on':
            s0.run(self.ids.mtr.mDir, 10000)
            print(str(s0.speed))


    def updateJoy(self, dt):
        joyx = joy.get_axis('x')
        joyy = joy.get_axis('y')
        self.ids.joy.x = joyx * self.width
        self.ids.joy.y = joyy * self.height

    def changeDir(self):
        if self.ids.mtr.mDir == 0:
            self.ids.mtr.mDir = 1
            s0.run(self.ids.mtr.mDir,10000)
        else:
            self.ids.mtr.mDir = 0
            s0.run(self.ids.mtr.mDir,10000)

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_interval(self.updateJoy, 0.01)
        Clock.schedule_interval(self.slider, 0.1)
        self.anim.start(self.ids.img)

    def image(self):
        SCREEN_MANAGER.current = 'button'

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        print("Callback from MainScreen.pressed()")
        s0.free_all()
        spi.close()
        GPIO.cleanup()
        quit()

    def toggleMotor(self):
        if self.ids.mtr.text == 'motor off':
            self.ids.mtr.text = 'motor on'
            s0.run(self.ids.mtr.mDir,10000)
            print('on')
        else:
            self.ids.mtr.text = 'motor off'
            print('off')
            s0.softStop()

    def toggle(self):
        if self.ids.btn.text == 'on':
            self.ids.btn.text = 'off'
        else:
            self.ids.btn.text = 'on'

    def count(self):
        print(joy.get_axis('x'), joy.get_axis('y'))
        self.ids.cnt.i += 1
        self.ids.cnt.text = str(self.ids.cnt.i)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class ButtonScreen(Screen):
    anim = Animation(size=(400, 300), duration=3) + Animation(size=(200, 150), duration=3)
    anim.repeat = True
    def __init__(self, **kw):
        super().__init__(**kw)
        self.anim.start(self.ids.img)
    def image(self):
        SCREEN_MANAGER.current = 'main'


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(ButtonScreen(name='button'))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
