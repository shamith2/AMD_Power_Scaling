import os
from datetime import datetime
import psutil
import jdatetime
import wmi

from battery_functions import *
from cpp import *

# global variables
c_header = "Count,Day,Time,Charging Status,Predicted Charging Time,State of Charge\n"
d_header = "Day,Date,Time,Time (in minutes),Charging Status,State of Charge,Predicted Charging Time,Battery Temperature (C),Battery Capacity (mAh),Charge Rate (mW), Time to Discharge, Battery Voltage (mV), Cycle Count, Battery Health (%)\n"
home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')
directory = os.path.join(home, 'DATASETS')
c_filename = os.path.join(directory, 'charging_status.csv')
d_filename = os.path.join(directory, 'data.csv')
c_datafiles = [c_filename, c_filename[:-4] + '_spring.csv', c_filename[:-4] + '_summer.csv', c_filename[:-4] + '_autumn.csv', c_filename[:-4] + '_winter.csv']
d_datafiles = [d_filename, d_filename[:-4] + '_spring.csv', d_filename[:-4] + '_summer.csv', d_filename[:-4] + '_autumn.csv', d_filename[:-4] + '_winter.csv']

def check_file(_files, header):
    for _file in _files:
        if not os.path.isdir(directory):
            os.makedirs(directory)
            create_dataset_file(_file, header)

        if not os.path.isfile(_file):
            create_dataset_file(_file, header)

def writeDataSet(state, filename):
    with open(filename, "a") as f:
        for i, value in enumerate(state):
            if i != 0:
                f.write("," + str(value))
            else:
                f.write(str(value))
        f.write("\n")

def create_dataset_file(filename, header):
    with open(filename, "w") as f:
        f.write(header)  

def charging_pattern_predictor(_day: int , _time: int, _month: int = None, k: int = 15, step: int = 15) -> np.ndarray:
    if _month is not None:
        if int(_month) in [1, 2, 3]:
            filename = c_datafiles[1]
        elif int(_month) in [4, 5, 6]:
            filename = c_datafiles[2]
        elif int(_month) in [7, 8, 9]:
            filename = c_datafiles[3]
        else:
            filename = c_datafiles[4]
    else:
        filename = c_datafiles[0]
    
    X, y = transform_data(filename)
    cpp = train_cpp(X, y, k)
    save_cpp(cpp)
    
    Y = np.zeros((step * 12) // step)

    # step = min(step, max_charge_time)

    for idx, i in enumerate(range(0, step * 12, step)):
        x = np.array([[_day, _time + i]], dtype=np.uint64)
        y = predict_cpp(cpp, x)

        Y[idx] = y[0]
    
    return Y

def get_t_optimal(Y: np.ndarray, prob: float = 0.51, step: int = 15) -> int:
    idx_list = np.where(Y < prob)[0]

    if idx_list.shape[0] != 0:
        idx = idx_list[0] * step
        return idx
    else:
        return Y.shape[0] * step

# def get_t_optimal(Y: np.ndarray) -> int:
#     idx_list = np.where(Y == 0)[0]

#     if idx_list.shape[0] != 0:
#         idx = idx_list[0]
#         return idx
#     else:
#         return Y.shape[0]

def convertTime(_time: str): 
    val = _time.split(":")
    return 60 * int(val[0]) + int(val[1])

def collect_data(agent: int = 0, battery: int = 0, store: bool = True, _enable_cpp: bool = False, prob: float = 0.51):
    if agent not in [0, 1, 2]:
        sys.exit()
    
    if battery not in [0, 1, 2]:
        sys.exit()

    # _week, _date, _time = datetime.now().strftime("%w %d/%m/%Y %H:%M:%S").split(' ')
    _week, _date, _time = jdatetime.datetime.now().strftime("%w %d/%m/%Y %H:%M:%S").split(' ')
    _day, _month, _year = _date.split('/')
    _time_in_min = convertTime(_time)

    _battery_info = psutil.sensors_battery()
    _charging_status = int(_battery_info.power_plugged)
    _state_of_charge = int(_battery_info.percent)
    _time_to_discharge = int(_battery_info.secsleft)

    _battery_temp = batteryTempandRate(0)
    _charge_rate, _battery_health_info = verifyBatteryState()

    if battery == 1:
        return tuple([_battery_health_info[3], _battery_health_info[2]]) # (Full Capacity, Design Capacity)
    elif battery == 2:
        return _battery_health_info[3] * _battery_health_info[0] # Full Capacity * Battery Voltage
    else:
        pass

    _enable_cpp = True

    if _enable_cpp:
        # Y = charging_pattern_predictor(_week, _time_in_min, _month)
        Y = charging_pattern_predictor(_week, _time_in_min)
        t_optimal = get_t_optimal(Y, prob)
    else:
        t_optimal = 0

    charging_data = tuple([1, _week, _time_in_min, _charging_status, t_optimal, _state_of_charge])
    data = tuple([_week, _date, _time, _time_in_min, _charging_status, _state_of_charge, t_optimal, _battery_temp, _battery_health_info[3], _charge_rate, _time_to_discharge, _battery_health_info[0], _battery_health_info[1], (_battery_health_info[3] * 100) / _battery_health_info[2]])

    if store:
        check_file(c_datafiles, c_header)
        writeDataSet(charging_data, c_datafiles[0])

        if int(_month) in [1, 2, 3]:
            writeDataSet(charging_data, c_datafiles[1])
        elif int(_month) in [4, 5, 6]:
            writeDataSet(charging_data, c_datafiles[2])
        elif int(_month) in [7, 8, 9]:
            writeDataSet(charging_data, c_datafiles[3])
        else:
            writeDataSet(charging_data, c_datafiles[4])
        
        check_file(d_datafiles, d_header)
        writeDataSet(data, d_datafiles[0])

        if int(_month) in [1, 2, 3]:
            writeDataSet(data, d_datafiles[1])
        elif int(_month) in [4, 5, 6]:
            writeDataSet(data, d_datafiles[2])
        elif int(_month) in [7, 8, 9]:
            writeDataSet(data, d_datafiles[3])
        else:
            writeDataSet(data, d_datafiles[4])
    
    if agent == 1:
        return charging_data[len(charging_data) - 2:]
    elif agent == 2:
        return tuple([24, _state_of_charge, _battery_health_info[3], t_optimal, _charge_rate])
    else:
        return data

def ChargeRateTest():
    # 0xFFFC := 65532
    # 0xFFFF := 65535
    
    filename = os.path.join(directory, 'charge_history.csv')
    check_file([filename], "Charge Rate Input,Charge Rate Output (mW),Battery Voltage (mV),State of Charge\n")
    
    for charge_rate_input in range(1, 65535 + 1):
        df = pd.read_csv(os.path.join(directory, filename))

        state_of_charge = int(psutil.sensors_battery().percent)

        if df.empty or not ((df['Charge Rate Input'] == charge_rate_input) & (df['State of Charge'] == state_of_charge)).any():
            retVal = batteryTempandRate(True, hex(charge_rate_input))

            if retVal != 0:
                sys.exit()
            
            time.sleep(2)
            
            charge_rate, battery_health_info = verifyBatteryState()
            writeDataSet(tuple([charge_rate_input, charge_rate, battery_health_info[0], state_of_charge]), filename)
        
        time.sleep(2)

def windows_battery_info():
    """
    Code taken from https://stackoverflow.com/questions/16380394/getting-battery-capacity-in-windows-with-python
    """

    c = wmi.WMI()
    t = wmi.WMI(moniker = "//./root/wmi")

    batts1 = c.Win32_Battery()
    print(batts1[0])
    for i, b in enumerate(batts1):
        print('Battery %d Design Capacity: %d mWh' % (i, b.DesignCapacity or 0))


    batts = t.ExecQuery('Select * from BatteryFullChargedCapacity')
    for i, b in enumerate(batts):
        print('Battery %d Fully Charged Capacity: %d mWh' % 
            (i, b.FullChargedCapacity))

    batts = t.ExecQuery('Select * from BatteryStatus where Voltage > 0')
    for i, b in enumerate(batts):
        print('\nBattery %d ***************' % i)
        print('Tag:               ' + str(b.Tag))
        print('Name:              ' + b.InstanceName)

        print('PowerOnline:       ' + str(b.PowerOnline))
        print('Discharging:       ' + str(b.Discharging))
        print('Charging:          ' + str(b.Charging))
        print('Voltage:           ' + str(b.Voltage))
        print('DischargeRate:     ' + str(b.DischargeRate))
        print('ChargeRate:        ' + str(b.ChargeRate))
        print('RemainingCapacity: ' + str(b.RemainingCapacity))
        print('Active:            ' + str(b.Active))
        print('Critical:          ' + str(b.Critical))

if __name__ == '__main__':
    # data = collect_data(agent=0, battery=0)
    # print(data)

    # ChargeRateTest()

    windows_battery_info()