# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A factory test to verify SAR and cros_config values.

Description
-----------
The test run with the following steps::

1. Identify network controller vendor.
2. Verify values.
  - For Intel, check SAR value.
  - For Realtek, check cros_config values.

Test Procedure
--------------
This is an automated test without user interaction.

Dependency
----------
- gooftool API ``cros.factory.gooftool.cros_config``.
- gooftool API ``cros.factory.gooftool.crosfw``.

Examples
--------
To run the test, add this into test list::
  {
    "pytest_name": "sar"
  }
"""


import logging
import re
import tempfile

from cros.factory.test import test_case
from cros.factory.utils import type_utils
from cros.factory.utils import process_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.device import device_utils
from cros.factory.gooftool import cros_config
from cros.factory.gooftool import crosfw

SAR = '90787878789078787878A0A0A0A0A0A0A0A0A0A00000000000000\
00000000000000000000000000000A00000A00000800000881010800000881010'
VALUES = [
    ('tablet-mode-power-table-rtw', 'limit-2g', 144),
    ('tablet-mode-power-table-rtw', 'limit-5g-1', 120),
    ('tablet-mode-power-table-rtw', 'limit-5g-3', 120),
    ('tablet-mode-power-table-rtw', 'limit-5g-4', 120),
    ('non-tablet-mode-power-table-rtw', 'limit-2g', 160),
    ('non-tablet-mode-power-table-rtw', 'limit-5g-1', 160),
    ('non-tablet-mode-power-table-rtw', 'limit-5g-3', 160),
    ('non-tablet-mode-power-table-rtw', 'limit-5g-4', 160),
    ('geo-offsets-fcc', 'offset-2g', 0),
    ('geo-offsets-fcc', 'offset-5g', 0),
    ('geo-offsets-eu', 'offset-2g', 0),
    ('geo-offsets-eu', 'offset-5g', 16),
    ('geo-offsets-rest-of-world', 'offset-2g', 0),
    ('geo-offsets-rest-of-world', 'offset-5g', 16),
]

class SARTest(test_case.TestCase):
  ARGS = []

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._cros_config = cros_config.CrosConfig()

  def tearDown(self):
    pass

  def runTest(self):
    vendor = self._getVendor('Network controller')
    if 'intel' in vendor.lower():
      self.checkSar()
    else:
      self.checkValues()

  def checkSar(self):
    sar = self._getSar()
    if sar != SAR:
      logging.error('Expected value: {0}'.format(SAR))
      raise type_utils.TestFailure('Sar does not match.')

  def checkValues(self):
    success = True
    for path, key, value in VALUES:
      result = self._getCrosConfig('/wifi/'+path, key)
      if result != value:
        logging.error('Expected value: {0}'.format(value))
        success = False
    if not success:
      raise type_utils.TestFailure('Values do not match.')

  def _getVendor(self, Class):
    regex = re.compile(r'^(.*):\s*(.*)$', re.MULTILINE)
    output = process_utils.CheckOutput(['lspci', '-vmm'])
    for block in output.split('\n\n'):
      device = {k: v for k, v in regex.findall(block)}
      if device.get('Class', None) == Class:
        logging.info(block)
        return device.get('Vendor', None)
    logging.error(output)
    raise type_utils.TestFailure('{0} not found.'.format(Class))

  def _getSar(self):
    fw = crosfw.LoadMainFirmware()
    with tempfile.NamedTemporaryFile() as fp:
      process_utils.CheckCall(['cbfstool',
                               fw.GetFileName(), 'extract',
                               '-r', 'FW_MAIN_A',
                               '-n', 'wifi_sar-madoo.hex',
                               '-f', fp.name])
      sar = fp.read().decode().strip()
      logging.info('Intel Sar: {0}'.format(sar))
      return sar

  def _getCrosConfig(self, path, key):
    result = self._cros_config.GetValue(path, key)
    if result.stderr:
      logging.warning('cros_config stderr: {0}'.format(result.stderr))
    output = result.stdout
    logging.info('cros_config {0} {1}: {2}'.format(path, key, output).strip())
    return int(output.strip())
