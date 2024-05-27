/*  
 * Module Description:
 *   ACPI Battery Driver module to change Battery Charging Rate
 *   used with /drivers/acpi/battery.c
 *
 * References:  https://uefi.org/specs/ACPI/6.4/10_Power_Source_and_Power_Meter_Devices/Power_Source_and_Power_Meter_Devices.html
 */

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Shamith Achanta");
MODULE_DESCRIPTION("ACPI Battery Driver module to change Battery Charging Rate");

// function prototype
static int acpi_battery_change_charging_rate(struct acpi_battery *battery, const int charging_rate)

// variables
static char *battery_name = "BAT0";
static int charging_rate = 20;

// module parameters
MODULE_PARM(battery_name, 'i');
MODULE_PARM(charging_rate, 's');

// module description
MODULE_PARM_DESC(battery_name, "Name of Battery: BAT0 or BAT1. default: BAT0");
MODULE_PARM_DESC(charging_rate, "Charging Rate of Battery. Should be between 20 and 80. default: 20");

static int acpi_battery_change_charging_rate(struct acpi_battery *battery, const int charging_rate)
/*
Function Description:
    This function changes the battery charging rate to the specified charging_rate

Parameters:
    charging_rate: An integer from 0 to 100 containing the battery charging rate in percentage. At 100%, the battery can be charged at maximum current.

Return Value:
    status of the operation: 
      0: successful
      -ENODEV: unsucessful
*/
{
    acpi_status status = 0;

	// if battery is not present or battery is not charging or issue with charging adapter or battery is full or battery charging rate is undefined
    if (!acpi_battery_present(battery) || battery->state & ACPI_BATTERY_STATE_CHARGING || \
        acpi_battery_handle_discharging(battery) == POWER_SUPPLY_STATUS_NOT_CHARGING || acpi_battery_is_charged(battery) || \
        battery->rate_now == ACPI_BATTERY_VALUE_UNKNOWN)
    {
		return -ENODEV;
    }

    acpi_handle_debug(battery->device->handle, "Current Charging Rate is %d\n", battery->rate_now);

	// change battery charging rate
    mutex_lock(&battery->lock);
	status = acpi_execute_simple_method(battery->device->handle, "_BTH", charging_rate);
	mutex_unlock(&battery->lock);

	if (ACPI_FAILURE(status))
    {
		return -ENODEV;
    }

	acpi_handle_debug(battery->device->handle, "Charging Rate set to %d\n", battery->rate_now);

	return 0;
}

static int __init main(void)
{
    struct power_supply *psy = power_supply_get_by_name(battery_name);
    struct acpi_battery *battery = to_acpi_battery(psy);

    // charging rate should be between 20 and 80
    if (charging_rate < 20 || charging_rate > 80)
    {
        printk(KERN_WARNING, "Charging Rate should be between 20 and 80\n");
        return -1;
    }

    int retVal = acpi_battery_change_charging_rate(battery, charging_rate);

    // cannot change battery charging rate
    if (ACPI_FAILURE(retVal))
    {
        printk(KERN_INFO, "Unable to change battery charging rate\n");
        return -1;
    }

    return 0;
}

module_init(main);
