# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Description
-----------
Start WWAN Burn tests.

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
      "pytest_name": "wwan_burn_test",
      "run_if": "device.component.has_lte",
      "label": "Wwan Burn",
      "args": {
        "timeout": 1,
        "autostart": true,
        "loop_time": 1
      }
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

BURN_L850_CHANGEPATH_CMD = "cd /usr/local/factory/fibocomm/L850/1003;"
BURN_L850_MOUNT_CMD = "mount /tmp -o remount,exec"
BURN_L850_CMD = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fDPR_HW_DOUBLETABLE"

BURN_NL668_CHANGEPATH_CMD = "cd /usr/local/factory/fibocomm/NL668;"
BURN_NL668_MOUNT_CMD = "mount /tmp -o remount,exec"
BURN_NL668_CMD = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fBODYSAR"

str_result_list = []

class WWANRSSITest(test_case.TestCase):

  ARGS = [
      Arg('timeout', int,
          'Timeout of the test.',
          default=200),
      Arg('autostart', bool, 'Auto start this test.',
          default=True),
      Arg('loop_time', int, 'Frequency of this test.',
          default=1)]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('WWAN Burn Test'))

  def wwanBurnL850(self):
      if self.args.loop_time:
          for loop in range(self.args.loop_time):
              #1,change path
              change_path_result = self._dut.CheckOutput(BURN_L850_CHANGEPATH_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_L850_CHANGEPATH_CMD, change_path_result))
              self.ui.SetState(_('Change Path cmd {item} result: {rea}.'.format(item=BURN_L850_CHANGEPATH_CMD, rea=change_path_result)))

              #2 mount
              mount_results = self._dut.CheckOutput(BURN_L850_MOUNT_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_L850_MOUNT_CMD, mount_results))
              self.ui.SetState(_('Mount cmd {item} result: {rea}.'.format(item=BURN_L850_MOUNT_CMD, rea=mount_results)))

              #3 burn
              burn_results = self._dut.CheckOutput(BURN_L850_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_L850_CMD, burn_results))
              self.ui.SetState(_('Burn cmd {item} result: {rea}.'.format(item=BURN_L850_CMD, rea=burn_results)))
              str_burn_result = burn_results.split(",")[1]
              str_result_list.append(str_burn_result)

              if str_burn_result == 'PASS':
                  return True
              time.sleep(1)

      return True

  def wwanBurnNL668(self):
      if self.args.loop_time:
          for loop in range(self.args.loop_time):
              #1,change path
              change_path_result = self._dut.CheckOutput(BURN_NL668_CHANGEPATH_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_NL668_CHANGEPATH_CMD, change_path_result))
              self.ui.SetState(_('Change Path cmd {item} result: {rea}.'.format(item=BURN_NL668_CHANGEPATH_CMD, rea=change_path_result)))

              #2 mount
              mount_results = self._dut.CheckOutput(BURN_NL668_MOUNT_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_NL668_MOUNT_CMD, mount_results))
              self.ui.SetState(_('Mount cmd {item} result: {rea}.'.format(item=BURN_NL668_MOUNT_CMD, rea=mount_results)))

              #3 burn
              burn_results = self._dut.CheckOutput(BURN_NL668_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (BURN_NL668_CMD, burn_results))
              self.ui.SetState(_('Burn cmd {item} result: {rea}.'.format(item=BURN_NL668_CMD, rea=burn_results)))
              str_burn_result = burn_results.split(",")[1]
              str_result_list.append(str_burn_result)

              if str_burn_result == 'PASS':
                  return True
              time.sleep(1)

      return True

  def runTest(self):
    self.ui.SetInstruction(
        _('WWAN Burn Test'))
    #logging.info('phy name is %s.', self._phy_name)
    self.ui.StartFailingCountdownTimer(self.args.timeout)

    #auto test
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

    #
    self.ui.SetState(_('WWAN Burn...'))
    check_result = ""
    for loop in range(20):
        check_module_cmd = "mmcli -L"
        check_result = self._dut.CheckOutput(check_module_cmd, log=True)
        if 'NL668' in check_result or 'L850-GL' in check_result:
            break
        else:
            self.Sleep(0.5)
            if loop > 19:
                self.FailTask(
                    "Module not present! Please check module state")

    if 'NL668' in check_result:
        self.wwanBurnNL668()
    elif 'L850-GL' in check_result:
        self.wwanBurnL850()
    else:
        self.FailTask(
            "Unknown Module Type!")
    session.console.info(str_result_list)
    if "FAIL" in str_result_list or "ERROR" in str_result_list:
        self.FailTask(
            "The result contains FAIL")

