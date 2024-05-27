# collect_linux.py
# collects system data on linux machines
#

import subprocess
import time
import argparse
import os
import sys

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

def collect_data(filename, duration, step, suffix=1, unit='s'):
    memInfo="""free -t | awk 'NR==4{printf "%f", $3*100/$2}'"""
    cpuInfo="""top -bn1 | awk 'NR==3' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{printf "%f", 100-$1}'"""
    # TODO: GPU USAGE
    gpuInfo="""echo -n '0'"""
    
    battDir="""/sys/class/power_supply/"""
    battSoCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity | awk '{printf "%f", $1}'"""
    # capacity level status: Normal: 1, Full: 2
    battCapLvlInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/capacity_level | awk '{if($1 == "Normal") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}'"""
    # plug-in status: Discharging: 0, Charging: 1, Full: 2
    battStatusInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/status | awk '{if($1 == "Charging") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}'"""
    battVolInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_now | awk '{printf "%ld", $1}'"""
    battDVInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/voltage_min_design | awk '{printf "%ld", $1}'"""
    battPowInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/power_now | awk '{printf "%ld", $1}'"""
    battCapInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_now | awk '{printf "%ld", $1}'"""
    battFCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full | awk '{printf "%ld", $1}'"""
    battDCInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/energy_full_design | awk '{printf "%ld", $1}'"""
    battCycleInfo="""ls """ + battDir + """ | grep BAT | xargs -I{} cat """ + battDir + """{}/cycle_count | awk '{printf "%d", $1}'"""
    battTempInfo="""acpi -t | awk '{print $(NB==1)}' | sed 's/.*, *\([0-9.]*\)* degrees C*/\1/' | awk '{printf "%f", $1}'"""
    battChargeRate="""upower -e | grep 'BAT' | xargs -I{} upower -i {} | grep energy-rate | tr -d -c 0-9. | awk '{printf "%f", $1}'"""

    commands = [memInfo, cpuInfo, gpuInfo, battSoCInfo, battCapInfo, battFCInfo, battDCInfo, battCapLvlInfo, battStatusInfo, battVolInfo, battDVInfo, battPowInfo, battCycleInfo, battTempInfo, battChargeRate]

    # data := (state, action, next state, reward, done)
    # state := (TIME,MEMORY_USAGE,CPU_USAGE,GPU_USAGE,BATTERY_CAPACITY,BATTERY_STATUS,BATTERY_VOLTAGE,BATTERY_POWER,BATTERY_ENERGY)

    for t in range(1, (duration // step) + 1):
        stateEntry = tuple()

        print("Collecting State Data for time {}{}...".format(t, unit), end=" ")

        stateEntry += (str(int(time.time())),)

        for command in commands:
            process = subprocess.run(command, capture_output=True, shell=True, text=True, encoding="utf-8")
            
            #if process.stderr == '':
            stateEntry += (process.stdout,)
            #else:
            #    print("\nExiting due to Error: {} in Collecting Data".format(process.stderr))
            #    return -1
        
        print("Done")

        print("Writing to DataSet File...", end=" ")
        writeDataSet(stateEntry, filename)
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
        print("Welcome to AMD Power Scaling Data Collection for Linux Users\nCopyright (c) 2022 Shamith Achanta\n")
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
