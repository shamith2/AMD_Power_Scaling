#include "acpiioct.h"
#include "wdm.h"

/*  
Driver Description:
    Windows Driver to Trottle Battery Charging Rate

References: https://docs.microsoft.com/en-us/windows-hardware/drivers/ , 
            https://uefi.org/specs/ACPI/6.4/10_Power_Source_and_Power_Meter_Devices/Power_Source_and_Power_Meter_Devices.html
*/

int throttleBatteryCharge(
    IN int throttleLimit,
    OUT int status
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
PIRP retIRP;
NTSTATUS status;

ULONG IoControlCode = IOCTL_ACPI_EVAL_METHOD;
// TODO: DeviceObject: _HID: "PNP0C0A"; Device: "BAT0"
PDEVICE_OBJECT DeviceObject;

ACPI_EVAL_INPUT_BUFFER_SIMPLE_INTEGER InputBuffer = {ACPI_EVAL_INPUT_BUFFER_SIMPLE_INTEGER_SIGNATURE, "_BTH", (ULONG) ("HTB_"), (ULONG) throttleLimit};
ULONG InputBufferLength = sizeof(ACPI_EVAL_INPUT_BUFFER_SIMPLE_INTEGER);
/*
Can also use _DSM method
UCHAR uuid = "4c2067e3-887d-475c-9720-4af1d3ed602e"
ACPI_METHOD_ARGUMENT argument = {ACPI_METHOD_ARGUMENT_BUFFER, 4, uuid, (ULONG) 0, (ULONG) 1, (ULONG) throttleLimit};
ACPI_EVAL_INPUT_BUFFER_COMPLEX InputBuffer = {ACPI_EVAL_INPUT_BUFFER_SIMPLE_INTEGER_SIGNATURE, "_DSM", (ULONG) ("MSD_"), sizeof(ACPI_METHOD_ARGUMENT), 2, [argument]};
ULONG InputBufferLength = sizeof(ACPI_EVAL_INPUT_BUFFER_COMPLEX);
*/

ACPI_EVAL_OUTPUT_BUFFER OutputBuffer;
ULONG OutputBufferLength = sizeof(ACPI_EVAL_OUTPUT_BUFFER);

BOOLEAN InternalDeviceIoControl = FALSE;
// TODO: ioctlEvent
KEVENT ioctlEvent;
IO_STATUS_BLOCK IoStatusBlock;
PLARGE_INTEGER waitTime = NULL; // in nano-seconds

// Initialize an event to wait on
KeInitializeEvent(&ioctlEvent, SynchronizationEvent, FALSE)

// Build the request
retIRP = IoBuildDeviceIoControlRequest(IoControlCode, DeviceObject, &InputBuffer, InputBufferLength, &OutputBuffer, OutputBufferLength, InternalDeviceIoControl, &ioctlEvent, &IoStatusBlock);

if (retIRP == NULL) 
{
  return 1;
}

// Pass request to DeviceObject, always wait for completion routine
status = IoCallDriver(DeviceObject, retIRP);

// Wait for the IRP to be completed, and then return the status code
if (status == STATUS_PENDING) 
{
  KeWaitForSingleObject(&ioctlEvent, Executive, KernelMode, FALSE, waitTime);
  status = IoStatusBlock.Status;
}

// TODO: placement of IoCompletion routine
// Currently, Context not required
/*if (ioctlEvent == NULL)
{
  ioStatus = IoCompletionRoutine(DeviceObject, retIRP)
}*/

// check the status of SendDownStreamIrp
if (status != STATUS_SUCCESS)
{
  return 2;
}

// check the validity of the output parameters
if (OutputBuffer.Signature != ACPI_EVAL_OUTPUT_BUFFER_SIGNATURE)
{
  return 3;
}

// process the output parameters that are passed back

// complete the request
// PriorityBoost: currently 6; equal priority with keyboard interrupts
IofCompleteRequest(retIRP, IO_KEYBOARD_INCREMENT);

return 0;

}
