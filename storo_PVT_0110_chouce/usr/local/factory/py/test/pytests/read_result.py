# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Description
-----------
Check info write from mes
like: skuid/fw_config/dram partnumber/ssfc and so on

method:
get messages from cbi
use ectool cbi get 2/0/4/6/8
and then cpmpare with data from component
like component.skuid = 17316 or 0xA0001

args:
check flags:
skuid_check  true or false
dram_partnumber_check true or false
fw_config_check true or false
ssfc_check true or false

"""


import re
import time
import logging
import subprocess
import binascii

#import factory_common  # pylint: disable=unused-import
from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test import test_ui
from cros.factory.test import session
from cros.factory.test import device_data

class ReadResult(test_case.TestCase):

  ARGS = [
      Arg('autostart', bool, 'Auto start this test.',
          default=False),
      Arg('timeout', int,
          'Timeout of the test.',
          default=200)
      ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('Read test result'))

  def InfoCheck(self, datatype):
      result = False

  def InfoCheck(self):
      totalresult = False
      self.ui.SetState(_('read result.txt'))
      with open(r'/usr/local/factory/wifi/rear_camera_result.txt', 'r') as f:
        print(f)
        lines = f.readlines()
        testresult = lines[-1]
        session.console.info("Get result is:%s" % testresult)
      if "PASS" in testresult:
        totalresult = True
      return totalresult

  def runTest(self):
    self.ui.SetInstruction(
        _('Read test result'))
    if not self.args.autostart:
      self.ui.SetState(
          _('Please press space to start testing.'))
      session.console.info("Please press space to start testing.")
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)
      self.ui.SetState(
          _('SPCAE_KEY Down. Start testing.'))
      session.console.info("SPCAE_KEY Down. Start testing.")
      self.ui.SetState(
          _('Wait 1 seconds.'))
    time.sleep(1)
    self.ui.StartFailingCountdownTimer(self.args.timeout)
    self.ui.SetState(_('read test result...'))

    result = self.InfoCheck()
    if result is False:
        self.FailTask(
            "result failed")
