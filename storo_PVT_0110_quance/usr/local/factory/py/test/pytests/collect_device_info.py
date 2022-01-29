# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import factory_common  # pylint: disable=unused-import

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import session
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test.utils import bluetooth_utils
import logging
import datetime

class CollectDeviceInfo(test_case.TestCase):
  """Collect device information from the DUT and send it to shopfloor(OEM demand)."""
  ARGS = [
      Arg('filter_colon', bool,
      'If true, wifi_mac and bluetooth_mac filter colon.', default=False),
      Arg('manufacturer_id', int,
          'ID of the manufacturer.',
          default=None)
  ]
  def setUp(self):
    self.assertIsNotNone(self.args.manufacturer_id,
                         'fail due to manufacturer_id is None, need to set it.')
    self.dut = device_utils.CreateDUTInterface()
    self.wifi_mac_address = None
    self.bt_address = None

  def runTest(self):
    mfg_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    rw_firmware_version = self.dut.CheckOutput(['crossystem', 'fwid'])
    release_image_version = self.dut.info.release_image_version
    self.wifi_mac_address = self.dut.info.wlan0_mac
    self.bt_address = bluetooth_utils.BtMgmt(self.args.manufacturer_id).GetMac()
    logging.info('wifi mac address: %s, bt address: %s',
                 self.wifi_mac_address, self.bt_address)
    if self.wifi_mac_address is None or self.bt_address is None:
      self.FailTask('Test fail due to the mac address is None.')
    if self.args.filter_colon:
      self.wifi_mac_address = self.wifi_mac_address.replace(':', '')
      self.bt_address = self.bt_address.replace(':', '')
    device_data.UpdateDeviceData(
      {'factory.wifi_mac': self.wifi_mac_address,
       'factory.bluetooth_mac': self.bt_address,
       'factory.fwid': rw_firmware_version,
       'factory.MFGDATE': mfg_date,
       'factory.release_image_version': release_image_version})
    session.console.info('Device data has been updated.')
