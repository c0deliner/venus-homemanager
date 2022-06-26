#!/usr/bin/env python3

import contextlib
import logging
from gi.repository import GLib as gobject
from dbus.mainloop.glib import DBusGMainLoop
import sys
import os
import _thread as thread
from homemeanger_decoder import HomeManager20, MCAST_GRP

# necessary packages from victron
sys.path.insert(1, os.path.join(os.path.dirname(__file__), './ext/velib_python'))
from vedbus import VeDbusService

VERSION = '2022.25'


class DbusSmaService:
    def __init__(self, servicename, deviceinstance, productname='Home Manager 2.0 dbus-bridge'):
        self.home_manager = HomeManager20()
        self.home_manager.read_data()
        self._dbusservice = VeDbusService(servicename)
        logging.debug(f"{servicename} /DeviceInstance = {deviceinstance}")

        # Register management objects, see dbus-api for more information
        self._dbusservice.add_path('/Mgmt/ProcessName', productname)
        self._dbusservice.add_path('/Mgmt/ProcessVersion', VERSION)
        self._dbusservice.add_path('/Mgmt/Connection', f'TCP/IP multicast group {MCAST_GRP}')

        # Register mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        self._dbusservice.add_path('/ProductId', 45058)  # value used in ac_sensor_bridge.cpp of dbus-cgwacs
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/FirmwareVersion', self.home_manager.hmdata['fw_version'])
        self._dbusservice.add_path('/HardwareVersion', 0)
        self._dbusservice.add_path('/Connected', 1)
        self._dbusservice.add_path('/Serial', self.home_manager.hmdata['serial'])
        self._dbusservice.add_path('/Ac/Power', 0, gettextcallback=self._get_text_for_w)
        self._dbusservice.add_path('/Ac/L1/Voltage', 0, gettextcallback=self._get_text_for_v)
        self._dbusservice.add_path('/Ac/L2/Voltage', 0, gettextcallback=self._get_text_for_v)
        self._dbusservice.add_path('/Ac/L3/Voltage', 0, gettextcallback=self._get_text_for_v)
        self._dbusservice.add_path('/Ac/L1/Current', 0, gettextcallback=self._get_text_for_a)
        self._dbusservice.add_path('/Ac/L2/Current', 0, gettextcallback=self._get_text_for_a)
        self._dbusservice.add_path('/Ac/L3/Current', 0, gettextcallback=self._get_text_for_a)
        self._dbusservice.add_path('/Ac/L1/Power', 0, gettextcallback=self._get_text_for_w)
        self._dbusservice.add_path('/Ac/L2/Power', 0, gettextcallback=self._get_text_for_w)
        self._dbusservice.add_path('/Ac/L3/Power', 0, gettextcallback=self._get_text_for_w)
        self._dbusservice.add_path('/Ac/L1/Energy/Forward', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/L2/Energy/Forward', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/L3/Energy/Forward', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/L1/Energy/Reverse', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/L2/Energy/Reverse', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/L3/Energy/Reverse', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/Energy/Forward', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/Energy/Reverse', 0, gettextcallback=self._get_text_for_kwh)
        self._dbusservice.add_path('/Ac/Current', 0, gettextcallback=self._get_text_for_a)

        gobject.timeout_add(1000, self._update)

    def _update(self):
        self.home_manager.read_data()
        with contextlib.suppress(KeyError):
            current = round((self.home_manager.hmdata['current_L1'] + self.home_manager.hmdata['current_L2'] +
                             self.home_manager.hmdata['current_L3']) / 3, 3)
            self._dbusservice['/Ac/Current'] = current
            self._dbusservice['/Ac/Power'] = self.home_manager.hmdata['positive_active_demand'] - \
                                             self.home_manager.hmdata['negative_active_demand']
            self._dbusservice['/Ac/Energy/Forward'] = self.home_manager.hmdata['positive_active_energy']
            self._dbusservice['/Ac/Energy/Reverse'] = self.home_manager.hmdata['negative_active_energy']
            self._dbusservice['/Ac/L1/Voltage'] = self.home_manager.hmdata['voltage_L1']
            self._dbusservice['/Ac/L2/Voltage'] = self.home_manager.hmdata['voltage_L2']
            self._dbusservice['/Ac/L3/Voltage'] = self.home_manager.hmdata['voltage_L3']
            self._dbusservice['/Ac/L1/Current'] = self.home_manager.hmdata['current_L1']
            self._dbusservice['/Ac/L2/Current'] = self.home_manager.hmdata['current_L2']
            self._dbusservice['/Ac/L3/Current'] = self.home_manager.hmdata['current_L3']
            self._dbusservice['/Ac/L1/Power'] = self.home_manager.hmdata['positive_active_demand_L1'] - \
                                                self.home_manager.hmdata['negative_active_demand_L1']
            self._dbusservice['/Ac/L2/Power'] = self.home_manager.hmdata['positive_active_demand_L2'] - \
                                                self.home_manager.hmdata['negative_active_demand_L2']
            self._dbusservice['/Ac/L3/Power'] = self.home_manager.hmdata['positive_active_demand_L3'] - \
                                                self.home_manager.hmdata['negative_active_demand_L3']
            self._dbusservice['/Ac/L1/Energy/Forward'] = self.home_manager.hmdata['positive_active_energy_L1']
            self._dbusservice['/Ac/L2/Energy/Forward'] = self.home_manager.hmdata['positive_active_energy_L2']
            self._dbusservice['/Ac/L3/Energy/Forward'] = self.home_manager.hmdata['positive_active_energy_L3']
            self._dbusservice['/Ac/L1/Energy/Reverse'] = self.home_manager.hmdata['negative_active_energy_L1']
            self._dbusservice['/Ac/L2/Energy/Reverse'] = self.home_manager.hmdata['negative_active_energy_L2']
            self._dbusservice['/Ac/L3/Energy/Reverse'] = self.home_manager.hmdata['negative_active_energy_L3']
        return True

    def _handle_changed_value(self, value):
        logging.debug(f"Object {self} has been changed to {value}")
        return True

    def _get_text_for_kwh(self, path, value):
        return "%.3FkWh" % (float(value) / 1000.0)

    def _get_text_for_w(self, path, value):
        return "%.1FW" % (float(value))

    def _get_text_for_v(self, path, value):
        return "%.2FV" % (float(value))

    def _get_text_for_a(self, path, value):
        return "%.2FA" % (float(value))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    thread.daemon = True
    DBusGMainLoop(set_as_default=True)
    DbusSmaService(servicename='com.victronenergy.grid.tcpip_239_12_255_254', deviceinstance=40)
    logging.info('Connected to dbus, switching over to gobject.MainLoop()')
    mainloop = gobject.MainLoop()
    mainloop.run()
