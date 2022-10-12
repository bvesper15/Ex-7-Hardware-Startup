# To set up the power_shutdown module:
The power_shutdown module is a module that allows the Raspberry Pi to gracefully shutdown when connected to an RPMIB (Raspberry Pi Multi Interface Board).

## Installation Instructions
Installing the power_shutdown module will take a little while as there are a fair amount of dependencies needed to compile and install the linux kernel module.

It is recommended you back up any important documents in the unlikely event your kernel is corrupted.

### Installation Script
There is a script located in the RaspberryPiCommon/Scripts named install-power-shutdown.sh.

Run this script with sudo. This will install all of the necessary dependencies, however the Pi needs to be rebooted in order for these changes
to take effect. 
* Please note that upon running the script for the first time it will create a file named "part_1_complete.txt" please do not remove this file.
The script will remove the file upon the second run of the script. 

Upon reboot you need to re-run this script. This will now make and install the power_shutdown module into the linux kernel.

After running the install script the second time and rebooted the installation process is complete.

## Test that power_shutdown functions properly
It is important to understand that testing this module includes removing power to the Pi while the os is still mounted.
If the power_shutdown module didn't install correctly your os may become corrupt due to a power loss event. 

Please backup all important files before testing.

 0. Cut power to the Pi and RPMIB
 1. Verify the Red power LED (LED1) on the RPiMIB stays illuminated after the RPiMIB  and Pi looses power
 2. Verify the Green status LED on the RPi next to the red power LED flickers for a few seconds after power is turned off
 3. Verify after about 8 seconds after the Green status LED on the RPi goes off the red power LED turn off
 4. Verify after about 30 seconds after removing power from the RPiMIB the Red power LED (LED1) on the RPiMIB goes off.
 
If all of these steps executed successfully the power_shutdown module was installed and is working correctly.
 
## Troubleshooting
In the event of a bug/install script isn't working correctly read through install-power-shutdown.sh and manually run all commands as root.
This [StackExchange post](https://raspberrypi.stackexchange.com/questions/39845/how-compile-a-loadable-kernel-module-without-recompiling-kernel) inspired the majority of the install script.
