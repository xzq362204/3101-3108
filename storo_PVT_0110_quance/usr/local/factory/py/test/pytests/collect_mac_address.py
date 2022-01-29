"""
Description
-----------
Collecting BT/WIFI mac address for module.

Test Procedure
--------------
1. This test does not require operator interaction.
2. Read BT/WIFI mac address from DUT and set them into device_data.

Examples
--------
Minimum runnable example::
  {
    "pytest_name": "collect_mac_address",
    "args": {
      "manufacturer_id": 29
    }
  }
"""
import logging

import factory_common  # pylint: disable=unused-import
from cros.factory.device import device_utils
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test.utils import bluetooth_utils
from cros.factory.test import device_data

KEY_WIFI_MAC_ADDRESS = 'factory.wifi_mac_address'
KEY_BT_MAC_ADDRESS = 'factory.bt_mac_address'

class CollectMacAddress(test_case.TestCase):

  ARGS = [
      Arg('manufacturer_id', int,
          'ID of the manufacturer.',
          default=None)]

  def setUp(self):
    self.assertIsNotNone(self.args.manufacturer_id,
                         'fail due to manufacturer_id is None, need to set it.')
    self.dut = device_utils.CreateDUTInterface()
    self.wifi_mac_address = None
    self.bt_address = None

  def runTest(self):
    self.wifi_mac_address = self.dut.info.wlan0_mac
    self.bt_address = bluetooth_utils.BtMgmt(self.args.manufacturer_id).GetMac()
    logging.info('wifi mac address: %s, bt address: %s',
                 self.wifi_mac_address, self.bt_address)
    if self.wifi_mac_address is None or self.bt_address is None:
      self.FailTask('Test fail due to the mac address is None.')

    device_data.UpdateDeviceData({KEY_WIFI_MAC_ADDRESS: self.wifi_mac_address})
    device_data.UpdateDeviceData({KEY_BT_MAC_ADDRESS: self.bt_address})
