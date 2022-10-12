#!/bin/bash

# Check to see if user executed this script as root, if not exit
if [ "$EUID" -ne 0 ]
  then echo "Please excute this script as root simply run sudo !!"
  exit 1
fi

FILE=part_1_complete.txt

# First part of install has completed finish the rest
if [ -f "$FILE" ]; then
  cd power_shutdown/ || exit 1

  echo "Making the power_shutdown module and installing it in the kernel"
  make all
  make install
  rm ../"$FILE"
  echo "The power_shutdown module has been installed please reboot the pi to complete installation"
  echo "This is the final step in the installation, this script doesn't need to be re-run upon reboot"
  exit 0
fi

# Get the working directory of where this script has been executed from
WORKING_DIR=$PWD

echo "Getting necessary dependencies"

# Install necessary dependencies before we begin
apt-get install bison -y
apt-get install flex -y
apt-get install bc -y

echo "Updating and upgrading this may take a few minutes"

# Navigate to the home directory
cd /home/pi || exit 1

# Get the RPi kernel source
wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source

# Make the rpi-source script executable
chmod +x /usr/bin/rpi-source

# Update the script notifiying of latest kernel version
/usr/bin/rpi-source -q --tag-update

# Perfrom all necessary kernel actions
rpi-source

# Navigate to pidev's power_shutdown
cd "$WORKING_DIR" || exit 1
touch part_1_complete.txt

echo "The Raspberry Pi needs to be rebooted at this point"
echo "Please rerun this script upon reboot to finish the installation"
