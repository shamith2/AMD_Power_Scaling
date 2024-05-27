# Makefile for ACPI Battery Driver
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
