# Makefile for ACPI Battery Driver
# Copyright (c) 2022 Shamith Achanta
# Report bugs to Shamith Achanta <shamith2@illinois.edu>
#

ACPI_DIR := /drivers/acpi

obj-m += acpi_battery.o 
acpi_battery-objs := acpi_battery_charge_rate.o $(ACPI_DIR)/battery.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

clear: clean
	rm -f Module.symvers
