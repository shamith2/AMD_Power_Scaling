#include <acpi/battery.h>

/*  
Driver Description:
    Windows Driver to Trottle Battery Charging Rate

References:  https://uefi.org/specs/ACPI/6.4/10_Power_Source_and_Power_Meter_Devices/Power_Source_and_Power_Meter_Devices.html
*/

int throttleBatteryCharge(int);

struct battObj {
    acpi_handle handle;
    DECLARE_RWSEM(lock);
}

int throttleBatteryCharge(
    int throttleLimit
)
/*
Routine Description:
    This subroutine IOCTL throttles the battery charging rate to the specified throttleLimit

Parameters:
    throttleLimit: An integer from 0 to 100 containing the battery thermal throttle limit in percentage. At 100%, the battery can be charged at maximum current.

Return Value:
    status of the operation: 
      0: successful
      1: Error in IoBuildDeviceIoControlRequest: STATUS_INSUFFICIENT_RESOURCES
      2: Request Not Successful
      3: Output Buffer Not Valid
*/
{

// variables
acpi_status status;
acpi_handle handle; 
acpi_string acpi_method = "\_SB.PCI0.ISA0.EC0.BTH";

union acpi_object arg0 = {ACPI_TYPE_INTEGER};
struct acpi_object_list parameters = {&arg0};
arg0.integer.value = throttleLimit;

/*
Can also use _DSM method
guid_t uuid = "4c2067e3-887d-475c-9720-4af1d3ed602e";
u64 rev = 0;
u64 func = 1;

down_write(battObj->lock);

// call the method
status = acpi_evaluate_dsm(handle, uuid, rev, func, &parameters);

up_write(battObj->lock);
*/

// get the handle of the method
// DeviceObject: _HID: "PNP0C0A"; Device: "BAT0"
status = acpi_get_handle(NULL, acpi_method, battObj->handle);

if (ACPI_FAILURE(status))
{
    return 1;
}

down_write(battObj->lock);

// Pass request to DeviceObject, always wait for completion routine
status = acpi_evaluate_object(handle, NULL, &parameters, NULL);

up_write(battObj->lock);

// check the status of driver call
if (ACPI_FAILURE(status))
{
    return 2;
}

// check the validity of the output parameters


// process the output parameters that are passed back

// complete the request
// PriorityBoost: currently 6; equal priority with keyboard interrupts

return 0;

}
