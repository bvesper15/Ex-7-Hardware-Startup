# Pidev Kivy Usage

## SelfUpdatingLabel
The goal of the self updating label is to update the text from a given method at a set time interval.
Common usage would be to update a labels text based off an objects method.

### Example usage
This example usage will walk you through how to update based off a joysticks value:

* Start by importing ```from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel```

* Declare your joystick object in your python file 
```python
from pidev.Joystick import Joystick

JOY = Joystick(number=0, ssh_deploy=True)
```

* Import your python declared joystick into your KV file: ```#: import JOY __main__.JOY``` this imports JOY from your python
file into your KV file with the name JOY, it is important to note that JOY now references the same JOY object in your python file

* Add the self updating label to your KV file:
```
SelfUpdatingLabel:
        size_hint: None, None
        font_size: 30
        text: str(root.stepper_property.get_position())
        update_property: JOY.get_position_in_units
        update_property_parameters: "x"
        center_x: root.width * 0.5
        center_y: root.height * 0.5
        color: 1, 1, 1, 1
```

* The update_property is what you would like the label to update to. NOTE: since JOY is a reference to an object if we set update_property to JOY.get_axis('x)
it will call the function once and never update, therefore we must call it with JOY.get_axis which is a reference to the method

* The update_property_parameters are parameters you would like to pass to the method you are calling
