#-*- coding:utf-8 -*-

"""
Author: Martin Stokroos, 2024

This plug-in is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this plug-in.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import math
import distutils.util
from time import sleep
from pyevt import EventExchanger
from libopensesame.item import Item
from libqtopensesame.items.qtautoplugin import QtAutoPlugin
from openexp.canvas import Canvas
from libopensesame.oslogging import oslogger
from openexp.keyboard import Keyboard

# constant
_DEVICE_GROUP = u'RSP-LT'

# global var
open_devices = {} # Store open device handles.


class RgbLedControl(Item):

    description = u"Plugin to send LED RGB data from \
        \r\nEventExchanger-based digital input/output device."

    # Reset plug-in to initial values.
    def reset(self):
        """Resets plug-in to initial values."""
        self.var.device = u'0: Keyboard'
        self.var.correct_response = u'1'
        self.var.allowed_responses = u'1;2;3'
        self.var.timeout = u'infinite'
        self.var.button1_color = "#000000"
        self.var.button2_color = "#000000"
        self.var.button3_color = "#000000"
        self.var.button4_color = "#000000"
        self.var.reset_delay = 500
        self.var.feedback = u'yes'
        self.var.correct_color = "#00FF00"
        self.var.incorrect_color = "#FF0000"

    def prepare(self):
        """The preparation phase of the plug-in goes here."""
        super().prepare()

        '''
        The next part calculates the bit mask for the allowed responses
        to receive from the RSP-12x.
        '''
        self.var.combined_allowed_events = 0
        try:
            list_allowed_buttons = self.var.allowed_responses.split(";")
            for x in list_allowed_buttons:
                self.var.combined_allowed_events +=  (1 << (int(x, 10) -1))
        except:
            # in case the input is one element
            x = self.var.allowed_responses
            self.var.combined_allowed_events =  (1 << (x-1))
            list_allowed_buttons = []
            list_allowed_buttons.append(x)
        #oslogger.info('{}'.format(list_allowed_buttons))
        #oslogger.info('{}'.format(self.var.combined_allowed_events))

        if self.var.device != u'0: Keyboard':
            # Create a shadow device list to find 'path' from the current selected device.
            # 'path' is an unique device ID.
            myevt = EventExchanger()
            sleep(0.1) # without a delay, the list will not always be complete.
            try:
                device_list = myevt.scan(_DEVICE_GROUP) # filter on allowed EVT types
                del myevt
                # oslogger.info("device list: {}".format(device_list))
            except:
                oslogger.warning("Connecting EVT device failed!")
            try:
                d_count = 1            
                for d in device_list:
                    if not d_count in open_devices: # skip if already open
                        # Dynamically load all EVT devices from the list
                        open_devices[d_count] = EventExchanger()
                        open_devices[d_count].attach_id(d['path']) # Get evt device handle
                        oslogger.info('Device successfully attached as:{} s/n:{}'.format(
                            d['product_string'], d['serial_number']))
                    d_count += 1
                oslogger.info('open devices: {}'.format(open_devices))
                self.current_device = int(self.var.device[:1])
                oslogger.info('Prepare - current device: {}'.format(self.current_device))
            except:
                self.var.device = u'0: Keyboard'
                oslogger.warning("Loading the RSP-12x-box failed! Default is keyboard")
                self.my_keyboard = Keyboard(self.experiment, 
                                    keylist=list_allowed_buttons,
                                    timeout=self.var.timeout if \
                                    type(self.var.timeout)==int else None)
        else:
            self.my_keyboard = Keyboard(self.experiment, 
                                keylist=list_allowed_buttons,
                                timeout=self.var.timeout if \
                                type(self.var.timeout)==int else None)

    def run(self):
        """The run phase of the plug-in goes here."""
        # Save the current time...
        t0 = self.set_item_onset()

        hexprepend = "0x"
        self.colors = [hexprepend + self.var.button1_color[1:],
                       hexprepend + self.var.button2_color[1:],
                       hexprepend + self.var.button3_color[1:],
                       hexprepend + self.var.button4_color[1:]]
        self.CorrectColor = hexprepend + self.var.correct_color[1:]
        self.InCorrectColor = hexprepend + self.var.incorrect_color[1:]
        CC = int(self.CorrectColor, 16)
        IC = int(self.InCorrectColor, 16)
        BLC = [0, 0, 0, 0]

        for b in range(4):
            BLC[b] = int(self.colors[b], 16)

        if self.var.device != u'0: Keyboard':
            for b in range(4):
                open_devices[self.current_device].set_led_rgb(
                    ((BLC[b] >> 16) & 0xFF),
                    ((BLC[b] >> 8) & 0xFF),
                    (BLC[b] & 0xFF),
                    b + 1, 1)

            if self.var.feedback == u'yes':
                for b in range(4):
                    open_devices[self.current_device].set_led_rgb(
                        ((IC >> 16) & 0xFF),
                        ((IC >> 8) & 0xFF),
                        (IC & 0xFF),
                        b + 1, b + 11)

                open_devices[self.current_device].set_led_rgb(
                    ((CC >> 16) & 0xFF),
                    ((CC >> 8) & 0xFF),
                    (CC & 0xFF),
                    int(self.var.correct_button),
                    int(self.var.correct_button) + 10)

            # Call the 'wait for event' function in \
            # the EventExchanger C# object.
            self.var.response, self.var.keyboard_response = \
                open_devices[self.current_device].wait_for_event(
                    self.var.combined_allowed_events, self.var.timeout if \
                    type(self.var.timeout)==int else None)

            if (self.var.response != -1):
                self.var.response = math.log2(self.var.response) + 1

            # Feedback:
            if self.var.feedback == u'yes':
                time.sleep(self.var.reset_delay / 1000.0)
                for b in range(4):
                    open_devices[self.current_device].set_led_rgb(0, 0, 0, b + 1, 1)
        else:
            # dummy-mode: keyboard response.....
            self.var.response, self.var.keyboard_response = \
                self.Keyboard.get_key()

        # HOUSE KEEPING:
        self.var.correct = \
            bool(self.var.response == self.var.correct_button)

        self.var.correct = distutils.util.strtobool(str(self.var.correct))

        print(self.var.correct)
        # Add all response related data to the Opensesame responses instance.
        self.experiment.responses.add(response_time=self.var.keyboard_response,
                                      correct=self.var.correct,
                                      response=self.var.response,
                                      item=self.name)


class QtRgbLedControl(RgbLedControl, QtAutoPlugin):

    """This class handles the GUI aspect of the plug-in. The name should be the
    same as that of the runtime class with the added prefix Qt.
    
    Important: defining a GUI class is optional, and only necessary if you need
    to implement non-standard interfaces or interactions. In this case, we use
    the GUI class to dynamically enable/ disable some controls (see below).
    """

    def __init__(self, name, experiment, script=None):
        # We don't need to do anything here, except call the parent
        # constructors. Since the parent constructures take different arguments
        # we cannot use super().
        RgbLedControl.__init__(self, name, experiment, script)
        QtAutoPlugin.__init__(self, __file__)

    def init_edit_widget(self):

        """Constructs the GUI controls. Usually, you can omit this function
        altogether, but if you want to implement more advanced functionality,
        such as controls that are grayed out under certain conditions, you need
        to implement this here.
        """

        super().init_edit_widget()

        self.combobox_add_devices() # first time fill the combobox

        # Event-triggered calls:
        self.refresh_checkbox.stateChanged.connect(self.refresh_combobox_device)
        self.device_combobox.currentIndexChanged.connect(self.update_combobox_device)
        self.timeout_line_edit.textChanged.connect(self.check_timeout_duration)

    def refresh_combobox_device(self):
        if self.refresh_checkbox.isChecked():
            # renew list:
            self.combobox_add_devices()

    def update_combobox_device(self):
        self.refresh_checkbox.setChecked(False)

    def check_timeout_duration(self, text):
        try:
            if text in u'infinite':
                self.var.timeout = None
            else:
                self.var.timeout = int(text)
                if not 0 <= self.var.timeout <= 3600000:
                    raise ValueError
        except ValueError:
            # Handle invalid input or out of range value
            self.timeout_line_edit.blockSignals(True)
            self.timeout_line_edit.setText('')
            self.timeout_line_edit.blockSignals(False)

    def combobox_add_devices(self):
        self.device_combobox.clear()
        self.device_combobox.addItem(u'0: Keyboard', userData=None)
        
        # Create the EVT device list
        myevt = EventExchanger()
        sleep(0.5) # without a delay, the list will not always be complete.
        try:
            device_list = myevt.scan(_DEVICE_GROUP) # filter on allowed EVT types
            del myevt
        except:
            device_list = None
        
        added_items_list = {}
        if device_list:
            d_count = 1
            for d in device_list:
                product_string = d['product_string']
                serial_string = d['serial_number']
                composed_string = str(d_count) + ": " + \
                    product_string[15:] + " s/n: " + serial_string
                # add device string to combobox:
                self.device_combobox.addItem(composed_string)
                added_items_list[d_count] = composed_string
                d_count += 1
                if d_count > 9:
                    # keep number of digits 1
                    break
        # Prevents hangup if the old device is not found after reopening the project.
        # Any change of the hardware configuration can cause this.
        if not self.var.device in added_items_list.values():
            self.var.device = u'0: Keyboard'
            oslogger.warning("The hardware configuration has been changed since the last run! Switching to dummy.")
