#!/bin/bash

function collect_data()
{    
    battDir="/sys/class/power_supply/"

    for ((t = 1; t <= $2/$3; t++))
    do
        echo -n "Collecting State Data for time $t$4... "
        
        timeInfo=$(date +%s)
        memInfo=$(free -t | awk 'NR==4{printf "%f", $3*100/$2}')
        cpuInfo=$(top -bn1 | awk 'NR==3' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{printf "%f", 100-$1}')
        # TODO: GPU USAGE
        gpuInfo=$(echo -n '0')
        
        battSoCInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/capacity)
        # capacity level status: Normal: 1, Full: 2
        battCapLvlInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/capacity_level | awk '{if($1 == "Normal") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}')
        # plug-in status: Discharging: 0, Charging: 1, Full: 2
        battStatusInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/status | awk '{if($1 == "Charging") {printf "%d", 1} else if($1 == "Full") {printf "%d", 2} else {printf "%d", 0}}')
        battVolInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/voltage_now)
        battDVInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/voltage_min_design)
        battPowInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/power_now)
        battCapInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/energy_now)
        battFCInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/energy_full)
        battDCInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/energy_full_design)
        battCycleInfo=$(ls $battDir | grep BAT | xargs -I{} cat $battDir{}/cycle_count)
        battTempInfo=$(acpi -t | awk '{print $(NB==1)}' | sed 's/.*, *\([0-9.]*\)* degrees C*/\1/' | awk '{printf "%f", $1}')
        battChargeRate=$(upower -e | grep 'BAT' | xargs -I{} upower -i {} | grep energy-rate | tr -d -c 0-9. | awk '{printf "%f", $1}')
        echo "Done"

        echo -n "Writing to DataSet File... "
        echo "$timeInfo,$memInfo,$cpuInfo,$gpuInfo,$battSoCInfo,$battCapInfo,$battFCInfo,$battDCInfo,$battCapLvlInfo,$battStatusInfo,$battVolInfo,$battDVInfo,$battPowInfo,$battCycleInfo,$battTempInfo,$battChargeRate" >> $1
        echo "Done"

        echo -n "Waiting for time $3$4... "
        sleep $3"$4"
        echo "Done"
        echo ""
    
    done
}

function create_dataset_file()
{
    touch $1
    echo "TIME(int),MEMORY_USAGE(%),CPU_USAGE(%),GPU_USAGE(%),SoC(%),BATTERY_CAPACITY(int),BATTERY_FULL_CAPACITY(int),BATTERY_DESIGN_CAPACITY(int),BATTERY_CAPACITY_LEVEL(int),BATTERY_STATUS(int),BATTERY_VOLTAGE(int),BATTERY_DESIGN_VOLTAGE(int),BATTERY_POWER(int),BATTERY_CYCLES(int),BATTERY_TEMP(C),BATTERY_CHARGE_RATE(W)" >> $1
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]
then
    echo "Usage: "
    echo "   ./collect.sh directory duration step timeunit reset"
    echo ""
    echo "Help: "
    echo "  -h, --help      Help Options"
    echo ""
    echo "Arguments: "
    echo "  directory       str: name of directory to store dataset"
    echo "  duration        int: how long to collect data; timestep taken from step"
    echo "  step            int: timestep to wait"
    echo "  timeunit        str: units of timestep {s/m/h/d}"
    echo "  reset           int: 1 to restart data collection"
    echo "  -y or --yes     str: yes to all prompts"
    echo ""
    echo "If you get permission denied: run 'chmod +x ./collect.sh'"
    echo ""
    echo "Report bugs to Shamith Achanta <shamith2@illinois.edu>"
    exit 0
fi

echo "Welcome to AMD Power Scaling Data Collection for Linux Users"
echo "Copyright (c) 2022 Shamith Achanta"
echo ""

if ([ "$6" = "-y" ] || [ "$6" = "--yes" ])
then
    to_continue=y
    to_install=y
else
    echo "The following system data will be collected: MEMORY USAGE, CPU USAGE, GPU USAGE, BATTERY HEALTH"
    echo -n "Do you wish to continue. If so, your identity will be anonymous. "
    read -p "Enter [y] or n to continue... " to_continue

    if [ "$to_continue" = "n" ] || [ "$to_continue" = "N" ]
    then
        echo "Thank you. Exiting..."
        echo ""
        echo "Have a Great Day!!!"
        exit 0
    fi

    echo ""
    echo "Do you have the the following packages installed: acpi, upower"
    read -p "Enter [y] or n to continue... " to_install
    echo ""
fi

if ([ "$to_continue" = "y" ] || [ "$to_continue" = "Y" ]) && ([ "$to_install" = "y" ] || [ "$to_install" = "Y" ])
then
    
    filename=$1"/dataset.csv"

    if [[ ! -f $filename ]]
    then
       create_dataset_file $filename 
    fi
    
    if [[ -f $filename ]] && [ "$5" = "1" ]
    then
        rm $filename
        create_dataset_file $filename
    fi

    if [[ ! -d $1 ]]
    then
        mkdir $1
        create_dataset_file $filename
    fi
    
    echo "Your data is being collected..."
    echo ""
    collect_data $filename $2 $3 $4
    echo "Finished Collecting DataSet"
elif [ "$to_install" = "n" ] || [ "$to_install" = "N" ]
then
    echo "Install <package> using the following command:"
    echo "  Debian: sudo apt update && sudo apt install <package>"
    echo "  Arch: pacman -Syy && sudo pacman -S <package>"
    echo "  Red Hat: yum check-update && sudo yum install <package>"
    echo ""
    echo "Re-Run the script after installing packages."
    exit 0
else
    echo "Check your Input: y or Y for yes, n or N for no"
    echo ""
fi

echo "Have a Great Day!!!"
exit 0
