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
import binascii

#import factory_common  # pylint: disable=unused-import
from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.test import test_ui
from cros.factory.test import session
from cros.factory.test import device_data

_KEY_COMPONENT_SKU = device_data.JoinKeys(device_data.KEY_COMPONENT, 'skuid')
_KEY_COMPONENT_FWCONFIG = device_data.JoinKeys(device_data.KEY_COMPONENT, 'fwconfig')
_KEY_COMPONENT_DRAMPARTNUMBER = device_data.JoinKeys(device_data.KEY_COMPONENT, 'dram.part_num')
_KEY_COMPONENT_SSFC = device_data.JoinKeys(device_data.KEY_COMPONENT, 'ssfc')


class InfoCheckTest(test_case.TestCase):

  ARGS = [
      Arg('autostart', bool, 'Auto start this test.',
          default=False),
      Arg('smt_skuid_boardid_check', bool,
          'Check skuid and boardid data.',
          default=False),
      Arg('skuid_check', bool,
          'Check skuid data.',
          default=False),
      Arg('dram_partnumber_check', bool,
          'Check dram part number data.',
          default=False),
      Arg('fw_config_check', bool,
          'Check fw_config data.',
          default=False),
      Arg('ssfc_check', bool, 'Check SSFC data.',
          default=False),
      Arg('timeout', int,
          'Timeout of the test.',
          default=200)
      ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('DUT data confirm and check'))

  def InfoCheck(self, datatype):
      result = False


  def InfoCheck(self):
      totalresult = True
      if self.args.smt_skuid_boardid_check:
          self.ui.SetState(_('Check SMT skuid and boardid data...'))
          check_skuid_cmd = "ectool cbi get 2"
          skuidresult = self._dut.CheckOutput(check_skuid_cmd, log=True)
          session.console.info("Check cbi skuid return :%s." % skuidresult)
          if skuidresult is None or "Error code" in skuidresult:
              return False
          tmp_str = skuidresult.split("(")[0]
          skuid_str1 = tmp_str.split(":")[1]
          skuid_str = skuid_str1.strip()
          session.console.info("Get cbi skuid :%s."% skuid_str)
          if skuid_str != '1703936':
              session.console.info("Check cbi skuid failed.")
              totalresult = False
          else:
              session.console.info("Check cbi skuid OK.")
          check_boardid_cmd = "ectool cbi get 0"
          boardidresult = self._dut.CheckOutput(check_boardid_cmd, log=True)
          session.console.info("Check cbi boardid return :%s." % boardidresult)
          if boardidresult is None or "Error code" in boardidresult:
              return False
          tmp_str = boardidresult.split("(")[0]
          boardid_str = tmp_str.split(":")[1].strip()
          session.console.info("Get cbi boardid :%s." % boardid_str)
          if boardid_str != '1':
              session.console.info("Check cbi boardid failed.")
              totalresult = False
          else:
              session.console.info("Check cbi boardid OK.")
          return totalresult
      if self.args.skuid_check:
          self.ui.SetState(_('Check skuid data...'))
          check_skuid_cmd = "ectool cbi get 2"
          skuidresult = self._dut.CheckOutput(check_skuid_cmd, log=True)
          session.console.info("Check cbi boardid return :%s" % skuidresult)
          if skuidresult is None or "Error code" in skuidresult:
              totalresult =  False
          else:
              tmp_str = skuidresult.split("(")[0]
              skuid_str_int = tmp_str.split(":")[1].strip()
              session.console.info("Get cbi skuid data:%s" % skuid_str_int)
              tmp_str = skuidresult.split("(")[1]
              skuid_str_hex = tmp_str.split(")")[0].strip()
              # check_skuid_cmd = "factory device-data component.skuid"
              value = device_data.GetDeviceData(_KEY_COMPONENT_SKU)
              strvalue = str(value)
              if strvalue is None:
                  session.console.info("Component's skuid data is None.")
                  totalresult = False
              else:
                  session.console.info("Get Component's skuid data:%s" % strvalue)
              if strvalue != skuid_str_int and strvalue != skuid_str_hex:
                  session.console.info("Component's Skuid data :%s is not the same "
                                       "with cbi data :%s or %s." % (strvalue, skuid_str_int, skuid_str_hex))
                  totalresult = False
              else:
                  session.console.info("Check cbi Skuid OK.")
      if self.args.dram_partnumber_check:
          self.ui.SetState(_('Check dram part number data...'))
          check_dram_partnumber_cmd = "ectool cbi get 3"
          dram_partnumbertmp = self._dut.CheckOutput(check_dram_partnumber_cmd, log=True)
          dram_partnumberresult = dram_partnumbertmp.split("\n")[0]
          session.console.info("Check cbi dram part number return :%s" % dram_partnumberresult)
          if dram_partnumberresult is None or "Error code" in dram_partnumberresult:
              totalresult = False
          #need not slpit
          value = device_data.GetDeviceData(_KEY_COMPONENT_DRAMPARTNUMBER)
          strvalue = str(value)
          session.console.info("Get component's dram part number:%s" % strvalue)
          if strvalue is None:
              totalresult = False
          if strvalue != dram_partnumberresult:
              session.console.info("Check dram part number failed.")
              totalresult = False
          else:
              session.console.info("Check dram part number OK.")
      if self.args.fw_config_check:
          self.ui.SetState(_('Check FW Config data...'))
          check_fwconfig_cmd = "ectool cbi get 6"
          fwconfigresult = self._dut.CheckOutput(check_fwconfig_cmd, log=True)
          session.console.info("Check cbi fw config return :%s" % fwconfigresult)
          if fwconfigresult is None or "Error code" in fwconfigresult:
              totalresult =  False
          else:
              tmp_str = fwconfigresult.split("(")[0]
              fwconfig_str_int = tmp_str.split(":")[1].strip()
              tmp_str = fwconfigresult.split("(")[1]
              fwconfig_str_hex = tmp_str.split(")")[0].strip()
              value = device_data.GetDeviceData(_KEY_COMPONENT_FWCONFIG)
              strvalue = str(value)
              if strvalue is None:
                  session.console.info("Component's FW Config data is None.")
                  totalresult = False
              else:
                  session.console.info("Get Component's fw config data:%s" % strvalue)
              if strvalue != fwconfig_str_int and strvalue != fwconfig_str_hex:
                  session.console.info("Component's FW Config data :%s is not the same "
                                       "with cbi data :%s or %s." % (strvalue, fwconfig_str_int, fwconfig_str_hex))
                  session.console.info("Check FW Config failed.")
                  totalresult = False
              else:
                  session.console.info("Check FW Config OK.")
      if self.args.ssfc_check:
          self.ui.SetState(_('Check SSFC data...'))
          check_ssfc_cmd = "ectool cbi get 8"
          ssfcresult = self._dut.CheckOutput(check_ssfc_cmd, log=True)
          session.console.info("Check cbi ssfc return :%s" % ssfcresult)
          if ssfcresult is None or "Error code" in ssfcresult:
              totalresult =  False
          else:
              tmp_str = ssfcresult.split("(")[0]
              ssfc_str_int = tmp_str.split(":")[1].strip()
              tmp_str = ssfcresult.split("(")[1]
              ssfc_str_hex = tmp_str.split(")")[0].strip()
              value = device_data.GetDeviceData(_KEY_COMPONENT_SSFC)
              strvalue = str(value)
              if strvalue is None:
                  session.console.info("Component's SSFC data is None.")
                  totalresult = False
              else:
                  session.console.info("Get Component's ssfc data:%s" % strvalue)
              if strvalue != ssfc_str_int and strvalue != ssfc_str_hex:
                  session.console.info("Component's SSFC data :%s is not the same "
                                       "with cbi data :%s or %s." % (strvalue, ssfc_str_int, ssfc_str_hex))
                  totalresult = False
                  session.console.info("Check SSFC data failed.")
              else:
                  session.console.info("Check SSFC OK.")
      return totalresult

  def runTest(self):
    self.ui.SetInstruction(
        _('Data Info Check Test'))
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
    self.ui.SetState(_('Data Info Check Test...'))

    result = self.InfoCheck()
    if result is False:
        self.FailTask(
            "Check cbi data failed")