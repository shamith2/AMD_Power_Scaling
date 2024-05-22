from ctypes import *
import ctypes
import os
import time
import sys

libaps = CDLL(os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging', 'AMDPMF', 'x64', 'Release', 'AmdPMFServices.dll'), use_last_error=True)
libcgr = CDLL(os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging', 'cpp_lib', 'BatteryQueryLib', 'x64', 'Release', 'BatteryQueryLib.dll'), use_last_error=True)
libec = CDLL(os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging', 'cpp_lib', 'EmbeddedController', 'x64', 'Release', 'EmbeddedController.dll'), use_last_error=True)

def batteryTempandRate(change_charge_rate: bool = False, charge_rate: str = '0x1'):
    # Get Battery Temperature
    if change_charge_rate == 0:
        aps_get_battery_temp = libaps.apsGetBatteryTemperature
        aps_get_battery_temp.argtypes = [POINTER(c_ulong)]
        aps_get_battery_temp.restype = c_int
        battery_temp = (c_ulong())
        battery_temp_ret = aps_get_battery_temp(byref(battery_temp))

        if battery_temp_ret != 0:
            sys.exit()
        
        battery_temp_c = battery_temp.value - 273.16

        return battery_temp_c

    # Change Charge Rate
    elif change_charge_rate == 1:
        aps_set_charge_rate = libaps.apsSetChargeRate
        aps_set_charge_rate.argtypes = [c_ulong]
        aps_set_charge_rate.restype = c_int
        charge_rate_ret = libaps.apsSetChargeRate(c_ulong(int(charge_rate, 16)))

        if charge_rate_ret != 0:
            sys.exit()
        
        else:
            return 0
    
    else:
        sys.exit()

def verifyBatteryState():
    # battery_health_info := [[Battery Voltage [mV] (%lu), Cycle Count (%lu), Design Capacity (%lu), Full Capacity (%lu), Units (%x), dwResult (%x)]
    py_battery_health_info = [0, 0, 0, 0, 0, 0, 0]
    size = len(py_battery_health_info)
    c_battery_health_info = (ctypes.c_ulong * size)(*py_battery_health_info)
    
    charge_rate = libcgr.GetBatteryState(c_battery_health_info)

    py_battery_health_info = [_info for _info in c_battery_health_info]

    return charge_rate, py_battery_health_info

def getBatteryTemperature():
    py_battery_temperature = [0, 0]
    size = len(py_battery_temperature)
    
    c_battery_temperature = (ctypes.c_ubyte * size)(*py_battery_temperature)
    retVal = libec.GetBatteryTemperature(c_battery_temperature)

    if retVal != 0:
        print(retVal)
        sys.exit()

    return py_battery_temperature

if __name__ == '__main__':
    # batteryTemp = batteryTempandRate(0)
    # print("Battery Temperature: {} K\n".format(batteryTemp))
    
    # retVal = batteryTempandRate(True, '0xfffc')
    # print(retVal)
    
    # time.sleep(2)
    
    # charge_rate, battery_health_info = verifyBatteryState()
    # print(charge_rate, battery_health_info)

    print(getBatteryTemperature())