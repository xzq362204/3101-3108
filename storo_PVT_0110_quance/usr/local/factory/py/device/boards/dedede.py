# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging

from cros.factory.device.boards import chromeos
from cros.factory.device import device_types
from cros.factory.device import led
from cros.factory.device import thermal


class _ECToolTemperatureSensors(thermal.ECToolTemperatureSensors):
  # https://chromium.googlesource.com/chromiumos/platform/ec/+/refs/heads/master/board/drawcia/board.h#121
  CHANNELS = {
      '0': 1,
      '1': 2,
      '2': 4,
      '3': 5
  }

  def GetValue(self, sensor):
    """Gets one single value with "temps" command."""
    sensor_id = self.GetSensors()[sensor]
    # 'ectool temps' prints a message like Reading 'temperature...(\d+)'
    retval = self._ConvertRawValue(
        self._device.CallOutput(
            'ectool temps %s' % sensor_id).rpartition('.')[2])
    if retval is None:
      channel = self.CHANNELS[sensor_id]
      output = self._device.CallOutput(['ectool', 'adcread', str(channel)])
      logging.warning('Failed to read thermal %s: %s', sensor_id, output)

    return retval

  def GetAllValues(self):
    """Returns all ectool temps values.

    ectool has a quick command 'temps all' that is faster then iterating all
    sensor with GetValue, so we want to implement GetAllValues explicitly.
    """
    raw_values = dict(self.ECTOOL_TEMPS_ALL_RE.findall(
        self._device.CallOutput('ectool temps all')))

    # Remap ID to cached names.
    values = {name: self._ConvertRawValue(raw_values.get(sensor_id))
            for name, sensor_id in self.GetSensors().items()}
    for sensor, value in values.items():
      if value is None:
        sensor_id = self.GetSensors()[sensor]
        channel = self.CHANNELS[sensor_id]
        output = self._device.CallOutput(['ectool', 'adcread', str(channel)])
        logging.warning('Failed to read thermal %s: %s', sensor_id, output)
    return values


class DededeThermal(thermal.Thermal):
  def _SetupSensors(self):
    """Configures available sensors.

    Derived implementations can override this to modify the priority and type of
    sensors.
    """
    self._sensors = {}
    self._main_sensor = None
    self._sources = []

    # CoreTemp should be considered as the better alternative than ThermalZone.
    self._AddThermalSensorSource(thermal.CoreTempSensors(self._device))
    if not self._main_sensor:
      self._AddThermalSensorSource(thermal.ThermalZoneSensors(self._device))
    # ECTool provides additional sensors.
    self._AddThermalSensorSource(_ECToolTemperatureSensors(self._device))


class DededeBoard(chromeos.ChromeOSBoard):
  """Board implementation for Dedede."""
  @device_types.DeviceProperty
  def led(self):
    return led.BatteryPowerLED(self)

  # TODO(b/164256608): revert this change when the issue is solved.
  @device_types.DeviceProperty
  def thermal(self):
    return DededeThermal(self)
