# evtplugins
OpenSesame Plugins for communication with the RUG/BSS Event Exchanger and Event Exchanger derivatives hardware.

The currently supported OpenSesame version is v3.3

The following plugin collection is available:

Plugin | Description | Status
------ | ----------- | ------
EVTxx | Event Exchanger variants | not validated
ResponseBox | Button response box variants with 1-4 buttons | not validated
RGB_Led_Control |  | not validated
TactileStimulator | Tactile Stimulator 0-5mA | validated
VAS |  | not validated
VAS2 |  | not validated

## Package dependencies
The plugins are dependent on the Python module pyevt and the underlying HIDAPI package.
[https://pypi.org/project/hidapi/](https://pypi.org/project/hidapi/)

pyevt and hidapi are installed from the Python Console in OpenSesame in a single command:
`!pip install --user pyevt`

## EVTxx

## ResponseBox

## RGB_Led_Control

## TactileStimulator
description ...

List of the variables that appear in the OpenSesame variable inspector:

variable name | description
------------- | -----------
shocker_calibration_perc | The percentage of the slider setting for the stimulus current of 5mA max.
shocker_calibration_milliamp | The calibration value of the stimulus current in mA's
shocker_calibration_value | The byte value representation of the calibrated current
shocker_shock_milliamp | The actual current in mA's, applied to the Tactile Stimulator hardware
shocker_shock_value | The actual byte value representation send to the Tactile Stimulator
shocker_time_last_shock | Unique time stamp in seconds from the moment of the last shock


## VAS

## VAS2

