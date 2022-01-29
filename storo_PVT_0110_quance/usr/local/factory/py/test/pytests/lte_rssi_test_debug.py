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
WWAN_RSSI_WCDMA_MAIN_CMD = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 1 10700 -60 20"
WWAN_RSSI_WCDMA_AUX_CMD = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 1 10700 -60 20"
WWAN_RSSI_LTE_MAIN_CMD = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 4 2000 -60 20"
WWAN_RSSI_LTE_AUX_CMD = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 4 2000 -60 20"


#WWAN_RSSI_CMD1 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 1 10700 -80 20"
WWAN_CMD1 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 1 10700 -80 20"
WWAN_CMD2 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 1 10700 -80 20"
WWAN_CMD3 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 2 9800 -80 20"
WWAN_CMD4 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 2 9800 -80 20"
WWAN_CMD5 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 4 1638 -80 20"
WWAN_CMD6 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 4 1638 -80 20"
WWAN_CMD7 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 5 4408 -80 20"
WWAN_CMD8 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 5 4408 -80 20"
WWAN_CMD9 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_MAIN 8 3013 -80 20"
WWAN_CMD10 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fWCDMA_RX_RSSI_DIV 8 3013 -80 20"
WWAN_CMD11 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 1 300 -80 20"
WWAN_CMD12 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 1 300 -80 20"
WWAN_CMD13 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 2 900 -80 20"
WWAN_CMD14 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 2 900 -80 20"
WWAN_CMD15 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 3 1575 -80 20"
WWAN_CMD16 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 3 1575 -80 20"
WWAN_CMD17 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 4 2175 -80 20"
WWAN_CMD18 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 4 2175 -80 20"
WWAN_CMD19 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 5 2525 -80 20"
WWAN_CMD20 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 5 2525 -80 20"
WWAN_CMD21 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 7 3100 -80 20"
WWAN_CMD22 = "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 7 3100 -80 20"
WWAN_CMD23= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 8 3625 -80 20"
WWAN_CMD24= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 8 3625 -80 20"
WWAN_CMD25= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 11 4580 -80 20"
WWAN_CMD26= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 11 4580 -80 20"
WWAN_CMD27= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 12 5095 -80 20"
WWAN_CMD28= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 12 5095 -80 20"
WWAN_CMD29= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 13 23230 -80 20"
WWAN_CMD30= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 13 23230 -80 20"
WWAN_CMD31= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 17 5790 -80 20"
WWAN_CMD32= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 17 5790 -80 20"
WWAN_CMD33= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 18 5925 -80 20"
WWAN_CMD34= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 18 5925 -80 20"
WWAN_CMD35= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 19 6075 -80 20"
WWAN_CMD36= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 19 6075 -80 20"
WWAN_CMD37= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 20 24300 -80 20"
WWAN_CMD38= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 20 24300 -80 20"
WWAN_CMD39= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 21 6525 -80 20"
WWAN_CMD40= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 21 6525 -80 20"
WWAN_CMD41= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 26 8865 -80 20"
WWAN_CMD42= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 26 8865 -80 20"
WWAN_CMD43= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 28 9435 -80 20"
WWAN_CMD44= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 28 9435 -80 20"
WWAN_CMD45= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 30 9820 -80 20"
WWAN_CMD46= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 30 9820 -80 20"
WWAN_CMD47= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_MAIN 66 66886 -80 20"
WWAN_CMD48= "cd /usr/local/factory/fibocomm/L850/1003;./FIBOCOM_MT_V1.0.0.3 -fLTE_RX_RSSI_DIV 66 66886 -80 20"


NL668_MOUNT_CMD = "mount /tmp -o remount,exec"
NL668_CMD1 = "cd /usr/local/factory/fibocomm/NL668/100;./FIBOCOM_MT_V1.0.0 -fSET_FTM_MODE"
NL668_CMD2 = "cd /usr/local/factory/fibocomm/NL668/100;./FIBOCOM_MT_V1.0.0 -fLTE_RX_RSSI_MAIN 2 18900 -50 20"
NL668_CMD3 = "cd /usr/local/factory/fibocomm/NL668/100;./FIBOCOM_MT_V1.0.0 -fLTE_RX_RSSI_DIV 2 18900 -50 20"
NL668_CMD4 = "cd /usr/local/factory/fibocomm/NL668/100;./FIBOCOM_MT_V1.0.0 -fSET_ONLINE_MODE"
str_result_list = []

class LteRSSITest(test_case.TestCase):

  ARGS = [
      Arg('timeout', int,
          'Timeout of the test.',
          default=2000),
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
      pass_count = 0
      if self.args.loop_time:
          for loop in range(1):
              rssi_results = self._dut.CheckOutput(test_cmd, log=True)
              #session.console.info("cmd : %s return: %s." % (test_cmd, rssi_results))
              #self.ui.SetState(_('{item} RSSI capature finished'
              #                   'return: {rea}.'.format(item=para, rea=rssi_results)))
              str_2 = rssi_results.split(",")[2]
              flag1 = self.isfloat(str_2)
              rssi_result = rssi_results.split(",")[1]
              str_result_list.append(rssi_result)
              if flag1 is True:
                  rssi_strength = float(rssi_results.split(",")[2])
              else:
                  continue

              if rssi_result == "PASS":
                pass_count += 1

              #self.ui.SetState(_('Current {item} rssi result is {rea}.'.format(item=para, rea=rssi_result)))
              #session.console.info("Current rssi result is %s ." % rssi_result)
              #self.ui.SetState(_('Current {item} rssi strength is {rea}.'.format(item=para, rea=rssi_strength)))
              #session.console.info("Current rssi signal strength is %sdBm." % rssi_strength)
              rssi_result_list.append(rssi_strength)
              #time.sleep(1)
      rssi_result_total = 0
      for res in rssi_result_list:
          rssi_result_total += res
      rssi_result = rssi_result_total / self.args.loop_time

      #session.console.info("%s:PassCount[ %d ] test_cmd:%s "%(para, pass_count, test_cmd))
      #time.sleep(1)
      return pass_count

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


    WWAN_CMD_COUNT1 = 0
    WWAN_CMD_COUNT2 = 0
    WWAN_CMD_COUNT3 = 0
    WWAN_CMD_COUNT4 = 0
    WWAN_CMD_COUNT5 = 0
    WWAN_CMD_COUNT6 = 0
    WWAN_CMD_COUNT7 = 0
    WWAN_CMD_COUNT8 = 0
    WWAN_CMD_COUNT9 = 0
    WWAN_CMD_COUNT10 = 0
    WWAN_CMD_COUNT11 = 0
    WWAN_CMD_COUNT12 = 0
    WWAN_CMD_COUNT13 = 0
    WWAN_CMD_COUNT14 = 0
    WWAN_CMD_COUNT15 = 0
    WWAN_CMD_COUNT16 = 0
    WWAN_CMD_COUNT17 = 0
    WWAN_CMD_COUNT18 = 0
    WWAN_CMD_COUNT19 = 0
    WWAN_CMD_COUNT20 = 0
    WWAN_CMD_COUNT21 = 0
    WWAN_CMD_COUNT22 = 0
    WWAN_CMD_COUNT23 = 0
    WWAN_CMD_COUNT24 = 0
    WWAN_CMD_COUNT25 = 0
    WWAN_CMD_COUNT26 = 0
    WWAN_CMD_COUNT27 = 0
    WWAN_CMD_COUNT28 = 0
    WWAN_CMD_COUNT29 = 0
    WWAN_CMD_COUNT30 = 0
    WWAN_CMD_COUNT31= 0
    WWAN_CMD_COUNT32= 0
    WWAN_CMD_COUNT33= 0
    WWAN_CMD_COUNT34= 0
    WWAN_CMD_COUNT35= 0
    WWAN_CMD_COUNT36= 0
    WWAN_CMD_COUNT37= 0
    WWAN_CMD_COUNT38= 0
    WWAN_CMD_COUNT39= 0
    WWAN_CMD_COUNT40= 0
    WWAN_CMD_COUNT41= 0
    WWAN_CMD_COUNT42= 0
    WWAN_CMD_COUNT43= 0
    WWAN_CMD_COUNT44= 0
    WWAN_CMD_COUNT45= 0
    WWAN_CMD_COUNT46= 0
    WWAN_CMD_COUNT47= 0
    WWAN_CMD_COUNT48= 0

    for loop in range(10):
        mount_result = self._dut.CheckOutput(WWAN_RSSI_MOUNT_CMD, log=True)

        WWAN_CMD_COUNT17 += self.getwwanrssiL850(WWAN_CMD17, "WWAN_CMD17")
        WWAN_CMD_COUNT18 += self.getwwanrssiL850(WWAN_CMD18, "WWAN_CMD18")
        continue;

        WWAN_CMD_COUNT1 += self.getwwanrssiL850(WWAN_CMD1, "WWAN_CMD1")
        WWAN_CMD_COUNT2 += self.getwwanrssiL850(WWAN_CMD2, "WWAN_CMD2")
        WWAN_CMD_COUNT3 += self.getwwanrssiL850(WWAN_CMD3, "WWAN_CMD3")
        WWAN_CMD_COUNT4 += self.getwwanrssiL850(WWAN_CMD4, "WWAN_CMD4")
        WWAN_CMD_COUNT5 += self.getwwanrssiL850(WWAN_CMD5, "WWAN_CMD5")
        WWAN_CMD_COUNT6 += self.getwwanrssiL850(WWAN_CMD6, "WWAN_CMD6")
        WWAN_CMD_COUNT7 += self.getwwanrssiL850(WWAN_CMD7, "WWAN_CMD7")
        WWAN_CMD_COUNT8 += self.getwwanrssiL850(WWAN_CMD8, "WWAN_CMD8")
        WWAN_CMD_COUNT9 += self.getwwanrssiL850(WWAN_CMD9, "WWAN_CMD9")
        WWAN_CMD_COUNT10 += self.getwwanrssiL850(WWAN_CMD10, "WWAN_CMD10")
        WWAN_CMD_COUNT11 += self.getwwanrssiL850(WWAN_CMD11, "WWAN_CMD11")
        WWAN_CMD_COUNT12 += self.getwwanrssiL850(WWAN_CMD12, "WWAN_CMD12")
        WWAN_CMD_COUNT13 += self.getwwanrssiL850(WWAN_CMD13, "WWAN_CMD13")
        WWAN_CMD_COUNT14 += self.getwwanrssiL850(WWAN_CMD14, "WWAN_CMD14")
        WWAN_CMD_COUNT15 += self.getwwanrssiL850(WWAN_CMD15, "WWAN_CMD15")
        WWAN_CMD_COUNT16 += self.getwwanrssiL850(WWAN_CMD16, "WWAN_CMD16")
        WWAN_CMD_COUNT17 += self.getwwanrssiL850(WWAN_CMD17, "WWAN_CMD17")
        WWAN_CMD_COUNT18 += self.getwwanrssiL850(WWAN_CMD18, "WWAN_CMD18")
        WWAN_CMD_COUNT19 += self.getwwanrssiL850(WWAN_CMD19, "WWAN_CMD19")
        WWAN_CMD_COUNT20 += self.getwwanrssiL850(WWAN_CMD20, "WWAN_CMD20")
        WWAN_CMD_COUNT21 += self.getwwanrssiL850(WWAN_CMD21, "WWAN_CMD21")
        WWAN_CMD_COUNT22 += self.getwwanrssiL850(WWAN_CMD22, "WWAN_CMD22")
        WWAN_CMD_COUNT23 += self.getwwanrssiL850(WWAN_CMD23, "WWAN_CMD23")
        WWAN_CMD_COUNT24 += self.getwwanrssiL850(WWAN_CMD24, "WWAN_CMD24")
        WWAN_CMD_COUNT25 += self.getwwanrssiL850(WWAN_CMD25, "WWAN_CMD25")
        WWAN_CMD_COUNT26 += self.getwwanrssiL850(WWAN_CMD26, "WWAN_CMD26")
        WWAN_CMD_COUNT27 += self.getwwanrssiL850(WWAN_CMD27, "WWAN_CMD27")
        WWAN_CMD_COUNT28 += self.getwwanrssiL850(WWAN_CMD28, "WWAN_CMD28")
        WWAN_CMD_COUNT29 += self.getwwanrssiL850(WWAN_CMD29, "WWAN_CMD29")
        WWAN_CMD_COUNT30 += self.getwwanrssiL850(WWAN_CMD30, "WWAN_CMD30")
        WWAN_CMD_COUNT31 += self.getwwanrssiL850(WWAN_CMD31, "WWAN_CMD31")
        WWAN_CMD_COUNT32 += self.getwwanrssiL850(WWAN_CMD32, "WWAN_CMD32")
        WWAN_CMD_COUNT33 += self.getwwanrssiL850(WWAN_CMD33, "WWAN_CMD33")
        WWAN_CMD_COUNT34 += self.getwwanrssiL850(WWAN_CMD34, "WWAN_CMD34")
        WWAN_CMD_COUNT35 += self.getwwanrssiL850(WWAN_CMD35, "WWAN_CMD35")
        WWAN_CMD_COUNT36 += self.getwwanrssiL850(WWAN_CMD36, "WWAN_CMD36")
        WWAN_CMD_COUNT37 += self.getwwanrssiL850(WWAN_CMD37, "WWAN_CMD37")
        WWAN_CMD_COUNT38 += self.getwwanrssiL850(WWAN_CMD38, "WWAN_CMD38")
        WWAN_CMD_COUNT39 += self.getwwanrssiL850(WWAN_CMD39, "WWAN_CMD39")
        WWAN_CMD_COUNT40 += self.getwwanrssiL850(WWAN_CMD40, "WWAN_CMD40")
        WWAN_CMD_COUNT41 += self.getwwanrssiL850(WWAN_CMD41, "WWAN_CMD41")
        WWAN_CMD_COUNT42 += self.getwwanrssiL850(WWAN_CMD42, "WWAN_CMD42")
        WWAN_CMD_COUNT43 += self.getwwanrssiL850(WWAN_CMD43, "WWAN_CMD43")
        WWAN_CMD_COUNT44 += self.getwwanrssiL850(WWAN_CMD44, "WWAN_CMD44")
        WWAN_CMD_COUNT45 += self.getwwanrssiL850(WWAN_CMD45, "WWAN_CMD45")
        WWAN_CMD_COUNT46 += self.getwwanrssiL850(WWAN_CMD46, "WWAN_CMD46")
        WWAN_CMD_COUNT47 += self.getwwanrssiL850(WWAN_CMD47, "WWAN_CMD47")
        WWAN_CMD_COUNT48 += self.getwwanrssiL850(WWAN_CMD48, "WWAN_CMD48")
    
    session.console.info("1-10: %d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (WWAN_CMD_COUNT1, WWAN_CMD_COUNT2,WWAN_CMD_COUNT3,WWAN_CMD_COUNT4,WWAN_CMD_COUNT5,WWAN_CMD_COUNT6,WWAN_CMD_COUNT7,WWAN_CMD_COUNT8,WWAN_CMD_COUNT9,WWAN_CMD_COUNT10))
    session.console.info("11-20: %d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (WWAN_CMD_COUNT11, WWAN_CMD_COUNT12,WWAN_CMD_COUNT13,WWAN_CMD_COUNT14,WWAN_CMD_COUNT15,WWAN_CMD_COUNT16,WWAN_CMD_COUNT17,WWAN_CMD_COUNT18,WWAN_CMD_COUNT19,WWAN_CMD_COUNT20))
    session.console.info("21-30: %d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (WWAN_CMD_COUNT21, WWAN_CMD_COUNT22,WWAN_CMD_COUNT23,WWAN_CMD_COUNT24,WWAN_CMD_COUNT25,WWAN_CMD_COUNT26,WWAN_CMD_COUNT27,WWAN_CMD_COUNT28,WWAN_CMD_COUNT29,WWAN_CMD_COUNT30))
    session.console.info("31-40: %d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (WWAN_CMD_COUNT31, WWAN_CMD_COUNT32,WWAN_CMD_COUNT33,WWAN_CMD_COUNT34,WWAN_CMD_COUNT35,WWAN_CMD_COUNT36,WWAN_CMD_COUNT37,WWAN_CMD_COUNT38,WWAN_CMD_COUNT39,WWAN_CMD_COUNT40))
    session.console.info("41-48: %d,%d,%d,%d,%d,%d,%d,%d" % (WWAN_CMD_COUNT41, WWAN_CMD_COUNT42,WWAN_CMD_COUNT43,WWAN_CMD_COUNT44,WWAN_CMD_COUNT45,WWAN_CMD_COUNT46,WWAN_CMD_COUNT47,WWAN_CMD_COUNT48))
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
