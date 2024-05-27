# collect_win.py
# collects system data on windows machines
#

import psutil
import time
import argparse
import os
import subprocess
import sys
import wmi
import pythoncom
import time

def writeDataSet(state, filename):
    with open(filename, "a") as f:
        for i, value in enumerate(state):
            if i != 0:
                f.write("," + value)
            else:
                f.write(value)
        f.write("\n")

def create_dataset_file(filename, header):
    with open(filename, "w") as f:
        f.write(header)

def batteryTemperature():
    pythoncom.CoInitialize()
    w = wmi.WMI(namespace='root\\wmi')
    temperature = w.MSAcpi_ThermalZoneTemperature()[0]
    temperature = int(temperature.CurrentTemperature / 10.0 - 273.15)
    return temperature

def collect_data(dir, datafile, duration, step, suffix=1, unit='s'):
    # powershell commands
    commands = ["powercfg /batteryreport /duration 7 /output " + os.path.join(str(dir), "battery-report.xml") + " /xml"]

    for command in commands:
        process = subprocess.run(str(command), capture_output=True, shell=True, text=True, encoding="utf-8")

        if process.stderr != '':
            print("\nExiting due to Error in Collecting Battery Report: {}".format(process.stderr))
            exit(-1)

    for t in range(1, (int(duration) // int(step)) + 1):
        print("Collecting State Data for time {}{}...".format(t, unit), end=" ")
        
        battery = psutil.sensors_battery()
        percent = str(battery.percent)

        stateData = tuple([str(int(time.time())),
                          str(psutil.virtual_memory().percent),
                          str(psutil.cpu_percent()),
                          str("none"),
                          str(percent),
                          str(int(psutil.sensors_battery().power_plugged)),
                          str(batteryTemperature())])
        
        print("Done")

        print("Writing to DataSet File... ", end='')
        writeDataSet(stateData, datafile)
        print("Done")

        print("Waiting for time {}{}...".format(step, unit), end=" ")
        sys.stdout.flush()
        time.sleep(int(step) * int(suffix))
        print("Done\n")

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="datasets")
    parser.add_argument("--duration", type=int)
    parser.add_argument("--step", type=int)
    parser.add_argument("--unit", default='s')
    parser.add_argument("--reset", default=0)
    parser.add_argument("--yes", default=0)
    args = parser.parse_args()

    header = "TIME(int),MEMORY_USAGE(%),CPU_USAGE(%),GPU_USAGE(%),SoC(%),BATTERY_CAPACITY(int),BATTERY_FULL_CAPACITY(int),BATTERY_DESIGN_CAPACITY(int),BATTERY_CAPACITY_LEVEL(int),BATTERY_STATUS(int),BATTERY_VOLTAGE(int),BATTERY_DESIGN_VOLTAGE(int),BATTERY_POWER(int),BATTERY_CYCLES(int),BATTERY_TEMP(C),BATTERY_CHARGE_RATE(W)\n"
    
    if (int(args.yes) == 1):
        to_continue = 'y'
    else:
        print("Welcome to AMD Power Scaling Data Collection for Windows Users\nCopyright (c) 2022 Shamith Achanta, Sumedh Vaidyanathan, Alex Yuan\n")
        print("The following system data will be collected: MEMORY USAGE, CPU USAGE, GPU USAGE, BATTERY HEALTH\nDo you wish to continue. If so, your identity will be anonymous. Enter [y] or n to continue...", end=' ')
        to_continue = str(input())

    if to_continue.lower() != 'y':
        print("\nThank you. Exiting...")

    else:
        filename = os.path.join(str(args.dir), 'dataset.csv')

        if not os.path.isfile(filename):
            create_dataset_file(filename, header)

        if os.path.isfile(filename) and int(args.reset):
            os.remove(filename)
            create_dataset_file(filename, header)
        
        if not os.path.isdir(str(args.dir)):
            os.makedirs(str(args.dir))
            create_dataset_file(filename, header)

        print("\nYour data is being collected...\n")
        if args.unit == 'm':
            suffix = 60
        elif args.unit == 'h':
            suffix = 60 * 60
        elif args.unit == 'd':
            suffix = 60 * 60 * 24
        else:
            print("Incorrect Usage: --unit has to be {s/m/h/d}")
            exit(1)

        done = collect_data(filename, args.duration, args.step, suffix, args.unit)
        print("Finished Collecting DataSet")
        
    print("Have a Great Day!!!")
