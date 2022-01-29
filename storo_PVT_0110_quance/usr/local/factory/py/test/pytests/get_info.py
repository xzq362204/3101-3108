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
import re

from cros.factory.device import device_utils
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test import device_data

class CollectMacAddress(test_case.TestCase):

  ARGS = [
      Arg('manufacturer_id', int,
          'ID of the manufacturer.',
          default=29)]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()

  def runTest(self):
    #print device_data.GetDeviceData('device_data.component.fwupdate')
    rebootflag = self.dut.CallOutput('factory device-data -g component.fwupdate').strip()
    print("123"+str(rebootflag)+"456")
    if str(rebootflag) == 'True':
      device_data.UpdateDeviceData({'component.fwupdate': False})
      print('set False')
    else:
      device_data.UpdateDeviceData({'component.fwupdate': True})
      print('set True')
