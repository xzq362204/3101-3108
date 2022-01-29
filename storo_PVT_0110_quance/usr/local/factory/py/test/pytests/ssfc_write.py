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

TRANSFER_VCM = {
    "Unprovisioned": 0,
    "BU64297GWZ": 1
}
TRANSFER_UFC = {
    "Unprovisioned": 0
}
TRANSFER_WFC = {
    "Unprovisioned": 0,
    "OV8856": 1
}
TRANSFER_LidSensor = {
    "Unprovisioned": 0,
    "BMA255": 1,
    "LIS2DWL": 3
}
TRANSFER_BaseSensor = {
    "BMI160": 1,
    "ICM-42607": 4
}

SSFC_Lists = ["0x0","0x1","0x4","0x4200000c","0x42000009","0x42000019","0x4200001c","0x4200040c","0x42000409","0x42000419","0x4200041c","0x400"]

class InfoCheckTest(test_case.TestCase):

  ARGS = [
      Arg('autostart', bool, 'Auto start this test.',
          default=True),
      Arg('ssfc_check', bool, 'Check SSFC data.',
          default=True),
      Arg('timeout', int,
          'Timeout of the test.',
          default=200)
      ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self.ui.SetTitle(_('SSFC confirm and check'))

  # cros-camera-tool modules list
  def ReadVCM(self):
      bRet, wfc_value = self.ReadWFC()
      if not bRet:
          return bRet, 0
      else:
          return bRet, wfc_value<<5

  def ReadUFC(self):
      return True, 0

  #cros-camera-tool modules list
  def ReadWFC(self):
      check_ssfc_wfc_cmd = "cros-camera-tool modules list"
      try:
          ssfc_wfc_result = self._dut.CheckOutput(check_ssfc_wfc_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (ssfc_wfc_result, e))
          return True,0

      session.console.info("cmd :%s, return :%s" % (check_ssfc_wfc_cmd, ssfc_wfc_result))
      if ssfc_wfc_result is None or "No cameras detected" in ssfc_wfc_result:
          return True, 0
      else:
          #match = re.search(r'"name": "[0-9a-zA-Z]{6}', str(ssfc_wfc_result))
          result_lines = ssfc_wfc_result.splitlines()
          result_line = result_lines[1].strip()
          wfc_chip = result_line.split(' ')[0].strip().upper()
          wfc_value = TRANSFER_WFC.get(wfc_chip, 0)#"name": "ov8856
          if wfc_value is None:
              return True, 0
          else:
              return True, wfc_value<<25
  #lid sensor
  #ectool i2cxfer 2 0x19 1 0x00  ret 0xfa => BMA255
  #ectool i2cxfer 2 0x19 1 0x0f  ret 0x44 => Lis2dwl
  def ReadLidSensor(self):
      self.ui.SetState(_('Check ssfc lid data...'))

      #BMA255
      check_lid_bma255_cmd = "ectool i2cxfer 2 0x19 1 0x00"
      try:
          lid_bma255_result = self._dut.CheckOutput(check_lid_bma255_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (check_lid_bma255_cmd, e))
          #return True,0
      else:
          if "0xfa" in lid_bma255_result:
              lid_value = TRANSFER_LidSensor.get("BMA255", 0)
              return True, lid_value<<3

      #Lis2dwl
      check_lid_Lis2dwl_cmd = "ectool i2cxfer 2 0x19 1 0x0f"
      try:
          lid_Lis2dwl_result = self._dut.CheckOutput(check_lid_Lis2dwl_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (check_lid_Lis2dwl_cmd, e))
          #return True,0
      else:
          if "0x44" in lid_Lis2dwl_result:
              lid_value = TRANSFER_LidSensor.get("LIS2DWL", 0)
              return True, lid_value<<3

      return True, 0

  #base sensor
  #ectool i2cxfer 2 0x68 1 0x00  ret 0xd1  => BMI160
  #ectool i2cxfer 2 0x68 1 0x75  ret 0x60 =>  ICM42607
  def ReadBaseSensor(self):
      self.ui.SetState(_('Check ssfc base data...'))

      #BMI160
      check_base_bmi160_cmd = "ectool i2cxfer 2 0x68 1 0x00"
      try:
          base_bmi160_result = self._dut.CheckOutput(check_base_bmi160_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (check_base_bmi160_cmd, e))
          #return True,0
      else:
          if "0xd1" in base_bmi160_result:
              base_value = TRANSFER_BaseSensor.get("BMI160", 0)
              return True, base_value

      #ICM42607
      check_base_icm42607_cmd = "ectool i2cxfer 2 0x68 1 0x75"
      try:
          base_icm42607_result = self._dut.CheckOutput(check_base_icm42607_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (check_base_icm42607_cmd, e))
          #return True,0
      else:
          if "0x60" in base_icm42607_result:
              base_value = TRANSFER_BaseSensor.get("ICM-42607", 0)
              return True, base_value

      return True,0

  def ReadSSFC(self):
      check_ssfc_cmd = "ectool cbi get 8"
      try:
          ssfcresult = self._dut.CheckOutput(check_ssfc_cmd, log=True)
      except Exception as e:
          session.console.info('error in executing %s (%s)' % (check_ssfc_cmd, e))
          return False,""
      
      session.console.info("cmd :%s, return :%s" % (check_ssfc_cmd, ssfcresult))
      if ssfcresult is None or "Error code" in ssfcresult:
          return False,""
      else:
          tmp_str = ssfcresult.split("(")[1]
          ssfc_value = tmp_str.split(")")[0].strip()
          return True, ssfc_value

  def CalSSFC(self):

      bRet, vcm_value = self.ReadVCM()
      if not bRet:
          return False,""

      bRet, ufc_value = self.ReadUFC()
      if not bRet:
          return False,""

      bRet, wfc_value = self.ReadWFC()
      if not bRet:
          return False,""

      bRet, lid_value = self.ReadLidSensor()
      if not bRet:
          return False,""

      bRet, base_value = self.ReadBaseSensor()
      if not bRet:
          return False,""

      ssfc_value = vcm_value | ufc_value | wfc_value | lid_value | base_value

      session.console.info("vcm_value :%s" % hex(vcm_value))
      session.console.info("ufc_value :%s" % hex(ufc_value))
      session.console.info("wfc_value :%s" % hex(wfc_value))
      session.console.info("lid_value :%s" % hex(lid_value))
      session.console.info("base_value :%s" % hex(base_value))
      session.console.info("ssfc_value :%s" % hex(ssfc_value))
      return True,hex(ssfc_value)

  def InfoWrite(self):
    self.ui.SetState(_('write ssfc data...'))
    bRet, cal_ssfc = self.CalSSFC()
    if not bRet:
      session.console.info("cal ssfc data return failed")
      self.FailTask("cal ssfc data return Fail")
      return False
    else:
      if cal_ssfc not in SSFC_Lists:
        session.console.info("cal ssfc data:%s not in SSFC_Lists %s" % (cal_ssfc,SSFC_Lists))
        self.FailTask("cal ssfc data:%s not in SSFC_Lists %s" % (cal_ssfc,SSFC_Lists))
        return False

      session.console.info("cal ssfc data:%s, try write to cbi" % cal_ssfc)
      write_ssfc_cmd = "ectool cbi set 8 " + cal_ssfc + " 4 0"
      ssfcwriteresult = self._dut.CheckOutput(write_ssfc_cmd, log=True)
      session.console.info("write cbi ssfc return :%s" % ssfcwriteresult)
      if ssfcwriteresult is None or "Error code" in ssfcwriteresult:
        session.console.info("write ssfc fail.")
        return False
      else:
        session.console.info("write ssfc OK.")
    return True

  def InfoCheck(self):
      if self.args.ssfc_check:
          self.ui.SetState(_('read ssfc data...'))

          bRet, cbi_ssfc = self.ReadSSFC()
          if not bRet:
              session.console.info("Get cbi ssfc return Fail")
              return False
          else:
              self.ui.SetState(_('cal ssfc data...'))

              session.console.info("Get cbi ssfc return:%s "%cbi_ssfc)

              bRet, cal_ssfc = self.CalSSFC()
              if not bRet:
                  session.console.info("cal ssfc data return Fail")
                  self.FailTask("cal ssfc data return Fail")
                  return False
              else:
                  session.console.info("cal ssfc data:%s" % cal_ssfc)
              if cal_ssfc not in SSFC_Lists:
                  session.console.info("cal ssfc data:%s not in SSFC_Lists %s" % (cal_ssfc,SSFC_Lists))
                  self.FailTask("cal ssfc data:%s not in SSFC_Lists %s" % (cal_ssfc,SSFC_Lists))
                  return False

              if cbi_ssfc != cal_ssfc:
                  session.console.info("cbi ssfc data :%s is not the same "
                                       "with cal ssfc data :%s." % (cbi_ssfc, cal_ssfc))
                  session.console.info("Check ssfc data failed.")
                  return False
              else:
                  session.console.info("Check ssfc OK.")
      return True

  def runTest(self):
    self.ui.SetInstruction(
        _('ssfc Write Test'))
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

    self.ui.SetState(_('ssfc info check...'))
    result = self.InfoCheck()
    if result is False:
        session.console.info("check ssfc data failed, try write")
        writeresult = self.InfoWrite()
        if writeresult is False:
          self.FailTask("write ssfc data failed")
        else:
            result = self.InfoCheck()
            if result is False:
                self.FailTask("write ssfc data failed")