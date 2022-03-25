/*  
 * Module Description:
 *   ACPI Battery Driver module to change Battery Charging Rate
 *   These functions need to be either added to or need to replace the existing functions in /drivers/acpi/battery.c
 * 
 * Copyright (c) 2022 Shamith Achanta
 * Report bugs to Shamith Achanta <shamith2@illinois.edu>
 *
 * References:  https://github.com/torvalds/linux/blob/master/drivers/acpi/battery.c,
 *              https://www.kernel.org/doc/html/latest/filesystems/sysfs.html,
 *              https://uefi.org/specs/ACPI/6.4/10_Power_Source_and_Power_Meter_Devices/Power_Source_and_Power_Meter_Devices.html,
 *              https://blog.actorsfit.com/a?ID=00450-da0325ec-0e37-4921-8b3b-58d95db4ae9e
 *
 *
 * TODO: check on an actual Linux machine
 * How to change battery charging rate from user space using sysfs:
 *  sudo echo $[charging_rate] >> /sys/class/power_supply/$[battery_name]/charging_rate
 * 
 */

// local function prototypes
static int acpi_battery_change_charging_rate(struct acpi_battery *battery, const int charging_rate);
static ssize_t acpi_battery_change_charging_rate_show(struct device *dev, struct device_attribute *attr, char *buf);
static ssize_t acpi_battery_change_charging_rate_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count);


/* Add This Function to /drivers/acpi/battery.c */
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

/* Add This Struct to /drivers/acpi/battery.c */
/* Equivalent to:
 *  static DEVICE_ATTR("charging_rate", 0644, acpi_battery_change_charging_rate_show, acpi_battery_change_charging_rate_store);
 */
static const struct device_attribute battery_charge_rate_attr = {
	.attr = {.name = "charging_rate", .mode = 0644},
	.show = acpi_battery_change_charging_rate_show,
	.store = acpi_battery_change_charging_rate_store
};

/* Add This Function to /drivers/acpi/battery.c */
static ssize_t acpi_battery_change_charging_rate_show(struct device *dev, struct device_attribute *attr, char *buf)
{
	struct acpi_battery *battery = to_acpi_battery(dev_get_drvdata(dev));

	return sprintf(buf, "%d\n", battery->rate_now);
}

/* Add This Function to /drivers/acpi/battery.c */
static ssize_t acpi_battery_change_charging_rate_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    struct acpi_battery *battery = to_acpi_battery(dev_get_drvdata(dev));

    int charging_rate;

    // if buffer is not properly formatted
    if (sscanf(buf, "%d\n", &charging_rate) != 1)
    {
        return -EIO;
    }

    // change battery charging rate
    int retVal = acpi_battery_change_charging_rate(battery, charging_rate);

    // return an error if battery charging rate cannot be changed
    if (retVal)
    {
        return retVal;
    }
	
    return count;
}

/* Modify this Function in /drivers/acpi/battery.c */
static int sysfs_add_battery(struct acpi_battery *battery)
{
	struct power_supply_config psy_cfg = { .drv_data = battery, };
	bool full_cap_broken = false;

	if (!ACPI_BATTERY_CAPACITY_VALID(battery->full_charge_capacity) &&
	    !ACPI_BATTERY_CAPACITY_VALID(battery->design_capacity))
		full_cap_broken = true;

	if (battery->power_unit == ACPI_BATTERY_POWER_UNIT_MA) {
		if (full_cap_broken) {
			battery->bat_desc.properties =
			    charge_battery_full_cap_broken_props;
			battery->bat_desc.num_properties =
			    ARRAY_SIZE(charge_battery_full_cap_broken_props);
		} else {
			battery->bat_desc.properties = charge_battery_props;
			battery->bat_desc.num_properties =
			    ARRAY_SIZE(charge_battery_props);
		}
	} else {
		if (full_cap_broken) {
			battery->bat_desc.properties =
			    energy_battery_full_cap_broken_props;
			battery->bat_desc.num_properties =
			    ARRAY_SIZE(energy_battery_full_cap_broken_props);
		} else {
			battery->bat_desc.properties = energy_battery_props;
			battery->bat_desc.num_properties =
			    ARRAY_SIZE(energy_battery_props);
		}
	}

	battery->bat_desc.name = acpi_device_bid(battery->device);
	battery->bat_desc.type = POWER_SUPPLY_TYPE_BATTERY;
	battery->bat_desc.get_property = acpi_battery_get_property;

	battery->bat = power_supply_register_no_ws(&battery->device->dev,
				&battery->bat_desc, &psy_cfg);

	if (IS_ERR(battery->bat)) {
		int result = PTR_ERR(battery->bat);

		battery->bat = NULL;
		return result;
	}
	battery_hook_add_battery(battery);

    // -------->
    int retVal = device_create_file(&battery->bat->dev, &battery_charge_rate_attr);
    // -------->

	return device_create_file(&battery->bat->dev, &alarm_attr);
}

/* Modify this Function in /drivers/acpi/battery.c */
static void sysfs_remove_battery(struct acpi_battery *battery)
{
	mutex_lock(&battery->sysfs_lock);
	if (!battery->bat) {
		mutex_unlock(&battery->sysfs_lock);
		return;
	}
	battery_hook_remove_battery(battery);

    // -------->
    device_remove_file(&battery->bat->dev, &battery_charge_rate_attr);
    // -------->

	device_remove_file(&battery->bat->dev, &alarm_attr);
	power_supply_unregister(battery->bat);
	battery->bat = NULL;
	mutex_unlock(&battery->sysfs_lock);
}
