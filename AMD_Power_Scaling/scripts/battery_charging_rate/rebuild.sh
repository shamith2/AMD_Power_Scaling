#!/bin/bash

wget https://www.kernel.org/pub/linux/kernel/v5.x/linux-5.16.17.tar.xz
tar -xf linux-5.16.17.tar.xz
sudo apt update && sudo apt install git build-essential bc xz-utils bison flex libssl-dev libelf-dev qt5-default
mv linux-5.16.17/drivers/acpi/battery.c linux-5.16.17/drivers/acpi/battery_orig.c
git clone https://www.github.com/shamith2/rl
cp rl/AMD_Power_Scaling/scripts/battery_charging_rate/battery.c linux-5.16.17/drivers/acpi/battery.c
cd linux-5.16.17/
cp -v /boot/config-$(uname -r) .config
make xconfig
scripts/config --disable SYSTEM_TRUSTED_KEYS
scripts/config --disable SYSTEM_REVOCATION_KEYS
make
sudo make modules_install
sudo make install
reboot
uname -mrs
