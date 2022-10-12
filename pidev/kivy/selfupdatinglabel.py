"""
@file selfupdatinglabel.py This file is responsible for holding the SelfUpdatingLabel Class
"""

from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from threading import Thread


class SelfUpdatingLabel(Label):
    """
    Class to constantly refresh a label's text
    """
    thread_instances = list()

    def __init__(self, **kwargs):
        """
        Construct a SelfUpdatingLabel which constantly updates the label's text based upon a given update_property
        :param kwargs: Labels default arguments
        """
        """Super the Label constructor to ensure the Label functions properly"""
        super(SelfUpdatingLabel, self).__init__(**kwargs)

        """Declare update_property and update_property_parameters"""
        self.update_property = ObjectProperty(defaultvalue=None)
        self.update_property_parameters = ObjectProperty(defaultvalue=None)

        """Start a thread to constantly update the label"""
        self.update_text_thread = Thread(target=self.update_text, daemon=True)
        self.update_text_thread.start()

        SelfUpdatingLabel.thread_instances.append(self.update_text_thread)

    def update_text(self) -> None:
        """
        Update the text with the given update_property at the given update_frequency.
        To update text based off a given function set update_property: object.function with no parenthesis
        If the function you are calling includes parameters specify them in update_property_parameters
        :return: None
        """
        while True:
            if self.update_property is None:
                return
            elif callable(self.update_property):  # if the update_property is a method to call
                if self.update_property_parameters is not None:  # call with given parameters
                    self.text = str(self.update_property(self.update_property_parameters))
                else:
                    self.text = str(self.update_property())
            else:  # Set to whatever was given
                self.text = str(self.update_property)

    def stop_updating(self) -> None:
        """
        Stop updating the label
        :return: None
        """
        self.update_text_thread.join()

    def start_updating(self) -> None:
        """
        Begin updating the label
        :return: None
        """
        self.update_text_thread.start()

    @staticmethod
    def get_all_threads() -> list:
        """
        Get all of the instantiated threads associated with each SelfUpdatingLabel
        :rtype: list
        :return: list of instantiated threads
        """
        return SelfUpdatingLabel.thread_instances
