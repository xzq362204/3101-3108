# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Description
-----------
Start Collect WWAN Log.

Test Procedure
--------------
autotest

Dependency
----------
qmicli -p -d qrtr://0 --nas-get-signal-strength

Examples
--------
Minimum runnable example::

  {
    "pytest_name": "wireless_log"
  }

 
"""


import re
import time
import logging

#import factory_common  # pylint: disable=unused-import
from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test import test_ui
from cros.factory.test import session
# WWAN RSSI command
#RSSI_CMD = "qmicli -p -d qrtr://0 --nas-get-signal-strength | grep -iA 1 RSSI | sed -n 2p | cut -d' ' -f3"
#RSSI_CMD = "cat /media/rssi.txt | grep -iA 1 RSSI | sed -n 2p | cut -d' ' -f3"
"""
"""

WWAN_DMSG_LOG_CMD = "cd /; ./dmesg>dmsg.log"
WWAN_SSDT_LOG_CMD = "cat /sys/firmware/acpi/tables/SSDT>/root/SSDT"
WWAN_VPD_LOG_CMD = "vpd -g wifi_sar > vpdwifisar.log"


class WWANLogTest(test_case.TestCase):

  ARGS = [
      Arg('timeout', int,
          'Timeout of the test.',
          default=30),
      Arg('autostart', bool, 'Auto start this test.',
          default=False),
      Arg('loop_time', int, 'Frequency of this test.',
          default=1)]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('WWAN Log Test'))

  def runTest(self):
    self.ui.SetInstruction(
        _('WWAN Log Test'))
    #logging.info('phy name is %s.', self._phy_name)
    self.ui.StartFailingCountdownTimer(self.args.timeout)
    if self.args.autostart:
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

    self.ui.SetState(_('WWAN Log testing...'))
    for loop in range(self.args.loop_time):        
        DMSG_results = self._dut.CheckOutput(WWAN_DMSG_LOG_CMD, log=True)
        session.console.info("cmd : %s return: %s." % (WWAN_DMSG_LOG_CMD, DMSG_results))
        self.ui.SetState(_('{item} capature Log finished'
                                 'return: {rea}.'.format(item=WWAN_DMSG_LOG_CMD, rea=DMSG_results)))
        
        SSDT_results = self._dut.CheckOutput(WWAN_SSDT_LOG_CMD, log=True)
        session.console.info("cmd : %s return: %s." % (WWAN_SSDT_LOG_CMD, SSDT_results))
        self.ui.SetState(_('{item} capature Log finished'
                                 'return: {rea}.'.format(item=WWAN_SSDT_LOG_CMD, rea=SSDT_results)))

        VPD_results = self._dut.CheckOutput(WWAN_VPD_LOG_CMD, log=True)
        session.console.info("cmd : %s return: %s." % (WWAN_VPD_LOG_CMD, VPD_results))
        self.ui.SetState(_('{item} capature Log finished'
                                 'return: {rea}.'.format(item=WWAN_VPD_LOG_CMD, rea=VPD_results)))

     
