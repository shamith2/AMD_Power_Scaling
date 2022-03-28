#!/bin/bash

wget https://www.kernel.org/pub/linux/kernel/v5.x/linux-5.16.17.tar.xz
tar -xf linux-5.16.17.tar.xz
sudo apt update && sudo apt install git build-essential bc xz-utils bison flex libssl-dev libelf-dev qt5-default dwarves zstd
git clone https://www.github.com/shamith2/rl
cp rl/AMD_Power_Scaling/scripts/battery_charging_rate/acpi_battery_change_charging_rate.patch .
cd linux-5.16.17/
cp -v /boot/config-$(uname -r) .config
make xconfig
scripts/config --disable SYSTEM_TRUSTED_KEYS
scripts/config --disable SYSTEM_REVOCATION_KEYS
patch -p1 < ../acpi_battery_change_charging_rate.patch
make
sudo make modules_install
sudo make install
reboot
