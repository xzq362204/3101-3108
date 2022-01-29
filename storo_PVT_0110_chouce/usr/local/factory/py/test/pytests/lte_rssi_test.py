# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Description
-----------
Start WWAN RSSI tests.

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
    "pytest_name": "lte_rssi_test"
  }


  def main_antenna(self):
      cmd = "/usr/local/factory/board/diag-router &"
      self._dut.CheckOutput(cmd, log=True)
      main_strength = self.signalstrength()
      if main_strength < -83 or main_strength > -40:
          self.FailTask(
              "The signal strength of MAIN antenna is %sdBm "
              "not in [-83dBm,-40dBm], the strength is not valid..." % main_strength)
      else:
          session.console.info("The signal strength of MAIN antenna is %sdBm." % main_strength)

  def aux_antenna(self):
      cmd = "/usr/local/factory/board/send_data 75 85 1 0 4 2"
      self._dut.CheckOutput(cmd, log=True)
      aux_strength = self.signalstrength()
      if aux_strength < -83 or aux_strength > -40:
          self.FailTask(
              "The signal strength of AUX antenna is %sdBm "
              "not in [-83dBm,-40dBm], the strength is not valid..." % aux_strength)
      else:
          session.console.info("The signal strength of AUX antenna is %sdBm." % aux_strength)
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

WWAN_RSSI_MOUNT_CMD = "mount /tmp -o remount,exec"
WWAN_RSSI_LTE_MAIN_CMD = "cd /usr/local/factory/fibocomm/L850;./FIBOCOM_MT_V1.0.0.5 -fLTE_RX_RSSI_MAIN 4 2175 -80 20"
WWAN_RSSI_LTE_AUX_CMD = "cd /usr/local/factory/fibocomm/L850;./FIBOCOM_MT_V1.0.0.5 -fLTE_RX_RSSI_DIV 4 2175 -80 20"

NL668_MOUNT_CMD = "mount /tmp -o remount,exec"
NL668_CMD1 = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fSET_FTM_MODE"
NL668_CMD2 = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fLTE_RX_RSSI_MAIN 4 20175 -55 20"
NL668_CMD3 = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fLTE_RX_RSSI_DIV 4 20175 -55 20"
NL668_CMD4 = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fSET_ONLINE_MODE"
str_result_list = []

class LteRSSITest(test_case.TestCase):

  ARGS = [
      Arg('timeout', int,
          'Timeout of the test.',
          default=200),
      Arg('autostart', bool, 'Auto start this test.',
          default=False),
      Arg('loop_time', int, 'Frequency of this test.',
          default=1),
      Arg('only_check_presence', bool, 'Only check module presence.',
          default=False)]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('WWAN RSSI Test'))

  def isfloat(self, value):
      try:
          float(value)
          return True
      except ValueError:
          return False

  def getwwanrssiL850(self, test_cmd, para):
      rssi_result_list = []
      if self.args.loop_time:
          for loop in range(self.args.loop_time):
              rssi_results = self._dut.CheckOutput(test_cmd, log=True)
              session.console.info("cmd : %s return: %s." % (test_cmd, rssi_results))
              self.ui.SetState(_('{item} RSSI capature finished'
                                 'return: {rea}.'.format(item=para, rea=rssi_results)))
              str_2 = rssi_results.split(",")[2]
              flag1 = self.isfloat(str_2)
              rssi_result = rssi_results.split(",")[1]
              str_result_list.append(rssi_result)
              if flag1 is True:
                  rssi_strength = float(rssi_results.split(",")[2])
              else:
                  continue
              self.ui.SetState(_('Current {item} rssi result is {rea}.'.format(item=para, rea=rssi_result)))
              session.console.info("Current rssi result is %s ." % rssi_result)
              self.ui.SetState(_('Current {item} rssi strength is {rea}.'.format(item=para, rea=rssi_strength)))
              session.console.info("Current rssi signal strength is %sdBm." % rssi_strength)
              rssi_result_list.append(rssi_strength)
              time.sleep(1)
      rssi_result_total = 0
      for res in rssi_result_list:
          rssi_result_total += res
      rssi_result = rssi_result_total / self.args.loop_time
      return rssi_result

  def getwwanrssiNL668(self):
      main_rssi_result_list = []
      aux_rssi_result_list = []
      count = self.args.loop_time
      if self.args.loop_time:
          for loop in range(self.args.loop_time):
              #0
              mount_result = self._dut.CheckOutput(NL668_MOUNT_CMD, log=True)
              session.console.info("cmd : %s return: %s." % (NL668_MOUNT_CMD, mount_result))
              #1
              rssi_results = self._dut.CheckOutput(NL668_CMD1, log=True)
              session.console.info("cmd : %s return: %s." % (NL668_CMD1, rssi_results))
              self.ui.SetState(_('Set FTM mode,'
                                 'return: {rea}.'.format(rea=rssi_results)))
              str_rssi_result = rssi_results.split(",")[1]
              str_result_list.append(str_rssi_result)
              #2
              rssi_results = self._dut.CheckOutput(NL668_CMD2, log=True)
              session.console.info("cmd : %s return: %s." % (NL668_CMD2, rssi_results))
              self.ui.SetState(_('Get main rssi,'
                                 'return: {rea}.'.format(rea=rssi_results)))
              str_rssi_result = rssi_results.split(",")[1]
              str_result_list.append(str_rssi_result)
              str_2 = rssi_results.split(",")[2]
              flag1 = self.isfloat(str_2)
              if flag1 is True:
                  rssi_strength = float(rssi_results.split(",")[2])
              else:
                  count-=1
                  rssi_results = self._dut.CheckOutput(NL668_CMD4, log=True)
                  session.console.info("cmd : %s return: %s." % (NL668_CMD4, rssi_results))
                  self.ui.SetState(_('Set online mode,'
                                     'return: {rea}.'.format(rea=rssi_results)))
                  continue
              #3
              main_rssi_result_list.append(rssi_strength)
              rssi_results = self._dut.CheckOutput(NL668_CMD3, log=True)
              session.console.info("cmd : %s return: %s." % (NL668_CMD3, rssi_results))
              self.ui.SetState(_('Get main rssi,'
                                 'return: {rea}.'.format(rea=rssi_results)))
              str_rssi_result = rssi_results.split(",")[1]
              str_result_list.append(str_rssi_result)
              str_2 = rssi_results.split(",")[2]
              flag1 = self.isfloat(str_2)
              if flag1 is True:
                  rssi_strength = float(rssi_results.split(",")[2])
              else:
                  rssi_results = self._dut.CheckOutput(NL668_CMD4, log=True)
                  session.console.info("cmd : %s return: %s." % (NL668_CMD4, rssi_results))
                  self.ui.SetState(_('Set online mode,'
                                     'return: {rea}.'.format(rea=rssi_results)))
                  continue
              #4
              aux_rssi_result_list.append(rssi_strength)
              rssi_results = self._dut.CheckOutput(NL668_CMD4, log=True)
              session.console.info("cmd : %s return: %s." % (NL668_CMD4, rssi_results))
              self.ui.SetState(_('Set online mode,'
                                 'return: {rea}.'.format(rea=rssi_results)))
              str_rssi_result = rssi_results.split(",")[1]
              str_result_list.append(str_rssi_result)
              time.sleep(1)
      rssi_result_total = 0
      for res in main_rssi_result_list:
          rssi_result_total += res
      if count > 0:
          main_rssi_result = rssi_result_total / count
      else:
          main_rssi_result = rssi_result_total / self.args.loop_time

      session.console.info("WWAN Main rssi avg:%s." % main_rssi_result)
      rssi_result_total = 0
      for res in aux_rssi_result_list:
          rssi_result_total += res
      if count > 0:
          aux_rssi_result = rssi_result_total / count
      else:
          aux_rssi_result = rssi_result_total / self.args.loop_time

      session.console.info("WWAN Aux rssi avg:%s." % aux_rssi_result)
      return True

  def runTest(self):
    self.ui.SetInstruction(
        _('WWAN RSSI Test'))
    #logging.info('phy name is %s.', self._phy_name)
    self.ui.StartFailingCountdownTimer(self.args.timeout)
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

    self.ui.SetState(_('WWAN RSSI testing...'))
    check_result = ""
    for loop in range(20):
        check_module_cmd = "mmcli -L"
        check_result = self._dut.CheckOutput(check_module_cmd, log=True)
        session.console.info("cmd : %s return: %s." % (check_module_cmd, check_result))
        self.ui.SetState(_('{item} Detect Lte'
                                 'return: {rea}.'.format(item=check_module_cmd, rea=check_result)))
        if 'NL668' in check_result or 'L850-GL' in check_result:
            if self.args.only_check_presence:
                return True
            else:
                break
        else:
            self.Sleep(0.5)
            if loop > 19:
                self.FailTask(
                    "Module not present! Please check module state")

    if 'NL668' in check_result:
        self.getwwanrssiNL668()
    elif 'L850-GL' in check_result:
        mount_result = self._dut.CheckOutput(WWAN_RSSI_MOUNT_CMD, log=True)
        session.console.info("cmd : %s return: %s." % (WWAN_RSSI_MOUNT_CMD, mount_result))
        self.getwwanrssiL850(WWAN_RSSI_LTE_MAIN_CMD, "lte_main")
        self.getwwanrssiL850(WWAN_RSSI_LTE_AUX_CMD, "lte_aux")
    else:
        self.FailTask(
            "Unknown Module Type!")
    session.console.info(str_result_list)
    if "FAIL" in str_result_list or "ERROR" in str_result_list:
        self.FailTask(
            "The result contains FAIL")
    #cmd = "ps -aux | grep -i diag-router | head -n1 | awk -F' ' '{print$2}'"
    #pid = self._dut.CheckOutput(cmd, log=True)
    #self.ui.SetState(_('return: {rea}.', rea=pid))
    #logging.info('cmd:{cmd} return:{result}.',cmd=cmd, result=pid)
    #kill_cmd = "kill -9 " + pid
    #self._dut.CheckOutput(kill_cmd, log=True)
    #time.sleep(4)
